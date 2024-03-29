import json

from fastapi import APIRouter, Path, Depends
from starlette.responses import JSONResponse
from redis.asyncio import Redis
from datetime import timedelta

from app.schema import AddressBalanceResponse, ErrorResponse, AddressBalanceResponseData, PriceFeedResponse, \
    PriceFeedResponseData
from app.services import Crypto
from app.base import logger
from app.dependencies import get_redis, get_launchpad_crypto

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/price-feed/{token}", response_model=PriceFeedResponse | ErrorResponse)
async def price_feed(redis: Redis = Depends(get_redis), crypto: Crypto = Depends(get_launchpad_crypto),
                     token: str = Path()):
    try:
        if await redis.exists(f"price-feed:{token}"):
            data = json.loads(await redis.get(f"price-feed:{token}"))
        else:
            data = await crypto.get_price_feed(token.lower())
            await redis.setex(f"price-feed:{token}", value=json.dumps(data), time=timedelta(seconds=30))

        return PriceFeedResponse(ok=True,
                                 data=PriceFeedResponseData(**data))
    except Exception as e:
        logger.error(f"Cannot get price_feed: {e}")
        return JSONResponse({"ok": False, "error": "Internal Server Error"}, status_code=500)


@router.get("/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_address_balance(
    address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
    redis: Redis = Depends(get_redis),
    crypto: Crypto = Depends(get_launchpad_crypto)
):
    async def get_data(network: str, address_: str):
        if await redis.exists(f"address-balance:{network}:{address_}"):
            return await redis.get(f"address-balance:{network}:{address_}")
        else:
            try:
                data = await crypto.get_token_balance(network, address_)
                await redis.setex(f"address-balance:{network}:{address_}", value=data,
                                  time=timedelta(seconds=30))
                await redis.setex(f"address-balance:{network}:{address_}:long", value=data,
                                  time=timedelta(minutes=20))
                return data
            except Exception as exec:
                return await redis.get(f"address-balance:{network}:{address_}:long")

    try:
        polygon = await get_data("polygon", address)
        eth = await get_data("eth", address)
        bsc = await get_data("bsc", address)
        blast = await get_data("blast", address)

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
        return JSONResponse({"ok": False, "error": "Internal Server Error"}, status_code=500)
