import json
from datetime import timedelta
from typing import Callable, Any, Awaitable

import bcrypt
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from redis.asyncio import Redis

from app.base import logger


def get_ip_from_request(request: Request) -> str:
    try:
        ip = request.headers.get("cf-connecting-ip")
        if not ip:
            ip = request.headers.get("x-forwarded-for")
        if not ip:
            ip = request.client.host
    except Exception as e:
        raise RuntimeError("Cannot get ip from request: {}".format(e))
    return ip


def validation_error(error_message: str, location: tuple[str, str]) -> RequestValidationError:
    return RequestValidationError(
        errors=[{"msg": error_message, "loc": location, "type": "value_error"}]
    )


async def get_data_with_cache(
    key: str,
    func: Callable[[], Awaitable[Any]],
    redis: Redis,
    short_key_exp_seconds: int = 30,
    long_key_exp_minutes: int = 20,
):
    if await redis.exists(key):
        cached_data = await redis.get(key)
        if cached_data:
            cached_data = cached_data.decode()
            cached_data = json.loads(cached_data)
            return cached_data

    try:
        cached_data = await func()
        if cached_data is None:
            logger.info("Get none from main function in get_data")
            raise Exception

        await redis.setex(
            key,
            timedelta(seconds=short_key_exp_seconds),
            json.dumps(cached_data),
        )
        await redis.setex(
            f"{key}:long",
            timedelta(minutes=long_key_exp_minutes),
            json.dumps(cached_data),
        )
    except Exception:
        cached_data = await redis.get(key + ":long")

        if cached_data is None:
            logger.info("No data in long cache")
            return cached_data

        cached_data = cached_data.decode()
        cached_data = json.loads(cached_data) if cached_data is not None else None
    return cached_data


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
