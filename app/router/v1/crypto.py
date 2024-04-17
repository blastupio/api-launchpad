import json
from datetime import timedelta

from fastapi import APIRouter, Path

from app.base import logger
from app.dependencies import RedisDep, CryptoDep
from app.schema import AddressBalanceResponse, ErrorResponse, AddressBalanceResponseData, PriceFeedResponse, \
    PriceFeedResponseData, InternalServerError
from app.utils import get_data_with_cache

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/price-feed/{token}", response_model=PriceFeedResponse | ErrorResponse)
async def price_feed(redis: RedisDep, crypto: CryptoDep, token: str = Path()):
    try:
        if await redis.exists(f"price-feed:{token}"):
            data = json.loads(await redis.get(f"price-feed:{token}"))
        else:
            data = await crypto.get_price_feed(token.lower())
            await redis.setex(f"price-feed:{token}", value=json.dumps(data), time=timedelta(seconds=30))

        return PriceFeedResponse(ok=True, data=PriceFeedResponseData(**data))
    except Exception as e:
        logger.error(f"Cannot get price_feed: {e}")
        return InternalServerError("Failed to get price feed")


@router.get("/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_address_balance(redis: RedisDep, crypto: CryptoDep, address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")):
    try:
        polygon = await get_data_with_cache(
            f"address-balance:polygon:{address}",
            lambda: crypto.get_token_balance("polygon", address),
            redis
        )
        eth = await get_data_with_cache(
            f"address-balance:eth:{address}",
            lambda: crypto.get_token_balance("eth", address),
            redis
        )
        bsc = await get_data_with_cache(
            f"address-balance:bsc:{address}",
            lambda: crypto.get_token_balance("bsc", address),
            redis
        )
        blast = await get_data_with_cache(
            f"address-balance:blast:{address}",
            lambda: crypto.get_token_balance("blast", address),
            redis
        )

        return AddressBalanceResponse(
            ok=True,
            data=AddressBalanceResponseData(
                polygon=int(polygon),
                eth=int(eth),
                bsc=int(bsc),
                blast=int(blast),
                total=int(polygon) + int(eth) + int(bsc) + int(blast)
            ))
    except Exception as e:
        logger.error(f"Cannot get address balance: {e}")
        return InternalServerError("Failed to get balance data")
