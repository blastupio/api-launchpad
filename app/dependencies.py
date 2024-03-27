from fastapi import Depends
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import async_session
from app.crud import OnRampCrud
from app.env import REDIS_URL, MUNZEN_API_KEY, MUNZEN_API_SECRET, MUNZEN_ENVIRONMENT, ONRAMP_RECIPIENT_ADDR, \
    CRYPTO_API_KEY_BLAST, ONRAMP_SENDER_SEED_PHRASE
from app.services import Lock
from onramp.services import Munzen, Crypto


async def get_redis() -> Redis:
    return from_url(REDIS_URL)


async def get_lock(redis: Redis = Depends(get_redis)) -> Lock:
    return Lock(redis)


async def get_session() -> AsyncSession:
    async with async_session() as session, session.begin():
        yield session


async def get_onramp_crud(session: AsyncSession = Depends(get_session)) -> OnRampCrud:
    return OnRampCrud(session)


async def get_munzen() -> Munzen:
    return Munzen(MUNZEN_API_KEY, MUNZEN_API_SECRET, MUNZEN_ENVIRONMENT, ONRAMP_RECIPIENT_ADDR)


async def get_crypto() -> Crypto:
    return Crypto(CRYPTO_API_KEY_BLAST, ONRAMP_SENDER_SEED_PHRASE)
