from math import ceil

from fastapi import APIRouter, Path, Query
from fastapi_pagination import Page

from app.dependencies import HistoryStakingCrudDep
from app.schema import GetHistoryStake, UserTvlIdoFarmingResponse
from app.services.ido_staking.tvl import get_user_usd_tvl

router = APIRouter(prefix="/staking", tags=["staking"])


@router.get("/history/{user_address}")
async def get_staking_history(
    history_staking_crud: HistoryStakingCrudDep,
    user_address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=30, ge=3, le=30),
) -> Page[GetHistoryStake]:
    total_rows = await history_staking_crud.history_count(user_address=user_address)
    history = await history_staking_crud.get_history(
        user_address=user_address, page=page, size=size
    )

    total_pages = ceil(total_rows / size)
    return Page(total=total_rows, page=page, size=size, items=history, pages=total_pages)


@router.get("/tvl/{user_address}", response_model=UserTvlIdoFarmingResponse)
async def get_tvl_ido_farming(
    user_address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
) -> UserTvlIdoFarmingResponse:
    user_usd_tvl = await get_user_usd_tvl(user_address=user_address)
    if user_usd_tvl is None:
        return UserTvlIdoFarmingResponse(error="Internal Error")
    return UserTvlIdoFarmingResponse(data=user_usd_tvl)
