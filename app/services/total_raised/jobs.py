import asyncio

from eth_abi import decode
from fastapi import Depends
from web3 import Web3

from app.abi import LAUNCHPAD_PLACE_TOKENS_ABI
from app.base import logger
from app.common import Command, CommandResult
from app.crud import LaunchpadProjectCrud
from app.dependencies import get_launchpad_projects_crud
from app.env import settings
from app.models import ProjectType
from app.router.v1.proxy import fetch_data
from app.services.total_raised.multicall import get_multicall_token_placed
from app.services.web3_nodes import web3_node
from app.types import PlacedToken, ProjectIdWithRaised


class RecalculateProjectsTotalRaised(Command):
    async def _get_total_raised_for_private_project(
        self, project_id: str, proxy_url: str
    ) -> float | None:
        _url = f"{proxy_url}/" if not proxy_url.endswith("/") else proxy_url
        url = f"{_url}crypto/total-balance"
        for i in range(5):
            try:
                json = await fetch_data(url, timeout=5)
            except Exception as e:
                logger.error(f"Can't get total raised for {project_id=} and {url=}:\n{e}")
                continue
            if not json["ok"]:
                await asyncio.sleep(i * 0.5)
                continue
            total_raised_usd = json.get("data", {}).get("usd")
            if total_raised_usd is None:
                logger.error(f"Can't get total raised for {project_id=} and {url=}:{json}")
                continue
            return float(total_raised_usd)
        logger.error(f"Can't get total raised for {project_id=} and {url=}")
        return None

    async def _get_for_default_projects(
        self,
        contract_project_id_by_project: dict[str, int],
        launchpad_goal_by_project: dict[str, float],
    ) -> list[ProjectIdWithRaised]:
        web3 = await web3_node.get_web3("blast")
        output_data = await get_multicall_token_placed(
            web3=web3, contract_project_id_by_project_id=contract_project_id_by_project
        )
        usd_volume_left_by_project_id = {}
        for (success, data), project_id in zip(output_data, contract_project_id_by_project.keys()):
            logger.info(f"Recalculating project {project_id}, {success=}")
            if not data:
                continue
            info = PlacedToken(
                *decode(types=[x["type"] for x in LAUNCHPAD_PLACE_TOKENS_ABI["outputs"]], data=data)
            )
            token_price = Web3.from_wei(info.price, "ether")
            volume = Web3.from_wei(info.volume, "ether")  # tokens left
            if volume < 1:
                # no tokens left => 0 usd_volume_left
                usd_volume_left_by_project_id[project_id] = 0
            else:
                usd_volume_left_by_project_id[project_id] = float(volume * token_price)
        res = [
            ProjectIdWithRaised(
                project_id=project_id,
                raised=round(launchpad_goal_by_project[project_id] - volume_left, 4),
            )
            for project_id, volume_left in usd_volume_left_by_project_id.items()
        ]
        return res

    async def _get_for_private_projects(
        self,
        proxy_link_by_project: dict[str, str],
    ) -> list[ProjectIdWithRaised]:
        tasks = [
            self._get_total_raised_for_private_project(project_id, proxy_link)
            for project_id, proxy_link in proxy_link_by_project.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        res = []
        for total_raised, project_id in zip(results, proxy_link_by_project.keys()):
            if isinstance(total_raised, float):
                res.append(
                    ProjectIdWithRaised(
                        project_id=project_id,
                        raised=total_raised,
                    )
                )
        return res

    async def command(
        self,
        crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
    ) -> CommandResult:
        logger.info("Recalculate projects total raised")
        if not settings.launchpad_contract_address:
            logger.error("Launchpad contract address is not set, can't calculate total raised")
            return CommandResult(success=False, need_retry=False)

        recalculating_data = await crud.get_data_for_total_raised_recalculating()

        contract_project_id_by_project, launchpad_goal_by_project, proxy_link_by_project = (
            {},
            {},
            {},
        )
        for x in recalculating_data:
            if x.project_type == ProjectType.PRIVATE_PRESALE:
                if not x.base_url:
                    logger.warning(f"Base url is not set for private project {x.id}")
                proxy_link_by_project[x.id] = x.base_url
            elif x.project_type == ProjectType.DEFAULT:
                if x.contract_project_id is None:
                    logger.warning(f"Contract project id is not set for default project {x.id}")
                    continue
                contract_project_id_by_project[x.id] = x.contract_project_id
                launchpad_goal_by_project[x.id] = float(x.raise_goal_on_launchpad)

        default_projects = await self._get_for_default_projects(
            contract_project_id_by_project, launchpad_goal_by_project
        )
        private_projects = await self._get_for_private_projects(proxy_link_by_project)
        await crud.update_raised_value(data=default_projects + private_projects)
        logger.info("Recalculating projects total_raised is done")

        return CommandResult(success=True, need_retry=False)
