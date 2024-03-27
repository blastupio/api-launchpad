from fastapi import Depends
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import async_session
from app.env import REDIS_URL
from app.services import Lock
from app.crud import LaunchpadProjectCrud


async def get_redis() -> Redis:
    return from_url(REDIS_URL)


async def get_lock(redis: Redis = Depends(get_redis)) -> Lock:
    return Lock(redis)


async def get_session() -> AsyncSession:
    async with async_session() as session, session.begin():
        yield session


async def get_launchpad_projects_crud(session: AsyncSession = Depends(get_session)) -> \
        LaunchpadProjectCrud:

    return LaunchpadProjectCrud(session)
