import time
import traceback

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
    async def _save_stake_events(self, crud: HistoryStakingCrud, chain_id: int, events) -> None:
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

    async def _save_claim_rewards_events(
        self, crud: HistoryStakingCrud, chain_id: int, events
    ) -> None:
        for event in events:
            await crud.add_history(
                params=CreateHistoryStake(
                    type=HistoryStakeType.CLAIM_REWARDS,
                    token_address=event.args["stakingToken"],
                    amount=str(event.args["amountInStakingToken"]),
                    txn_hash=event.transactionHash.hex(),
                    block_number=event.blockNumber,
                    chain_id=str(chain_id),
                    user_address=event.args["user"],
                )
            )

    async def _save_unstake_events(self, crud: HistoryStakingCrud, chain_id: int, events) -> None:
        for event in events:
            await crud.add_history(
                params=CreateHistoryStake(
                    type=HistoryStakeType.UNSTAKE,
                    token_address=event.args["stakingToken"],
                    amount=str(event.args["amount"]),
                    user_address=event.args["user"],
                    txn_hash=event.transactionHash.hex(),
                    block_number=event.blockNumber,
                    chain_id=str(chain_id),
                )
            )

    async def command(
        self,
        crud: HistoryStakingCrud = Depends(get_staking_history_crud),
    ) -> CommandResult:
        if not settings.yield_staking_contract_addr:
            logger.error("Staking events: yield staking contract address is not set")
            return CommandResult(success=False, need_retry=False)

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
        n_stakes, n_claim_rewards, n_unstake = 0, 0, 0
        try:
            while True:
                from_block = last_checked_block + 1
                # 3000 is limit, can't set larger than that
                to_block = min(current_block, from_block + 3000)
                logger.info(f"Staking events: monitoring {from_block=} {to_block=}")

                if from_block > to_block:
                    logger.info(f"Staking events: No events {from_block=} {to_block=}")
                    break

                stake_events = await staking_contract.events.Staked().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_stakes += len(stake_events)
                await self._save_stake_events(crud, chain_id, stake_events)

                claim_reward_events = await staking_contract.events.RewardClaimed().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_claim_rewards += len(claim_reward_events)
                await self._save_claim_rewards_events(crud, chain_id, claim_reward_events)

                unstake_events = await staking_contract.events.Withdrawn().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_unstake += len(unstake_events)
                await self._save_unstake_events(crud, chain_id, unstake_events)

                last_checked_block = to_block
                await stake_history_redis.set_last_checked_block(chain_id, to_block)
                time.sleep(0.5)

            if any((n_stakes, n_claim_rewards, n_unstake)):
                # one needs to commit only ones after while cycle
                # don't commit inside add_history
                logger.info(f"Staking events: saving {n_stakes=}, {n_claim_rewards=}, {n_unstake=}")
                await crud.session.commit()
        except Exception as e:
            logger.error(f"Staking events: error with processing:\n{e} {traceback.format_exc()}")
            return CommandResult(success=False, need_retry=True)

        return CommandResult(success=True, need_retry=False)
