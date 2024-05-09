from eth_abi import decode
from fastapi import Depends

from app.abi import LAUNCHPAD_PLACE_TOKENS_ABI
from app.base import logger
from app.common import Command, CommandResult
from app.crud import LaunchpadProjectCrud
from app.dependencies import get_launchpad_projects_crud
from app.env import settings
from app.services.total_raised.multicall import get_multicall_token_placed
from app.services.web3_nodes import web3_node
from app.types import PlacedToken, ProjectIdWithRaised


class RecalculateProjectsTotalRaised(Command):
    async def command(
        self,
        crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
    ) -> CommandResult:
        logger.info("Recalculate projects total raised")
        if not settings.launchpad_contract_address:
            logger.error("Launchpad contract address is not set, can't calculate total raised")
            return CommandResult(success=False, need_retry=False)

        recalculating_data = await crud.get_data_for_total_raised_recalculating()
        web3 = await web3_node.get_web3("blast")

        contract_project_id_by_project, launchpad_goal_by_project = {}, {}
        for x in recalculating_data:
            if x.contract_project_id is None:
                logger.error(f"Contract project id is not set for default project {x.id}")
                continue
            contract_project_id_by_project[x.id] = x.contract_project_id
            launchpad_goal_by_project[x.id] = float(x.raise_goal_on_launchpad)

        output_data = await get_multicall_token_placed(
            web3=web3, contract_project_id_by_project_id=contract_project_id_by_project
        )
        usd_volume_left_by_project_id = {}
        for (success, data), project_id in zip(output_data, contract_project_id_by_project.keys()):
            logger.info(f"Recalculating project {project_id}, {success=}")
            if not data:
                # no data for contract_project_id
                continue
            info = PlacedToken(
                *decode(types=[x["type"] for x in LAUNCHPAD_PLACE_TOKENS_ABI["outputs"]], data=data)
            )
            token_price = info.price / 10e18
            volume = info.volume / 10e18  # tokens left
            if volume < 1:
                # no tokens left
                continue
            usd_volume_left_by_project_id[project_id] = volume * token_price
        res = [
            ProjectIdWithRaised(
                project_id=project_id,
                raised=round(launchpad_goal_by_project[project_id] - volume_left, 4),
            )
            for project_id, volume_left in usd_volume_left_by_project_id.items()
        ]
        await crud.update_raised_value(res)
        logger.info("Recalculating projects total_raised is done")

        return CommandResult(success=True, need_retry=False)
