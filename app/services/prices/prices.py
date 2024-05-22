import asyncio

from collections import defaultdict
from typing import Any

from app.base import logger
from app.schema import ChainId, Address, TokenInChain, RatesForChainAndToken
from app.services.coingecko.client import coingecko_cli
from app.services.prices.cache import token_price_cache


async def get_tokens_price_for_chain(
    chain_id: ChainId, token_addresses: list[str | Address]
) -> dict[Address, float]:
    """
    Get prices from cache and coingecko.
    """
    if not token_addresses:
        return {}

    # try to get from cache
    cached_prices_for_chain_id = await token_price_cache.get({chain_id: token_addresses})
    cached_prices = cached_prices_for_chain_id.get(chain_id, {})

    if len(token_addresses) == len(cached_prices):
        logger.info(f"Prices: full cache hit for {chain_id=}, {token_addresses=}")
        # all tokens in cache
        return cached_prices

    res: dict[Address, float] = {}

    # get only addresses that are not in cache
    token_addresses_with_coingecko = [
        address for address in token_addresses if address not in cached_prices
    ]
    coingecko_prices = await coingecko_cli.get_tokens_price(
        chain_id, token_addresses_with_coingecko
    )
    res.update(coingecko_prices)
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
        coros.append(get_tokens_price_for_chain(chain_id, addresses))
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
