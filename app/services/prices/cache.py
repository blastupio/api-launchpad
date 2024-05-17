import asyncio
from datetime import timedelta

from redis.asyncio import Redis

from app.dependencies import get_redis
from app.schema import ChainId, Address


class TokenPriceCache:
    def __init__(self, redis_cli: Redis) -> None:
        self._redis_cli = redis_cli

    @property
    def redis(self):
        return self._redis_cli

    def __get_cache_key(self, chain_id: ChainId, address: Address) -> str:
        return f"tkn-price-{chain_id}-{address.lower()}"

    def __get_chain_id_with_address_from_cache_key(self, cache_key: str) -> tuple[ChainId, Address]:
        chain_id, address = cache_key.split("-")[2:]
        return ChainId(int(chain_id)), Address(address)

    async def set(  # noqa
        self, prices: dict[ChainId, dict[Address, float | None]], ex: timedelta | None = None
    ) -> None:  # noqa
        tasks = []
        for chain_id, addr_to_price in prices.items():
            for address, price in addr_to_price.items():
                cache_key = self.__get_cache_key(chain_id, address)
                if price:
                    tasks.append(self.redis.set(cache_key, price, ex=ex))
        await asyncio.gather(*tasks)

    async def get(
        self, addresses_by_chain_id: dict[ChainId, list[str]]
    ) -> dict[ChainId, dict[Address, float]]:
        keys = [
            self.__get_cache_key(chain_id, Address(address))
            for chain_id, addr_list in addresses_by_chain_id.items()
            for address in addr_list
        ]
        if not (data := await self.redis.mget(keys)):
            return {}

        res: dict[ChainId, dict[Address, float]] = {}
        for key, value in zip(keys, data):
            chain_id, address = self.__get_chain_id_with_address_from_cache_key(key)
            if value:
                res.setdefault(chain_id, {})[address] = float(value)
        return res


token_price_cache = TokenPriceCache(redis_cli=get_redis())
