from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import async_session
from app.crud import OnRampCrud, LaunchpadProjectCrud

from app.env import (
    MUNZEN_API_KEY,
    MUNZEN_API_SECRET,
    MUNZEN_ENVIRONMENT,
    ONRAMP_RECIPIENT_ADDR,
    CRYPTO_API_KEY_BLAST,
    ONRAMP_SENDER_SEED_PHRASE,
    ETH_PRICE_FEED_ADDR,
    CRYPTO_ENVIRONMENT,
    CONTROLLER_SEED_PHRASE,
    CONTRACT_ADDR_POLYGON,
    CONTRACT_ADDR_ETH,
    CONTRACT_ADDR_BSC,
    USDT_CONTRACT_ADDR_POLYGON,
    USDT_CONTRACT_ADDR_ETH,
    CRYPTO_API_KEY_POLYGON,
    CRYPTO_API_KEY_ETH,
    CRYPTO_API_KEY_BSC,
    ONRAMP_SEED_PHRASE,
    CONTRACT_ADDR_BLAST,
    USDT_CONTRACT_ADDR_BLAST,
    USDT_CONTRACT_ADDR_BSC,
)
from app.redis import redis_cli
from app.services import Lock, Crypto as CryptoLaunchpad
from onramp.services import Munzen, Crypto, AmountConverter


def get_launchpad_crypto() -> CryptoLaunchpad:
    return CryptoLaunchpad(
        environment=CRYPTO_ENVIRONMENT,
        contracts={
            "polygon": CONTRACT_ADDR_POLYGON,
            "eth": CONTRACT_ADDR_ETH,
            "bsc": CONTRACT_ADDR_BSC,
            "blast": CONTRACT_ADDR_BLAST,
        },
        usdt_contracts={
            "polygon": USDT_CONTRACT_ADDR_POLYGON,
            "eth": USDT_CONTRACT_ADDR_ETH,
            "bsc": USDT_CONTRACT_ADDR_BSC,
            "blast": USDT_CONTRACT_ADDR_BLAST,
        },
        api_keys={
            "polygon": CRYPTO_API_KEY_POLYGON,
            "eth": CRYPTO_API_KEY_ETH,
            "bsc": CRYPTO_API_KEY_BSC,
            "blast": CRYPTO_API_KEY_BLAST,
        },
        private_key_seed=CONTROLLER_SEED_PHRASE,
        onramp_private_key_seed=ONRAMP_SEED_PHRASE,
    )


CryptoDep = Annotated[CryptoLaunchpad, Depends(get_launchpad_crypto)]


def get_redis() -> Redis:
    return redis_cli


RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_lock(redis: Redis = Depends(get_redis)) -> Lock:
    return Lock(redis)


async def get_session() -> AsyncSession:
    async with async_session() as session, session.begin():
        yield session


async def get_launchpad_projects_crud(
    session: AsyncSession = Depends(get_session),
) -> LaunchpadProjectCrud:

    return LaunchpadProjectCrud(session)


LaunchpadProjectCrudDep = Annotated[LaunchpadProjectCrud, Depends(get_launchpad_projects_crud)]


async def get_onramp_crud(session: AsyncSession = Depends(get_session)) -> OnRampCrud:
    return OnRampCrud(session)


async def get_munzen() -> Munzen:
    return Munzen(MUNZEN_API_KEY, MUNZEN_API_SECRET, MUNZEN_ENVIRONMENT, ONRAMP_RECIPIENT_ADDR)


async def get_crypto() -> Crypto:
    return Crypto(CRYPTO_API_KEY_BLAST, ONRAMP_SENDER_SEED_PHRASE, ETH_PRICE_FEED_ADDR)


async def get_amount_converter(
    redis: Redis = Depends(get_redis), crypto: Crypto = Depends(get_crypto)
) -> AmountConverter:
    return AmountConverter(redis, crypto)
