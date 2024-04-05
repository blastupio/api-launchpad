from time import time

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.dependencies import get_redis
from .v1.router import router as v1router


async def _calculate_rpm(redis: Redis = Depends(get_redis)) -> int:
    current_minute = int(time() / 60) * 60
    res = await redis.incr(f"rpm:{current_minute}")
    if res == 1:
        await redis.expire(f"rpm:{current_minute}", 600)
    return res


router = APIRouter(dependencies=[Depends(_calculate_rpm)])
router.include_router(v1router)


@router.get("/internal/rpm")
async def get_current_rpm(redis: Redis = Depends(get_redis)):
    stats = []
    for i in range(10):
        minute = int(time() / 60) * 60 - (1 + i) * 60
        if await redis.exists(f"rpm:{minute}"):
            value = (await redis.get(f"rpm:{minute}")).decode('utf-8')

            if not value:
                continue
            stats.append(int(value))

    return {
        "ok": True,
        "data": {
            "rpm": sum(stats) / len(stats) if len(stats) > 0 else 0,
            "probes": len(stats),
            "min": min(*stats) if len(stats) > 1 else 0,
            "max": max(*stats) if len(stats) > 1 else 0,
        }
    }
