import time

from fastapi import Depends

from app.abi import LAUNCHPAD_CONTRACT_ADDRESS_ABI
from app.base import logger
from app.common import Command, CommandResult
from app.crud.launchpad_events import LaunchpadContractEventsCrud
from app.dependencies import get_launchpad_contract_events_crud
from app.env import settings
from app.models import LaunchpadContractEventType
from app.schema import CreateLaunchpadEvent
from app.services.analytics.redis_cli import reg_users_and_allocation_redis
from app.services.web3_nodes import web3_node


class ProcessLaunchpadContractEvents(Command):
    async def command(
        self,
        crud: LaunchpadContractEventsCrud = Depends(get_launchpad_contract_events_crud),
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
        n_user_registered, n_allocations = 0, 0
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
                await crud.session.commit()
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            return CommandResult(success=False, need_retry=True)

        return CommandResult(success=True, need_retry=False)
