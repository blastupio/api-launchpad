from datetime import timedelta

from redis.asyncio import Redis


class Lock:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def acquire(self, key: str) -> bool:
        acquired = await self.redis.incr(key) == 1
        if acquired:
            await self.redis.expire(key, time=timedelta(minutes=5))

        return acquired

    async def expire(self, key: str, time: int | timedelta):
        if await self.redis.exists(key):
            await self.redis.expire(key, time=time)

    async def release(self, key: str):
        return await self.redis.delete(key)
