import asyncio

from collections import defaultdict
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import get_redis
from app.schema import ChainId, Address, TokenInChain, RatesForChainAndToken
from app.services.coingecko.client import coingecko_cli
from app.services.coingecko.consts import chain_id_to_native_coin_coingecko_id
from app.services.coingecko.types import CoinGeckoCoinId


TOKEN_PRICE_TTL_MINUTES = 1
LONG_TOKEN_PRICE_TTL_MINUTES = 10
ERRORS_COUNT_TO_SWITCH_TO_LONG_CACHE = 10


class TokenPriceCache:
    def __init__(self, redis_cli: Redis) -> None:
        self._redis_cli = redis_cli

    @property
    def redis(self):
        return self._redis_cli

    def __get_cache_key(self, chain_id: ChainId, address: Address) -> str:
        return f"tkn-price-{chain_id}-{address.lower()}"

    def __get_long_cache_key(self, chain_id: ChainId, address: Address) -> str:
        return f"long:tkn-price-{chain_id}-{address.lower()}"

    def __get_chain_id_with_address_from_cache_key(self, cache_key: str) -> tuple[ChainId, Address]:
        chain_id, address = cache_key.split("-")[2:]
        return ChainId(int(chain_id)), Address(address)

    async def set(self, prices: dict[ChainId, dict[Address, float | None]]) -> None:  # noqa
        tasks = []
        for chain_id, addr_to_price in prices.items():
            for address, price in addr_to_price.items():
                cache_key = self.__get_cache_key(chain_id, address)
                long_cache_key = self.__get_long_cache_key(chain_id, address)
                if price:
                    tasks.append(
                        self.redis.set(
                            cache_key, price, ex=timedelta(minutes=TOKEN_PRICE_TTL_MINUTES)
                        )
                    )
                    tasks.append(
                        self.redis.set(
                            long_cache_key,
                            price,
                            ex=timedelta(minutes=LONG_TOKEN_PRICE_TTL_MINUTES),
                        )
                    )
        await asyncio.gather(*tasks)

    async def get(
        self, addresses_by_chain_id: dict[ChainId, list[str]], get_from_long_cache: bool = False
    ) -> dict[ChainId, dict[Address, float]]:
        res: dict[ChainId, dict[Address, float]] = {}
        key_func = self.__get_long_cache_key if get_from_long_cache else self.__get_cache_key

        keys = [
            key_func(chain_id, Address(address))
            for chain_id, addr_list in addresses_by_chain_id.items()
            for address in addr_list
        ]
        if values := [value for value in await self.redis.mget(keys) if value]:
            for key, value in zip(keys, values):
                chain_id, address = self.__get_chain_id_with_address_from_cache_key(key)
                if value:
                    res.setdefault(chain_id, {})[address] = float(value)
        return res


def _use_long_cache_to_get_prices(errors_count: int) -> bool:
    if errors_count >= ERRORS_COUNT_TO_SWITCH_TO_LONG_CACHE:
        logger.info(f"Prices: {errors_count=}, switching to long cache")
        return True
    return False


async def get_tokens_price(
    chain_id: ChainId, token_addresses: list[str | Address]
) -> dict[Address, float]:
    if not token_addresses:
        return {}

    provider_errors_count = await coingecko_cli.get_errors_count()
    # try to get from cache
    cached_prices_for_chain_id = await token_price_cache.get(
        {chain_id: token_addresses},
        get_from_long_cache=_use_long_cache_to_get_prices(provider_errors_count),
    )
    cached_prices = cached_prices_for_chain_id.get(chain_id, {})

    if len(token_addresses) == len(cached_prices):
        logger.info(f"Prices: cache hit for {chain_id=}, {token_addresses=}")
        # all tokens in cache
        return cached_prices

    # get only addresses that are not in cache
    token_addresses_with_coingecko = [
        address for address in token_addresses if address not in cached_prices
    ]

    coingecko_id_by_chain_id_and_address = (
        await coingecko_cli.get_coingecko_id_by_chain_id_and_address()
    )
    token_address_by_coingecko_id = await coingecko_cli.get_token_address_by_coingecko_id(
        chain_id, coingecko_id_by_chain_id_and_address
    )

    token_ids_with_nans = (
        coingecko_id_by_chain_id_and_address.get(chain_id, {}).get(token_address.lower())
        for token_address in token_addresses_with_coingecko
    )
    token_ids = [token_id for token_id in token_ids_with_nans if token_id]
    if (
        NATIVE_TOKEN_ADDRESS in token_addresses_with_coingecko
        and chain_id in chain_id_to_native_coin_coingecko_id
    ):
        native_coin_id = chain_id_to_native_coin_coingecko_id[chain_id]
        token_ids.append(native_coin_id)
        token_address_by_coingecko_id[native_coin_id] = NATIVE_TOKEN_ADDRESS

    if not token_ids:
        logger.warning(f"Prices: no token ids for {chain_id=}, {token_addresses=}")
        return {}

    coingecko_prices: dict[CoinGeckoCoinId, dict[str, float]] | None = (
        await coingecko_cli.get_coingecko_price(token_ids)
    )
    if coingecko_prices is None:
        return cached_prices

    res: dict[Address, float] = {}
    for coingecko_id, coingecko_price in coingecko_prices.items():
        token_address = token_address_by_coingecko_id.get(coingecko_id)
        if token_address and (usd_price := coingecko_price.get("usd")):
            res[Address(token_address)] = usd_price

    if res:
        logger.info(f"Prices: cache {chain_id=}, {token_addresses=}")
        await token_price_cache.set({chain_id: res})  # cache result from coingecko
    res.update(cached_prices)
    return res


async def get_any2any_prices(
    from_token: TokenInChain, to_tokens: list[TokenInChain]
) -> RatesForChainAndToken:
    tokens_by_chains: defaultdict[ChainId, list[Address]] = defaultdict(list)
    for token in [from_token] + to_tokens:
        tokens_by_chains[token.chain_id].append(token.address)

    coros = []
    for chain_id, addresses in tokens_by_chains.items():
        coros.append(get_tokens_price(chain_id, addresses))
    prices_result = await asyncio.gather(*coros)

    prices_agg: dict[ChainId, dict[str, Any]] = {}
    for chain_id, prices in zip(tokens_by_chains.keys(), prices_result):
        prices_agg[chain_id] = prices

    rates: RatesForChainAndToken = defaultdict(dict)

    from_price = prices_agg[from_token.chain_id].get(from_token.address.lower())
    if not from_price:
        return rates
    for to_token in to_tokens:
        to_price = prices_agg.get(to_token.chain_id, {}).get(to_token.address.lower())
        if not to_price:
            rates[to_token.chain_id][to_token.address.lower()] = None
            continue
        rates[to_token.chain_id][to_token.address.lower()] = from_price / to_price
    return rates


token_price_cache = TokenPriceCache(redis_cli=get_redis())
