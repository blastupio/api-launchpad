import asyncio
import math
import time
import traceback
from collections import defaultdict

from fastapi import Depends
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3

from app import chains
from app.base import logger
from app.common import Command, CommandResult
from app.crud.history_staking import HistoryStakingCrud
from app.crud.points import PointsHistoryCrud
from app.crud.profiles import ProfilesCrud
from app.dependencies import (
    get_staking_history_crud,
    get_profile_crud,
    get_points_history_crud,
    get_lock,
)
from app.env import settings
from app.models import HistoryStakeType, PointsHistory, OperationType
from app.schema import CreateHistoryStake
from app.services import Lock
from app.services.ido_staking.abi import staking_abi
from app.services.ido_staking.multicall import get_locked_balance
from app.services.ido_staking.redis_cli import stake_history_redis
from app.services.prices import get_tokens_price_for_chain


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


class AddIdoStakingPoints(Command):
    async def command(
        self,
        crud: HistoryStakingCrud = Depends(get_staking_history_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        lock: Lock = Depends(get_lock),
    ) -> CommandResult:
        try:
            # get all users that staked some tokens
            user_addresses_by_token_address = await crud.get_user_addresses_by_token_address()

            # get locked balance from contract
            balance_by_token_address_and_user_address: dict[str, dict[str, float]] = {}
            for token_address, user_addresses in user_addresses_by_token_address.items():
                res = await get_locked_balance(token_address, user_addresses)
                balance_by_token_address_and_user_address.update(res)

            # get price for staked tokens
            chain_id = chains.blast.id if settings.app_env == "dev" else chains.blast_sepolia.id
            token_addresses = list(balance_by_token_address_and_user_address.keys())
            price_for_tokens = await get_tokens_price_for_chain(
                chain_id, token_addresses=token_addresses
            )
            if not price_for_tokens:
                logger.error(f"IDO points: no price for staked tokens: {token_addresses=}")
                return CommandResult(success=False, need_retry=True)
            elif len(price_for_tokens) < len(token_addresses):
                logger.error(f"IDO points: no price for some of staked tokens: {price_for_tokens=}")
                return CommandResult(success=False, need_retry=True)

            # calculate total usd balance for users locked balance
            usd_balance_by_user_address = defaultdict(float)
            for (
                token_address,
                token_balance_by_user_address,
            ) in balance_by_token_address_and_user_address.items():
                for user_address, balance in token_balance_by_user_address.items():
                    usd_balance = round(
                        price_for_tokens[token_address] * float(Web3.from_wei(balance, "ether")), 2
                    )
                    usd_balance_by_user_address[user_address] += usd_balance
        except Exception as e:
            logger.error(f"IDO points: error with processing:\n{e} {traceback.format_exc()}")
            return CommandResult(success=False, need_retry=True)

        # add points to profile if it has more than 100 USD staked
        try:
            while not await lock.acquire("add-ido-points"):
                await asyncio.sleep(0.001)
            for user_address, balance in usd_balance_by_user_address.items():
                if balance < 100:  # 100 usd
                    continue
                points_amount = math.ceil(balance / 100)
                profile = await profile_crud.get_or_create_profile(user_address)

                from app.tasks import add_ido_staking_points_for_profile

                add_ido_staking_points_for_profile.apply_async(
                    args=[profile.id, points_amount], countdown=1
                )
        finally:
            await lock.release("add-ido-points")
        return CommandResult(success=True, need_retry=False)


class AddIdoStakingPointsForProfile(Command):
    def __init__(self, profile_id: int, points_amount: int) -> None:
        self.profile_id = profile_id
        self.points_amount = points_amount

    async def command(
        self,
        crud: HistoryStakingCrud = Depends(get_staking_history_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        points_history_crud: PointsHistoryCrud = Depends(get_points_history_crud),
        lock: Lock = Depends(get_lock),
    ) -> CommandResult:
        lock_key = f"add-profile-ido-points-{self.profile_id}"
        try:
            while not await lock.acquire(lock_key):
                await asyncio.sleep(0.001)
            profile = await profile_crud.get_by_id(self.profile_id)
            if not profile:
                logger.info(f"IDO points: profile with id={self.profile_id} not found")
                return CommandResult(success=False, need_retry=False)

            logger.info(f"IDO points: adding {self.points_amount}BP to {profile.address}")
            points_before = profile.points
            profile.points = profile.points + self.points_amount
            await profile_crud.persist(profile)

            history = PointsHistory(
                profile_id=profile.id,
                points_before=points_before,
                amount=self.points_amount,
                points_after=profile.points,
                operation_type=OperationType.ADD_IDO_POINTS,
            )
            await points_history_crud.persist(history)
        except Exception as e:
            logger.error(
                f"IDO points: error with adding to {self.profile_id}:\n{e} {traceback.format_exc()}"
            )
            return CommandResult(success=False, need_retry=True)
        finally:
            await lock.release(lock_key)
        return CommandResult(success=True, need_retry=False)
