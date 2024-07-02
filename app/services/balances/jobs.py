from decimal import Decimal, getcontext
from time import sleep

from fastapi import Depends
from sqlalchemy import select, func, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3
from sqlalchemy.dialects.postgresql import insert

from app.base import logger
from app.common import Command, CommandResult
from app.dependencies import (
    get_launchpad_crypto,
    get_session,
)
from app.models import HistoryBlpStake, BalanceSync
from app.services import Crypto


class SyncBalances(Command):
    async def command(
        self,
        session: AsyncSession = Depends(get_session),
        crypto: Crypto = Depends(get_launchpad_crypto),
    ) -> CommandResult:
        addresses = (await session.scalars(select(HistoryBlpStake.user_address).distinct())).all()
        await session.execute(text(f"TRUNCATE TABLE {BalanceSync.__tablename__}"))
        await session.execute(insert(BalanceSync).values([{"address": x} for x in addresses]))

        logger.info(f"SyncBalances: processing for {len(addresses)} addresses...")

        await self.__process(addresses, crypto, session)
        for i in range(3):
            addresses = (
                await session.scalars(
                    select(BalanceSync.address).where(BalanceSync.should_be_synced.is_(True))
                )
            ).all()
            if not addresses:
                break

            logger.info(f"SyncBalances: (retry {i+1}) processing for {len(addresses)} addresses...")
            await self.__process(addresses, crypto, session)

        return CommandResult(success=True)

    async def __process(self, addresses, crypto, session):
        for i, address in enumerate(addresses):
            if i % 10 == 0:
                logger.info(f"SyncBalances: processing {i+1}/{len(addresses)}")
            try:
                locked_blp_balance = await self.__with_retry(crypto.get_locked_blp_balance, address)
                blp_staking_value = await self.__with_retry(crypto.get_blp_staking_value, address)
            except Exception as e:
                logger.error(f"SyncBalances: failed to get balance for {address}: {e}")
                continue

            getcontext().prec = 18
            locked_balance_d = Decimal(Web3.from_wei(locked_blp_balance, "ether"))
            staking_balance_d = Decimal(Web3.from_wei(blp_staking_value, "ether"))
            locked_balance = str(locked_balance_d)
            staking_balance = str(staking_balance_d)
            staking_percent = str(staking_balance_d / (locked_balance_d + staking_balance_d) * 100)

            await session.execute(
                update(BalanceSync)
                .where(BalanceSync.address == address)
                .values(
                    locked_balance=locked_balance,
                    staking_balance=staking_balance,
                    staking_percent=staking_percent,
                    synced_at=func.now(),
                    should_be_synced=False,
                )
            )

    @staticmethod
    async def __with_retry(func_, address: str):
        for i in range(4):
            try:
                return await func_(address)
            except Exception as e:
                logger.warning(f"SyncBalances: retrying {func_.__name__} for {address}: {e}")
                if i == 3:
                    raise e
                sleep(0.1)
