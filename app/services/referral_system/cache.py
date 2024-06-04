import json
from datetime import timedelta

from redis.asyncio import Redis

from app.dependencies import get_redis


class ReferralRedis:
    def __init__(self, redis_cli: Redis):
        self.redis_cli = redis_cli

    def _get_n_referrals_key(self, address: str) -> str:
        return f"n_referrals_{address.lower()}"

    async def get_n_referrals(self, address: str) -> int | None:
        res = await self.redis_cli.get(name=self._get_n_referrals_key(address))
        return int(res) if res else None

    async def set_n_referrals(self, address: str, n_referrals: int) -> None:
        await self.redis_cli.set(
            name=self._get_n_referrals_key(address),
            value=json.dumps(n_referrals),
            ex=timedelta(minutes=1),
        )


referral_redis = ReferralRedis(redis_cli=get_redis())
