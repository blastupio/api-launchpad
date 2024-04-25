import json
from datetime import timedelta

from fastapi import APIRouter, Path

from app.base import logger
from app.dependencies import RedisDep, CryptoDep
from app.schema import (
    AddressBalanceResponse,
    ErrorResponse,
    AddressBalanceResponseData,
    PriceFeedResponse,
    PriceFeedResponseData,
    InternalServerError,
)
from app.services.balances.blastup_balance import get_blastup_tokens_balance_for_chains

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/price-feed/{token}", response_model=PriceFeedResponse | ErrorResponse)
async def price_feed(redis: RedisDep, crypto: CryptoDep, token: str = Path()):
    try:
        if await redis.exists(f"price-feed:{token}"):
            data = json.loads(await redis.get(f"price-feed:{token}"))
        else:
            data = await crypto.get_price_feed(token.lower())
            await redis.setex(
                f"price-feed:{token}", value=json.dumps(data), time=timedelta(seconds=30)
            )

        return PriceFeedResponse(ok=True, data=PriceFeedResponseData(**data))
    except Exception as e:
        logger.error(f"Cannot get price_feed: {e}")
        return InternalServerError("Failed to get price feed")


@router.get("/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_address_balance(address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")):
    try:
        balances_by_chain_id = await get_blastup_tokens_balance_for_chains(address)
        return AddressBalanceResponse(
            ok=True,
            data=AddressBalanceResponseData(
                polygon=balances_by_chain_id[137],
                eth=balances_by_chain_id[1],
                bsc=balances_by_chain_id[56],
                blast=balances_by_chain_id[81457],
                total=sum(balances_by_chain_id.values()),
            ),
        )
    except Exception as e:
        logger.error(f"Cannot get balance for {address}: {e}")
        return InternalServerError("Failed to get user info")
