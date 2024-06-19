import json
from datetime import timedelta

from redis.asyncio import Redis

from app.dependencies import get_redis


class StakeBlpHistoryRedis:
    def __init__(self, redis_cli: Redis):
        self.redis_cli = redis_cli

    @staticmethod
    def _get_key(chain_id: int, pool_id: int) -> str:
        return f"last_checked_blp_staking_block_{chain_id}_{pool_id}"

    async def get_last_checked_block(self, chain_id: int, pool_id: int) -> int | None:
        res = await self.redis_cli.get(self._get_key(chain_id, pool_id))
        return int(res) if res else None

    async def set_last_checked_block(self, chain_id: int, pool_id: int, block_height: int):
        await self.redis_cli.set(
            self._get_key(chain_id, pool_id),
            json.dumps(block_height),
            ex=timedelta(hours=25),
        )


stake_blp_history_redis = StakeBlpHistoryRedis(redis_cli=get_redis())
