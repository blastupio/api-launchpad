import httpx

from app.base import logger
from app.schema import ChainId, Address
from app.services.coingecko.consts import from_platform_to_chain_id
from app.services.coingecko.types import ListCoin


async def get_coingecko_list_of_coins():
    url = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        json_response = response.json()

    return json_response


async def get_coingecko_id_by_chain_id_and_address():
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
    res: dict[ChainId, dict[Address, str]] = {}
    list_of_coins: list[ListCoin] = await get_coingecko_list_of_coins()
    for coin in list_of_coins:
        for platform_name, token_address_on_platform in coin["platforms"].items():
            chain_id = from_platform_to_chain_id.get(platform_name)
            if chain_id:
                if chain_id in res:
                    res[chain_id][Address(token_address_on_platform)] = coin["id"]
                else:
                    res[chain_id] = {Address(token_address_on_platform): coin["id"]}
    return res


def get_token_address_by_coingecko_id(
    chain_id: ChainId, coingecko_id_by_chain_id_and_address: dict[ChainId, dict[Address, str]]
) -> dict[str, Address]:
    res = {}
    for token_address, coingecko_id in coingecko_id_by_chain_id_and_address[chain_id].items():
        res[coingecko_id] = token_address
    return res


async def get_coingecko_price(token_ids: list[str]) -> dict[str, dict[str, float]]:
    url = "https://api.coingecko.com/api/v3/simple/price/"
    logger.info(f"Getting coingecko price for {token_ids}")
    params = {"ids": ",".join(token_ids), "vs_currencies": "usd"}
    async with httpx.AsyncClient(timeout=10.0, params=params) as client:
        response = await client.get(url)
        json_response = response.json()
    return json_response
