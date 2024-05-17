import asyncio
import json
from collections import defaultdict
from datetime import timedelta
from typing import Any

import httpx
from redis.asyncio import Redis

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import get_redis
from app.env import settings
from app.schema import ChainId, Address
from app.services.coingecko.consts import (
    from_platform_to_chain_id,
    chain_id_to_native_coin_coingecko_id,
    chain_id_to_testnet_coin_coingecko_id,
)
from app.services.coingecko.types import ListCoin, CoinGeckoCoinId


class CoingeckoClient:
    def __init__(self, redis_cli: Redis, api_key: str | None = None):
        self.__redis = redis_cli
        self.__api_key = api_key
        self.__DEFAULT_HEADERS = {"x-cg-pro-api-key": self.__api_key} if self.__api_key else {}
        self.__host = (
            "https://pro-api.coingecko.com/api/v3"
            if self.__api_key
            else "https://api.coingecko.com/api/v3"
        )

    @property
    def redis(self) -> Redis:
        return self.__redis

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[Any, Any] | list[Any] | None:
        headers = headers or {}
        params = params or {}

        headers |= self.__DEFAULT_HEADERS

        for i in range(1, 5):
            try:
                async with httpx.AsyncClient(timeout=10.0, params=params) as client:
                    resp = await client.get(url, params=params, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()

                    coingecko_errors = await self.__increment_errors_count()
                    logger.info(f"Coingecko: error count={coingecko_errors}")
                    time_sleep = 0.5 * i
                    await asyncio.sleep(time_sleep)
                    resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error(f"Coingecko: error for {url} with {params=} and {headers=}: {exc}")
                return None

    async def get_coingecko_list_of_coins(self) -> list[ListCoin] | None:
        url = f"{self.__host}/coins/list"
        params = {"include_platform": True}
        resp = await self.get(url, params=params)
        return resp

    async def _get_price(self, token_ids: list[str]) -> dict[str, dict[str, float]] | None:
        url = f"{self.__host}/simple/price/"
        logger.info(f"Getting coingecko price for {token_ids}")
        params = {"ids": ",".join(set(token_ids)), "vs_currencies": "usd"}
        resp = await self.get(url, params=params)
        return resp

    async def __increment_errors_count(self) -> int:
        key = "coingecko_errors_count"
        if (count := await self.redis.incr(key)) == 1:
            await self.redis.expire(
                key, timedelta(minutes=settings.coingecko_errors_in_cache_minutes)
            )
        return count

    async def get_errors_count(self) -> int:
        res = await self.redis.get("coingecko_errors_count")
        return int(res) if res else 0

    async def get_coingecko_id_by_chain_id_and_address(
        self,
    ) -> dict[ChainId, dict[Address, CoinGeckoCoinId]]:
        """
        From this:
        [
            {
                "id": "cybria",
                "symbol": "cyba",
                "name": "Cybria",
                "platforms": {
                    "ethereum": "0x1063181dc986f76f7ea2dd109e16fc596d0f522a"
                },
            },
            {
                "id": "cybro",
                "symbol": "cybro",
                "name": "CYBRO",
                "platforms": {
                    "blast": "0x963eec23618bbc8e1766661d5f263f18094ae4d5"
                }
            }
        ]
        to this:
        {
            1: {"0x1063181dc986f76f7ea2dd109e16fc596d0f522a": "cybria"}
            81457: {"0x963eec23618bbc8e1766661d5f263f18094ae4d5": "cybro"}
        }
        """
        _value = await self.redis.get("coingecko_id_by_chain_id_and_address")
        value = json.loads(_value) if _value else {}
        if value:
            # json.loads returns dicts with string chain_ids, so we need to convert them to int
            return {int(key): value for key, value in value.items()}

        res: dict[ChainId, dict[Address, CoinGeckoCoinId]] = defaultdict(dict)
        list_of_coins: list[ListCoin] | None = await self.get_coingecko_list_of_coins()
        if not list_of_coins:
            logger.error("Coingecko: no list of coins")
            return {}

        for coin in list_of_coins:
            for platform_name, token_address_on_platform in coin["platforms"].items():
                if chain_id := from_platform_to_chain_id.get(platform_name):
                    res[chain_id][Address(token_address_on_platform)] = CoinGeckoCoinId(coin["id"])

        # support for native coins
        for chain_id, native_coin_id in chain_id_to_native_coin_coingecko_id.items():
            res[chain_id][Address(native_coin_id)] = CoinGeckoCoinId(native_coin_id)

        # support for tokens in testnets
        for (
            chain_id,
            token_address_to_coingecko_id,
        ) in chain_id_to_testnet_coin_coingecko_id.items():
            for address, coingecko_id in token_address_to_coingecko_id.items():
                res[chain_id][Address(address)] = CoinGeckoCoinId(coingecko_id)

        await self.redis.setex(
            "coingecko_id_by_chain_id_and_address", timedelta(hours=4), json.dumps(res)
        )
        return res

    async def get_token_address_by_coingecko_id(
        self,
        chain_id: ChainId,
    ) -> dict[CoinGeckoCoinId, Address]:
        _value = await self.redis.get(f"token_address_by_coingecko_id_{chain_id}")
        value = json.loads(_value) if _value else {}
        if value:
            return value

        coingecko_id_by_chain_id_and_address = await self.get_coingecko_id_by_chain_id_and_address()
        res = {}
        for token_address, coingecko_id in coingecko_id_by_chain_id_and_address.get(
            chain_id, {}
        ).items():
            res[coingecko_id] = token_address

        if not res:
            return {}

        await self.redis.setex(
            f"token_address_by_coingecko_id_{chain_id}", timedelta(minutes=30), json.dumps(res)
        )
        return res

    async def get_tokens_price(
        self, chain_id: ChainId, token_addresses: list[str | Address]
    ) -> dict[Address, float]:
        coingecko_id_by_chain_id_and_address = await self.get_coingecko_id_by_chain_id_and_address()
        token_address_by_coingecko_id = await self.get_token_address_by_coingecko_id(chain_id)

        token_ids_with_nans = (
            coingecko_id_by_chain_id_and_address.get(chain_id, {}).get(token_address.lower())
            for token_address in token_addresses
        )
        token_ids = [token_id for token_id in token_ids_with_nans if token_id]

        if (
            NATIVE_TOKEN_ADDRESS in token_addresses
            and chain_id in chain_id_to_native_coin_coingecko_id
        ):
            native_coin_id = chain_id_to_native_coin_coingecko_id[chain_id]
            token_ids.append(native_coin_id)
            token_address_by_coingecko_id[native_coin_id] = NATIVE_TOKEN_ADDRESS

        if not token_ids:
            logger.warning(f"Coingecko: no token ids for {chain_id=}, {token_addresses=}")
            return {}

        coingecko_prices: dict[CoinGeckoCoinId, dict[str, float]] | None = await self._get_price(
            token_ids
        )
        if coingecko_prices is None:
            logger.error(f"Coingecko: no prices for {chain_id=}, {token_addresses=}")
            return {}

        res: dict[Address, float] = {}
        for coingecko_id, coingecko_price in coingecko_prices.items():
            token_address = token_address_by_coingecko_id.get(coingecko_id)
            if token_address and (usd_price := coingecko_price.get("usd")):
                res[Address(token_address)] = usd_price
        return res


coingecko_cli = CoingeckoClient(redis_cli=get_redis(), api_key=settings.coingecko_api_key)
