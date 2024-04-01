from fastapi import APIRouter, Path, Depends, Query

from typing import Union

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.get("/{id_or_slug}/stages")
async def get_stages(id_or_slug: Union[str, int]):
    pass


@router.get("/{id_or_slug}/target")
async def get_target(id_or_slug: Union[str, int]):
    pass


@router.get("/{id_or_slug}/total-balance")
async def get_total_balance(id_or_slug: Union[str, int]):
    pass


@router.get("/{id_or_slug}/current-stage-v2")
async def get_current_stage_v2(id_or_slug: Union[str, int], network: str = Query()):
    pass


@router.get("/{id_or_slug}/{address}/balance")
async def get_balance(
        id_or_slug: Union[str, int],
        address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")
):
    pass
