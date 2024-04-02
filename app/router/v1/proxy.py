import httpx
import asyncio
from fastapi import APIRouter, Path, Depends, Query

from typing import Union

from app.dependencies import get_launchpad_projects_crud
from app.crud import LaunchpadProjectCrud
from app.models import LaunchpadProject
from app.schema import ProjectDataResponse, ErrorResponse, AddressBalanceResponse

router = APIRouter(prefix="/proxy", tags=["proxy"])


async def fetch_data(api_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        return response.json()


@router.get("/{id_or_slug}/project-data", response_model=ProjectDataResponse | ErrorResponse)
async def get_project_data(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud)
):
    try:
        project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)

        base_url = project.base_proxy_url[0].base_url

        tasks = [
            fetch_data(base_url + '/crypto/stages'),
            fetch_data(base_url + '/crypto/target'),
            fetch_data(base_url + '/crypto/total-balance'),
            fetch_data(base_url + f'/crypto/current-stage-v2?network=polygon')
        ]
        responses = await asyncio.gather(*tasks)
        stages, target, total_balance, current_stage = responses
    except Exception as exec:
        return ErrorResponse(error=str(exec))

    default_error = "Some unexpected error"

    return {
        "result": True,
        "data": {
            "stages": stages.get("data") or stages.get("error") or default_error,
            "target": target.get("data") or target.get("error") or default_error,
            "total_balance": total_balance.get("data") or total_balance.get("error") or default_error,
            "current_stage": current_stage.get("data") or current_stage.get("error") or default_error
        }
    }


@router.get("/{id_or_slug}/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_balance(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")
):
    try:
        project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)

        base_url = project.base_proxy_url[0].base_url
        balance = await fetch_data(base_url + f"/{address}/balance")
    except Exception as exec:
        return ErrorResponse(error=str(exec))

    return {"result": True, "data": balance}
