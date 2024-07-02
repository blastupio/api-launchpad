import asyncio
import traceback
from collections import defaultdict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import logger, engine
from app.common import Command, CommandResult
from app.crud.history_blp_staking import HistoryBlpStakingCrud
from app.crud.profiles import ProfilesCrud
from app.dependencies import (
    get_staking_blp_history_crud,
    get_profile_crud,
    get_lock,
    get_add_points,
    get_launchpad_crypto,
)
from app.models import HistoryBlpStakeType, OperationType, OperationReason
from app.schema import CreateBlpHistoryStake
from app.services import Lock, Crypto
from app.services.blp_staking.consts import pool_by_id, get_blp_staking_contract
from app.services.blp_staking.multicall import get_staked_balance
from app.services.blp_staking.cache import stake_blp_history_cache
from app.services.blp_staking.reward import calculate_bp_daily_reward
from app.services.points.add_points import AddPoints
from app.services.web3_nodes import web3_node


class ProcessBlpHistoryStakingEvent(Command):
    async def command(
        self,
        crud: HistoryBlpStakingCrud = Depends(get_staking_blp_history_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
    ) -> CommandResult:
        web3 = await web3_node.get_web3(network="blast")
        chain_id = await web3.eth.chain_id
        current_block = await web3.eth.block_number

        for pool_id, pool in pool_by_id.items():
            if (
                last_checked_block := await stake_blp_history_cache.get_last_checked_block(
                    chain_id, pool_id
                )
            ) is None:
                last_checked_block = current_block - 100_000

            while True:
                from_block = last_checked_block + 1
                # 3000 is limit, can't set larger than that
                to_block = min(current_block, from_block + 3000)
                logger.info(
                    f"BlpStaking events: monitoring {pool.staking_contract_address} {from_block=} {to_block=}"  # noqa
                )

                if from_block > to_block:
                    logger.info(f"BlpStaking events: no events {from_block=} {to_block=}")
                    break

                from app.tasks import monitor_and_save_blp_staking_events

                monitor_and_save_blp_staking_events.apply_async(
                    kwargs={
                        "from_block": from_block,
                        "to_block": to_block,
                        "pool_id": pool_id,
                        "chain_id": chain_id,
                    },
                    countdown=1,
                )

                last_checked_block = to_block
                await stake_blp_history_cache.set_last_checked_block(chain_id, pool_id, to_block)
                await asyncio.sleep(0.5)

        return CommandResult(success=True, need_retry=False)


class MonitorBlpStakingLogsAndSave(Command):
    def __init__(self, from_block: int, to_block: int, chain_id: int, pool_id: int) -> None:
        self.from_block = from_block
        self.to_block = to_block
        self.chain_id = chain_id
        self.pool_id = pool_id

    async def _save_stake_events(
        self,
        crud: HistoryBlpStakingCrud,
        profile_crud: ProfilesCrud,
        events,
    ) -> None:
        for event in events:
            await crud.add_history(
                params=CreateBlpHistoryStake(
                    type=HistoryBlpStakeType.STAKE,
                    amount=str(event.args["amount"]),
                    txn_hash=event.transactionHash.hex(),
                    block_number=event.blockNumber,
                    chain_id=str(self.chain_id),
                    user_address=event.args["user"],
                    pool_id=self.pool_id,
                )
            )
            # save new profile if not exists
            await profile_crud.get_or_create_profile(address=event.args["user"])

    async def _save_claim_rewards_events(self, crud: HistoryBlpStakingCrud, events) -> None:
        for event in events:
            await crud.add_history(
                params=CreateBlpHistoryStake(
                    type=HistoryBlpStakeType.CLAIM_REWARDS,
                    amount=str(event.args["amount"]),
                    txn_hash=event.transactionHash.hex(),
                    block_number=event.blockNumber,
                    chain_id=str(self.chain_id),
                    user_address=event.args["user"],
                    pool_id=self.pool_id,
                )
            )

    async def _save_unstake_events(self, crud: HistoryBlpStakingCrud, events) -> None:
        for event in events:
            await crud.add_history(
                params=CreateBlpHistoryStake(
                    type=HistoryBlpStakeType.UNSTAKE,
                    amount=str(event.args["amount"]),
                    user_address=event.args["user"],
                    txn_hash=event.transactionHash.hex(),
                    block_number=event.blockNumber,
                    chain_id=str(self.chain_id),
                    pool_id=self.pool_id,
                )
            )

    async def command(
        self,
        crud: HistoryBlpStakingCrud = Depends(get_staking_blp_history_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
    ) -> CommandResult:
        web3 = await web3_node.get_web3(network="blast")
        staking_contract = get_blp_staking_contract(web3, pool=pool_by_id[self.pool_id])

        try:
            stake_events = await staking_contract.events.Staked().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            n_stakes = len(stake_events)
            await self._save_stake_events(crud, profile_crud, stake_events)

            claim_reward_events = await staking_contract.events.Claimed().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            n_claim_rewards = len(claim_reward_events)
            await self._save_claim_rewards_events(crud, claim_reward_events)

            unstake_events = await staking_contract.events.Withdrawn().get_logs(
                fromBlock=self.from_block, toBlock=self.to_block
            )
            n_unstake = len(unstake_events)
            await self._save_unstake_events(crud, unstake_events)

            if any((n_stakes, n_claim_rewards, n_unstake)):
                logger.info(
                    f"BlpStaking events[{self.pool_id}]: saving {n_stakes=}, {n_claim_rewards=}, {n_unstake=}",  # noqa
                    extra={
                        "from_block": self.from_block,
                        "to_block": self.to_block,
                        "pool_id": self.pool_id,
                    },
                )
                await crud.session.commit()
        except Exception as e:
            logger.error(
                f"BlpStaking events[{self.pool_id}]: saving error:\n{e} {traceback.format_exc()}",
                extra={
                    "from_block": self.from_block,
                    "to_block": self.to_block,
                    "pool_id": self.pool_id,
                },
            )
            return CommandResult(success=False, need_retry=True)
        return CommandResult(success=True, need_retry=False)


class AddBlpStakingPoints(Command):
    async def command(
        self,
        crud: HistoryBlpStakingCrud = Depends(get_staking_blp_history_crud),
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        lock: Lock = Depends(get_lock),
        crypto: Crypto = Depends(get_launchpad_crypto),
    ) -> CommandResult:
        try:
            # get all users that staked some tokens
            user_addresses_by_pool_id = await crud.get_user_address_by_pool_id()

            # get locked balance from contract
            balance_by_pool_id_and_user_address: dict[int, dict[str, int]] = defaultdict(int)
            for pool_id, user_addresses in user_addresses_by_pool_id.items():
                pool = pool_by_id[pool_id]
                res = await get_staked_balance(pool.staking_contract_address, user_addresses)
                balance_by_pool_id_and_user_address[pool_id] = res
        except Exception as e:
            logger.error(
                f"BlpStaking: unhandled error while adding points:\n{e} {traceback.format_exc()}"
            )
            return CommandResult(success=False, need_retry=True)

        try:
            while not await lock.acquire("add-blp-staking-points"):
                await asyncio.sleep(0.001)

            for pool_id, balance_by_address in balance_by_pool_id_and_user_address.items():
                for user_address, pool_locked_balance in balance_by_address.items():
                    if pool_locked_balance == 0:
                        continue

                    staked_blp = await crypto.get_blp_staking_value(user_address)
                    points_amount = calculate_bp_daily_reward(
                        pool_locked_balance, staked_blp, pool_id
                    )
                    profile, _ = await profile_crud.get_or_create_profile(user_address)

                    from app.tasks import (
                        add_blp_staking_points_for_profile,
                        add_referral_blp_staking_points_for_profile,
                    )

                    add_blp_staking_points_for_profile.apply_async(
                        args=[user_address, points_amount],
                        countdown=1,
                    )
                    if referrer_address := profile.referrer:
                        referrer, _ = await profile_crud.get_or_create_profile(referrer_address)
                        referrer_points_amount = round(
                            points_amount * referrer.ref_percent / 100, 2
                        )
                        add_referral_blp_staking_points_for_profile.apply_async(
                            kwargs={
                                "address": referrer_address,
                                "points_amount": referrer_points_amount,
                                "referring_profile_id": profile.id,
                            },
                            countdown=1,
                        )
        finally:
            await lock.release("add-blp-staking-points")
        return CommandResult(success=True, need_retry=False)


class AddBlpStakingPointsForProfile(Command):
    def __init__(
        self,
        address: str,
        points_amount: float,
        operation_type: OperationType = OperationType.ADD_BLP_STAKING_POINTS,
        referring_profile_id: int | None = None,
        operation_reason: OperationReason | None = None,
    ) -> None:
        self.address = address
        self.points_amount = points_amount
        self.operation_type = operation_type
        self.referring_profile_id = referring_profile_id
        self.operation_reason = operation_reason

    async def command(
        self,
        profile_crud: ProfilesCrud = Depends(get_profile_crud),
        add_points: AddPoints = Depends(get_add_points),
        lock: Lock = Depends(get_lock),
    ) -> CommandResult:
        try:
            logger.info(
                f"BLP staking points: adding {self.operation_type} {self.points_amount}BP to {self.address}"  # noqa
            )
            async with AsyncSession(engine) as session:
                async with session.begin():
                    await add_points.add_points(
                        address=self.address,
                        amount=self.points_amount,
                        operation_type=self.operation_type,
                        operation_reason=self.operation_reason,
                        referring_profile_id=self.referring_profile_id,
                        session=session,
                    )
        except Exception as e:
            logger.error(
                f"LP staking points: error with adding to {self.address}:\n{e} {traceback.format_exc()}"  # noqa
            )
            return CommandResult(success=False, need_retry=True)
        return CommandResult(success=True, need_retry=False)
