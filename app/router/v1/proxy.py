from fastapi import APIRouter, Path, Depends, Query

from typing import Union

from app.schema import ProjectDataResponse, ErrorResponse, AddressBalanceResponse

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.get("/{id_or_slug}/project-data", response_model=ProjectDataResponse | ErrorResponse)
async def get_project_data(id_or_slug: Union[str, int], network: str = Query()):
    pass


@router.get("/{id_or_slug}/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_balance(
        id_or_slug: Union[str, int],
        address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")
):
    pass
