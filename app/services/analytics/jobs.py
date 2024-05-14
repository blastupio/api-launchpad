import time
from base64 import b64decode
from collections import defaultdict

import pandas as pd
import pygsheets
from fastapi import Depends
from pygsheets import PyGsheetsException
from web3 import Web3

from app.abi import LAUNCHPAD_CONTRACT_ADDRESS_ABI
from app.base import logger, engine
from app.common import Command, CommandResult
from app.crud import LaunchpadProjectCrud
from app.crud.launchpad_events import LaunchpadContractEventsCrud
from app.dependencies import get_launchpad_contract_events_crud, get_launchpad_projects_crud
from app.env import settings
from app.models import LaunchpadContractEventType
from app.schema import CreateLaunchpadEvent
from app.services.analytics.redis_cli import reg_users_and_allocation_redis
from app.services.web3_nodes import web3_node


class ProcessLaunchpadContractEvents(Command):
    async def get_all_events_and_save_to_gs(
        self, crud: LaunchpadContractEventsCrud, project_crud: LaunchpadProjectCrud
    ):
        if not settings.google_service_account_json:
            logger.error("Process launchpad events: google_service_account_json not set")
            return
        data = defaultdict(list)
        async with engine.begin() as conn:
            events = await crud.get_all_events(conn)
            info_by_contract_project_id = (
                await project_crud.get_project_info_by_contract_project_id(conn)
            )
            for event in events:
                contr_project_id = event.contract_project_id
                tier = event.extra.get("tier")
                project_name = info_by_contract_project_id.get(contr_project_id, {}).get("name", "")
                tokens_amount = round(Web3.from_wei(int(event.extra.get("amount", 0)), "ether"), 6)
                token_price = info_by_contract_project_id.get(contr_project_id, {}).get("price", 0)
                usd_amount = round(tokens_amount * token_price, 2)
                if (
                    event_type := event.event_type.value
                ) == LaunchpadContractEventType.USER_REGISTERED.value:
                    tokens_amount, usd_amount, token_price = "", "", ""

                data["#"].append(event.id)
                data["event_type"].append(event_type)
                data["project_name"].append(project_name)
                data["contract_project_id"].append(contr_project_id)
                data["tokens_amount"].append(tokens_amount)
                data["usd_token_price"].append(token_price)
                data["usd_amount"].append(usd_amount)
                data["tier"].append(tier + 1 if tier is not None else "")
                data["user_address"].append(event.user_address)
                data["token_address"].append(event.token_address)
                data["txn_hash"].append(event.txn_hash)
                data["block_number"].append(event.block_number)
                data["created_at"].append(event.created_at)
        dataframe = pd.DataFrame(data)

        gc = pygsheets.authorize(
            service_account_json=b64decode(settings.google_service_account_json),
        )
        try:
            sh = gc.open(settings.google_launchpad_events_report_filename)
            sh[0].set_dataframe(dataframe, (1, 1))
            filename = settings.google_launchpad_events_report_filename
            logger.info(f"Saved launchpad events report to {filename}")
        except PyGsheetsException as exc:
            logger.error(f"Process launchpad events: gs exception: {str(exc)}")

    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
        project_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
    ) -> CommandResult:
        if not settings.launchpad_contract_address:
            logger.error("Process launchpad events: launchpad contract address is not set")
            return CommandResult(success=False, need_retry=False)

        web3 = await web3_node.get_web3(network="blast")
        chain_id = await web3.eth.chain_id
        current_block = await web3.eth.block_number
        log = f"Process launchpad events: {settings.launchpad_contract_address=}, {chain_id=}, {current_block=}"  # noqa
        logger.info(log)
        if (
            last_checked_block := await reg_users_and_allocation_redis.get_last_checked_block(
                chain_id
            )
        ) is None:
            last_checked_block = current_block - 100_000

        if last_checked_block >= current_block:
            return CommandResult(success=True, need_retry=False)

        contract = web3.eth.contract(
            address=web3.to_checksum_address(settings.launchpad_contract_address),
            abi=LAUNCHPAD_CONTRACT_ADDRESS_ABI,
        )
        n_user_registered, n_allocations, new_events = 0, 0, 0
        try:
            while True:
                from_block = last_checked_block + 1
                # 3000 is limit, can't set larger than that
                to_block = min(current_block, from_block + 3000)
                logger.info(f"Monitoring launchpad events from {from_block} to {to_block}")

                if from_block > to_block:
                    logger.info(f"No launchpad events from {from_block} to {to_block}")
                    break

                user_registered_events = await contract.events.UserRegistered().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_user_registered += len(user_registered_events)
                new_events += n_user_registered
                for event in user_registered_events:
                    await crud.add_event(
                        params=CreateLaunchpadEvent(
                            event_type=LaunchpadContractEventType.USER_REGISTERED,
                            token_address=event.args["token"],
                            user_address=event.args["user"],
                            txn_hash=event.transactionHash.hex(),
                            contract_project_id=event.args["id"],
                            extra={"tier": event.args["tier"]},
                            block_number=event.blockNumber,
                        )
                    )

                tokens_allocations_events = await contract.events.TokensBought().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_allocations += len(tokens_allocations_events)
                new_events += n_allocations
                for event in tokens_allocations_events:
                    await crud.add_event(
                        params=CreateLaunchpadEvent(
                            event_type=LaunchpadContractEventType.TOKENS_BOUGHT,
                            token_address=event.args["token"],
                            user_address=event.args["buyer"],
                            txn_hash=event.transactionHash.hex(),
                            contract_project_id=event.args["id"],
                            extra={"amount": str(event.args["amount"])},
                            block_number=event.blockNumber,
                        )
                    )

                last_checked_block = to_block
                await reg_users_and_allocation_redis.set_last_checked_block(chain_id, to_block)
                time.sleep(0.5)

            if n_allocations or n_user_registered:
                # one needs to commit only ones after while cycle
                # don't commit inside add_event
                logger.info(
                    f"Process launchpad events: saving {n_allocations=}, {n_user_registered=}"
                )
                await crud.session.commit()
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            return CommandResult(success=False, need_retry=True)
        if new_events:
            # todo: append only new events, not all events
            await self.get_all_events_and_save_to_gs(crud, project_crud)

        return CommandResult(success=True, need_retry=False)
