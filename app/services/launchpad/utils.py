import asyncio

from httpx import AsyncClient

from app.base import logger


async def get_crypto_contracts(project_proxy_url: str) -> dict[str, str] | None:
    async with AsyncClient(timeout=5) as client:
        err = None
        _url = f"{project_proxy_url.rstrip('/')}/"
        url = f"{_url}crypto/contracts"
        for i in range(5):
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    err = response.text
                    await asyncio.sleep(i * 0.5)
                    continue
                json_response = response.json()
                return json_response.get("data", {}).get("contracts")
            except Exception as e:
                err = e
                await asyncio.sleep(i * 0.5)
        if err:
            logger.error(f"Can't get contracts for {url=}: {err}")
    return None


class CoinTypeResolver:
    @staticmethod
    def is_native(func: str):
        return func in (
            "depositCoin(address referrer)",
            "depositCoin(address)",
            "depositCoinTo(address to,address referrer)",
            "depositCoin",
            "depositCoinTo",
        )
