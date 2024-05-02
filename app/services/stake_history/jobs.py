import time

from fastapi import Depends
from web3 import AsyncWeb3, AsyncHTTPProvider

from app.base import logger
from app.common import Command, CommandResult
from app.crud.history_staking import HistoryStakingCrud
from app.dependencies import get_staking_history_crud
from app.env import settings
from app.models import HistoryStakeType
from app.schema import CreateHistoryStake
from app.services.stake_history.abi import staking_abi
from app.services.stake_history.redis_cli import stake_history_redis


class ProcessHistoryStakingEvent(Command):
    async def command(
        self,
        crud: HistoryStakingCrud = Depends(get_staking_history_crud),
    ) -> CommandResult:
        web3 = AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_blast))
        chain_id = await web3.eth.chain_id
        current_block = await web3.eth.block_number
        if (
            last_checked_block := await stake_history_redis.get_last_checked_block(chain_id)
        ) is None:
            last_checked_block = current_block - 100_000

        if last_checked_block >= current_block:
            return CommandResult(success=True, need_retry=False)

        staking_contract = web3.eth.contract(
            address=web3.to_checksum_address(settings.yield_staking_contract_addr),
            abi=staking_abi,
        )
        while True:
            from_block = last_checked_block + 1
            # 2500 is limit, can't set larger than that
            to_block = min(current_block, from_block + 3000)
            logger.info(f"Monitoring from block {from_block} to block {to_block}")

            if from_block > to_block:
                logger.info(f"No events from block {from_block} to block {to_block}")
                break

            try:
                events = await staking_contract.events.Staked().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                for event in events:
                    await crud.add_history(
                        params=CreateHistoryStake(
                            type=HistoryStakeType.STAKE,
                            token_address=event.args["stakingToken"],
                            amount=str(event.args["amount"]),
                            txn_hash=event.transactionHash.hex(),
                            block_number=event.blockNumber,
                            chain_id=str(chain_id),
                            user_address=event.args["user"],
                        )
                    )

                events = await staking_contract.events.Withdrawn().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                for event in events:
                    await crud.add_history(
                        params=CreateHistoryStake(
                            type=HistoryStakeType.CLAIM_REWARDS,
                            token_address=event.args["stakingToken"],
                            amount=str(event.args["amount"]),
                            txn_hash=event.transactionHash.hex(),
                            block_number=event.blockNumber,
                            chain_id=str(chain_id),
                            user_address=event.args["user"],
                        )
                    )

                last_checked_block = to_block
                await stake_history_redis.set_last_checked_block(chain_id, to_block)
            except Exception as e:
                logger.error(f"Error processing events: {e}")
                return CommandResult(success=False, need_retry=True)
            time.sleep(0.5)

        return CommandResult(success=True, need_retry=False)
