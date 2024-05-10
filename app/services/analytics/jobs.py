import time

from fastapi import Depends

from app.base import logger
from app.common import Command, CommandResult
from app.env import settings
from app.services.analytics.redis_cli import reg_users_and_allocation_redis
from app.services.web3_nodes import web3_node


class ProcessRegisteredUsersAndAllocations(Command):
    async def command(
        self,
        # crud: HistoryStakingCrud = Depends(get_staking_history_crud),
    ) -> CommandResult:
        if not settings.launchpad_contract_address:
            logger.error(
                "Process registered users and allocations: launchpad contract address is not set"
            )
            return CommandResult(success=False, need_retry=False)

        web3 = await web3_node.get_web3(network="blast")
        chain_id = await web3.eth.chain_id
        current_block = await web3.eth.block_number
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
            # abi=staking_abi,
        )
        n_stakes, n_claim_rewards = 0, 0
        try:
            while True:
                from_block = last_checked_block + 1
                # 3000 is limit, can't set larger than that
                to_block = min(current_block, from_block + 3000)
                logger.info(f"Monitoring from block {from_block} to block {to_block}")

                if from_block > to_block:
                    logger.info(f"No events from block {from_block} to block {to_block}")
                    break

                stake_events = await contract.events.Staked().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_stakes += len(stake_events)
                # for event in stake_events:
                # await crud.add_history(
                #     params=CreateHistoryStake(
                #         type=HistoryStakeType.STAKE,
                #         token_address=event.args["stakingToken"],
                #         amount=str(event.args["amount"]),
                #         txn_hash=event.transactionHash.hex(),
                #         block_number=event.blockNumber,
                #         chain_id=str(chain_id),
                #         user_address=event.args["user"],
                #     )
                # )

                claim_reward_events = await contract.events.RewardClaimed().get_logs(
                    fromBlock=from_block, toBlock=to_block
                )
                n_claim_rewards += len(claim_reward_events)
                # for event in claim_reward_events:
                #     await crud.add_history(
                #         params=CreateHistoryStake(
                #             type=HistoryStakeType.CLAIM_REWARDS,
                #             token_address=event.args["stakingToken"],
                #             amount=str(event.args["amountInStakingToken"]),
                #             txn_hash=event.transactionHash.hex(),
                #             block_number=event.blockNumber,
                #             chain_id=str(chain_id),
                #             user_address=event.args["user"],
                #         )
                #     )

                last_checked_block = to_block
                await reg_users_and_allocation_redis.set_last_checked_block(chain_id, to_block)
                time.sleep(0.5)

            # if n_stakes or n_claim_rewards:
            #     # one needs to commit only ones after while cycle
            #     # don't commit inside add_history
            #     await crud.session.commit()
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            return CommandResult(success=False, need_retry=True)

        return CommandResult(success=True, need_retry=False)
