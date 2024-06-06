import json
from datetime import timedelta

from redis.asyncio import Redis

from app.base import logger
from app.dependencies import get_redis
from app.services.ido_staking.types import LockedAmount, UserLockedAmount


class TvlCache:
    def __init__(self, redis_cli: Redis) -> None:
        self.redis_cli = redis_cli

    def _get_cache_key(self) -> str:
        return "locked_amount_overview"

    async def set_locked_amount(self, locked_amount: LockedAmount) -> None:
        if not (locked_amount.native and locked_amount.stablecoin):
            logger.warning(f"TvlCache: locked_amount is empty: {locked_amount}")
            return
        value = {
            "native": locked_amount.native,
            "stablecoin": locked_amount.stablecoin,
        }
        await self.redis_cli.set(
            name=self._get_cache_key(), value=json.dumps(value), ex=timedelta(minutes=3)
        )

    async def get_locked_amount(self) -> LockedAmount | None:
        data = await self.redis_cli.get(name=self._get_cache_key())
        if data is None:
            return None
        return LockedAmount(**json.loads(data))


class UserTvlCache:
    def __init__(self, redis_cli: Redis) -> None:
        self.redis_cli = redis_cli

    def _get_cache_key(self, address: str) -> str:
        return f"locked_amount_overview_{address.lower()}"

    async def set_locked_amount(self, address: str, locked_amount: UserLockedAmount) -> None:
        value = {
            "native": locked_amount.native,
            "stablecoin": locked_amount.stablecoin,
        }
        await self.redis_cli.set(
            name=self._get_cache_key(address), value=json.dumps(value), ex=timedelta(seconds=30)
        )

    async def get_locked_amount(self, address: str) -> UserLockedAmount | None:
        data = await self.redis_cli.get(name=self._get_cache_key(address))
        if data is None:
            return None
        return UserLockedAmount(**json.loads(data))


tvl_cache = TvlCache(redis_cli=get_redis())
user_tvl_cache = UserTvlCache(redis_cli=get_redis())
