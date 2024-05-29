import httpx

from app.base import logger


async def get_native_yield() -> float:
    default_value = 3.0
    url = "https://eth-api.lido.fi/v1/protocol/steth/apr/sma"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        if response.status_code != 200:
            logger.error(f"Request to {url} failed with {response.status_code}\n{response.text}")
            return default_value
        response = response.json()
    value = response.get("data", {}).get("smaApr", default_value)
    return round(value, 4)


async def get_stablecoin_yield() -> float:
    """
    get from https://summer.fi/earn?deposit-token=DAI&protocol=maker
    """
    default_value = 10.0
    url = "https://summer.fi/api/prerequisites"
    params = {"protocols": "maker,sparkv3"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            err = f"Request to {url} failed with {response.status_code}\n{response.text}"
            logger.warning(err)
            return default_value
        response = response.json()

    try:
        dict_description = [x for x in response["productHub"]["table"] if x["label"] == "DSR"][0]
        str_value = dict_description["weeklyNetApy"]
        return float(str_value) * 100
    except (IndexError, KeyError, TypeError):
        return default_value
