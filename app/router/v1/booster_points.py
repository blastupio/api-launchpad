from fastapi import Depends, Path
from redis.asyncio import Redis

from app import router
from app.dependencies import get_launchpad_crypto, get_redis
from app.schema import GetBoosterPointsResponse, ErrorResponse
from app.services import Crypto
from app.utils import get_data_with_cache


@router.get("/{address}/{?project_id_or_slug}", response_model=GetBoosterPointsResponse | ErrorResponse)
async def get_booster_points(
        address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
        redis: Redis = Depends(get_redis),
        crypto: Crypto = Depends(get_launchpad_crypto),
        project_id_or_slug: str | int | None = None
):
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
        return JSONResponse({"ok": False, "error": "Internal Server Error"}, status_code=500)
