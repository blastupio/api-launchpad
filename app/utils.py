import json
from datetime import timedelta
from typing import Callable, Any, Awaitable

from fastapi.exceptions import RequestValidationError
from redis.asyncio import Redis

from app.base import logger


def validation_error(error_message: str, location: tuple[str, str]) -> RequestValidationError:
    return RequestValidationError(errors=[{"msg": error_message, "loc": location, "type": "value_error"}])


async def get_data_with_cache(key: str, func: Callable[[], Awaitable[Any]], redis: Redis):
    if await redis.exists(key):
        cached_data = await redis.get(key)
        cached_data = json.loads(cached_data)
    else:
        try:
            cached_data = await func()
            if cached_data is None:
                logger.info("Get none from main function in get_data")
                raise Exception
            if isinstance(cached_data, (dict, list)):
                value_to_cache = json.dumps(cached_data)
            else:
                value_to_cache = str(cached_data)
            await redis.setex(key, value=value_to_cache, time=timedelta(seconds=30))
            await redis.setex(key + ":long", value=value_to_cache, time=timedelta(minutes=20))
        except Exception as exec:
            cached_data = await redis.get(key + ':long')
            cached_data = int(cached_data) if cached_data is not None else None
            if cached_data is None:
                logger.info("No data in long cache")

    return cached_data
