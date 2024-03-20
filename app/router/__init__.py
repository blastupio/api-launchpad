from time import time

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.dependencies import get_redis


async def _calculate_rpm(redis: Redis = Depends(get_redis)) -> int:
    current_minute = int(time() / 60) * 60
    res = await redis.incr(f"rpm:{current_minute}")
    if res == 1:
        await redis.expire(f"rpm:{current_minute}", 600)
    return res


router = APIRouter(dependencies=[Depends(_calculate_rpm)])
