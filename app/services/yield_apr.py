import httpx

from app.base import logger


async def get_native_yield() -> float:
    default_value = 3.0
    url = "https://eth-api.lido.fi/v1/protocol/steth/apr/sma"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = (await client.get(url)).json()
    value = response.get("data", {}).get("smaApr", default_value)
    return round(value, 4)


async def get_stablecoin_yield() -> float:
    default_value = 10.0
    url = "https://summer.fi/api/product-hub"
    data = {"protocols": ["maker"], "testnet": False}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=data)
        if response.status_code != 200:
            logger.error(f"Request to {url} failed with {response.status_code}\n{response.text}")
            return default_value
        response = response.json()

    try:
        str_value = [
            x for x in response["table"] if x["earnStrategyDescription"] == "DAI Savings Rate"
        ][0]
        return float(str_value) * 100
    except (IndexError, KeyError, TypeError):
        return default_value
