import asyncio
from typing import Any

import httpx

from app.base import logger
from app.schema import ChainId, Address
from app.services.coingecko.consts import from_platform_to_chain_id
from app.services.coingecko.types import ListCoin, CoinGeckoCoinId


class CoingeckoClient:
    def __init__(self, api_key: str | None = None):
        self.__api_key = api_key
        self.__DEFAULT_PARAMS = {"x_cg_pro_api_key": self.__api_key} if self.__api_key else {}
        self.__host = (
            "https://api-pro.coingecko.com/api/v3"
            if self.__api_key
            else "https://api.coingecko.com/api/v3"
        )

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[Any, Any] | list[Any] | None:
        headers = headers or {}
        params = params or {}

        if hasattr(self, "__DEFAULT_PARAMS"):
            params |= self.__DEFAULT_PARAMS

        for i in range(1, 5):
            try:
                async with httpx.AsyncClient(timeout=10.0, params=params) as client:
                    resp = await client.get(url, params=params, headers=headers)
                    resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error(f"Error for {url} with {params=} and {headers=}: {exc}")
                return None
            if resp.status_code == 200:
                return resp.json()
            elif status := resp.status_code in (429, 500, 503):
                time_sleep = 0.5 * i
                logger.info(f"Bad {status=} for {url} with {params=} and {headers=}: {resp.text}")
                await asyncio.sleep(time_sleep)

    async def get_coingecko_list_of_coins(self) -> list[ListCoin]:
        url = f"{self.__host}/coins/list"
        params = {"include_platform": True}
        resp = await self.get(url, params=params)
        return resp

    async def get_coingecko_price(self, token_ids: list[str]) -> dict[str, dict[str, float]]:
        url = f"{self.__host}/simple/price/"
        logger.info(f"Getting coingecko price for {token_ids}")
        params = {"ids": ",".join(token_ids), "vs_currencies": "usd"}
        resp = await self.get(url, params=params)
        return resp

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
        res: dict[ChainId, dict[Address, CoinGeckoCoinId]] = {}
        list_of_coins: list[ListCoin] = await self.get_coingecko_list_of_coins()
        for coin in list_of_coins:
            for platform_name, token_address_on_platform in coin["platforms"].items():
                chain_id = from_platform_to_chain_id.get(platform_name)
                if chain_id:
                    if chain_id in res:
                        res[chain_id][Address(token_address_on_platform)] = CoinGeckoCoinId(
                            coin["id"]
                        )
                    else:
                        res[chain_id] = {
                            Address(token_address_on_platform): CoinGeckoCoinId(coin["id"])
                        }
        return res

    @staticmethod
    def get_token_address_by_coingecko_id(
        chain_id: ChainId,
        coingecko_id_by_chain_id_and_address: dict[ChainId, dict[Address, CoinGeckoCoinId]],
    ) -> dict[CoinGeckoCoinId, Address]:
        res = {}
        for token_address, coingecko_id in coingecko_id_by_chain_id_and_address[chain_id].items():
            res[coingecko_id] = token_address
        return res


coingecko_client = CoingeckoClient()
