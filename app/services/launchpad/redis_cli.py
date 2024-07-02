import json
from datetime import timedelta

from redis.asyncio import Redis

from app.dependencies import get_redis


class LaunchpadEventsCache:
    def __init__(self, redis_cli: Redis):
        self.redis_cli = redis_cli

    async def get_last_checked_block(self, chain_id: int) -> int | None:
        res = await self.redis_cli.get(f"last_checked_registered_users_and_allocations_{chain_id}")
        return int(res) if res else None

    async def set_last_checked_block(self, chain_id: int, block_height: int):
        await self.redis_cli.set(
            f"last_checked_registered_users_and_allocations_{chain_id}",
            json.dumps(block_height),
            ex=timedelta(hours=25),
        )


class LaunchpadMultichainEventsCache:
    def __init__(self, redis_cli: Redis):
        self.redis_cli = redis_cli

    def __get_key(self, chain_id: int, contract_address: str) -> str:
        return f"last_checked_multichain_event_{chain_id}_{contract_address.lower()}"

    async def get_last_checked_block(self, chain_id: int, contract_address: str) -> int | None:
        res = await self.redis_cli.get(self.__get_key(chain_id, contract_address))
        return int(res) if res else None

    async def set_last_checked_block(self, chain_id: int, contract_address: str, block_height: int):
        await self.redis_cli.set(
            self.__get_key(chain_id, contract_address),
            json.dumps(block_height),
            ex=timedelta(hours=25),
        )


launchpad_events_cache = LaunchpadEventsCache(redis_cli=get_redis())
launchpad_multichain_events_cache = LaunchpadMultichainEventsCache(redis_cli=get_redis())
