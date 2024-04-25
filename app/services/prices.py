import asyncio

from collections import defaultdict
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis

from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import get_redis
from app.schema import ChainId, Address, TokenInChain, RatesForChainAndToken
from app.services.coingecko.client import coingecko_cli
from app.services.coingecko.consts import chain_id_to_native_coin_coingecko_id
from app.services.coingecko.types import CoinGeckoCoinId


TOKEN_PRICE_TTL_MINUTES = 1


class TokenPriceCache:
    def __init__(self) -> None:
        self._redis_cli: Redis | None = None

    async def _get_redis(self):
        if self._redis_cli is None:
            self._redis_cli = await get_redis()
        return self._redis_cli

    def __get_cache_key(self, chain_id: ChainId, address: Address) -> str:
        return f"tkn-price-{chain_id}-{address.lower()}"

    def __get_chain_id_with_address_from_cache_key(self, cache_key: str) -> tuple[ChainId, Address]:
        chain_id, address = cache_key.split("-")[2:]
        return ChainId(int(chain_id)), Address(address)

    async def set(self, prices: dict[ChainId, dict[Address, float | None]]) -> None:  # noqa
        redis_cli = await self._get_redis()
        tasks = []
        for chain_id, addr_to_price in prices.items():
            for address, price in addr_to_price.items():
                cache_key = self.__get_cache_key(chain_id, address)
                if price:
                    tasks.append(
                        redis_cli.set(
                            cache_key, price, ex=timedelta(minutes=TOKEN_PRICE_TTL_MINUTES)
                        )
                    )
        await asyncio.gather(*tasks)

    async def get(
        self, addresses_by_chain_id: dict[ChainId, list[str]]
    ) -> dict[ChainId, dict[Address, float]]:
        redis_cli = await self._get_redis()
        keys = [
            self.__get_cache_key(chain_id, Address(address))
            for chain_id, addr_list in addresses_by_chain_id.items()
            for address in addr_list
        ]
        if not (data := await redis_cli.mget(keys)):
            return {}

        res: dict[ChainId, dict[Address, float]] = {}
        for key, value in zip(keys, data):
            chain_id, address = self.__get_chain_id_with_address_from_cache_key(key)
            if value:
                res.setdefault(chain_id, {})[address] = float(value)
        return res


async def get_tokens_price(chain_id: ChainId, token_addresses: list[str]) -> dict[Address, float]:
    if not token_addresses:
        return {}

    # try to get from cache
    cached_prices_for_chain_id = await token_price_cache.get({chain_id: token_addresses})
    cached_prices = cached_prices_for_chain_id.get(chain_id, {})

    if len(token_addresses) == len(cached_prices):
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

    from_price = prices_agg[from_token.chain_id].get(from_token.address)
    if not from_price:
        return rates
    for to_token in to_tokens:
        to_price = prices_agg.get(to_token.chain_id, {}).get(to_token.address)
        if not to_price:
            rates[to_token.chain_id][to_token.address] = None
            continue
        rates[to_token.chain_id][to_token.address] = from_price / to_price
    return rates


token_price_cache = TokenPriceCache()
