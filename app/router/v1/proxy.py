import asyncio
from typing import Union

import httpx
from fastapi import APIRouter, Path, Depends
from redis.asyncio import Redis

from app.crud import LaunchpadProjectCrud
from app.dependencies import get_launchpad_projects_crud, get_redis
from app.models import LaunchpadProject
from app.schema import ProjectDataResponse, ErrorResponse, AddressBalanceResponse
from app.utils import get_data_with_cache

router = APIRouter(prefix="/proxy", tags=["proxy"])


async def fetch_data(api_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        return response.json()


@router.get("/{id_or_slug}/project-data", response_model=ProjectDataResponse | ErrorResponse)
async def get_project_data(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis)
):
    async def get_proxy_data():
        try:
            project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
            base_url = project.base_proxy_url[0].base_url
            tasks = [
                fetch_data(base_url + '/crypto/stages'),
                fetch_data(base_url + '/crypto/target'),
                fetch_data(base_url + '/crypto/contracts'),
                fetch_data(base_url + '/crypto/total-balance'),
                fetch_data(base_url + f'/crypto/current-stage-v2?network=polygon')
            ]
            responses = await asyncio.gather(*tasks)
            return responses
        except Exception as exec:
            return {}, {}, {}, {}, {}

    stages, target, contracts, total_balance, current_stage = await get_data_with_cache(
        f"project-proxy-data:{id_or_slug}",
        get_proxy_data,
        redis
    )

    return {
        "ok": True,
        "data": {
            "stages": stages.get("data"),
            "target": target.get("data"),
            "contracts": contracts.get("data"),
            "total_balance": total_balance.get("data"),
            "current_stage": current_stage.get("data")
        }
    }


@router.get("/{id_or_slug}/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse)
async def get_balance(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis),
        address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$")
):
    async def get_proxy_data():
        try:
            project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
            base_url = project.base_proxy_url[0].base_url
            return await fetch_data(base_url + f"/crypto/{address}/balance")
        except Exception as exec:
            return {}

    balance = await get_data_with_cache(
        f"project-proxy-data-balance:{id_or_slug}:{address}",
        get_proxy_data,
        redis
    )

    return {"ok": True, "data": balance.get('data')}
