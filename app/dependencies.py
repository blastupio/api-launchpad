from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import async_session
from app.crud import OnRampCrud, LaunchpadProjectCrud

from app.env import settings

from app.redis import redis_cli
from app.services import Lock, Crypto as CryptoLaunchpad
from onramp.services import Munzen, Crypto, AmountConverter


def get_launchpad_crypto() -> CryptoLaunchpad:
    return CryptoLaunchpad(
        environment=settings.crypto_environment,
        contracts={
            "polygon": settings.contract_addr_polygon,
            "eth": settings.contract_addr_eth,
            "bsc": settings.contract_addr_bsc,
            "blast": settings.contract_addr_blast,
        },
        usdt_contracts={
            "polygon": settings.usdt_contract_addr_polygon,
            "eth": settings.usdt_contract_addr_eth,
            "bsc": settings.usdt_contract_addr_bsc,
            "blast": settings.usdt_contract_addr_blast,
        },
        api_keys={
            "polygon": settings.crypto_api_key_polygon,
            "eth": settings.crypto_api_key_eth,
            "bsc": settings.crypto_api_key_bsc,
            "blast": settings.crypto_api_key_blast,
        },
        private_key_seed=settings.controller_seed_phrase,
        onramp_private_key_seed=settings.onramp_seed_phrase,
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
    return Munzen(
        settings.munzen_api_key,
        settings.munzen_api_secret,
        settings.munzen_environment,
        settings.onramp_recipient_addr,
    )


async def get_crypto() -> Crypto:
    return Crypto(
        settings.crypto_api_key_blast,
        settings.onramp_sender_seed_phrase,
        settings.eth_price_feed_addr,
    )


async def get_amount_converter(
    redis: Redis = Depends(get_redis), crypto: Crypto = Depends(get_crypto)
) -> AmountConverter:
    return AmountConverter(redis, crypto)
