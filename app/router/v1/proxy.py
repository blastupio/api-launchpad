import asyncio
from uuid import UUID

import httpx
from fastapi import APIRouter, Request, Path, Body

from app.base import logger
from app.dependencies import LaunchpadProjectCrudDep, RedisDep
from app.schema import (
    ProjectDataResponse,
    ErrorResponse,
    AddressBalanceResponse,
    SaveTransactionResponse,
    OnrampOrderRequest,
    SaveTransactionDataRequest,
    OnrampOrderResponse,
    NotFoundError,
)
from app.utils import get_data_with_cache

router = APIRouter(prefix="/proxy", tags=["proxy"])


async def fetch_data(api_url: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url)
        return response.json()


def get_ip_from_request(request: Request) -> str:
    try:
        ip = request.headers.get("cf-connecting-ip")
        if not ip:
            ip = request.headers.get("x-forwarded-for")
        if not ip:
            ip = request.client.host
    except Exception as e:
        raise RuntimeError("Cannot get ip from request: {}".format(e))
    return ip


@router.get("/{id_or_slug}/project-data", response_model=ProjectDataResponse | ErrorResponse)
async def get_project_data(
    id_or_slug: str | int, projects_crud: LaunchpadProjectCrudDep, redis: RedisDep
):
    async def get_proxy_data():
        try:
            project = await projects_crud.find_by_id_or_slug(id_or_slug)
            base_url = project.proxy_link.base_url
            tasks = [
                fetch_data(base_url + "/crypto/stages"),
                fetch_data(base_url + "/crypto/target"),
                fetch_data(base_url + "/crypto/contracts"),
                fetch_data(base_url + "/crypto/total-balance"),
                fetch_data(base_url + "/crypto/current-stage-v2?network=polygon"),
            ]
            responses = await asyncio.gather(*tasks)
            return responses
        except Exception as e:
            logger.info(f"Failed get project data: {e}")
            return None

    project_data = await get_data_with_cache(
        f"project-proxy-data:{id_or_slug}", get_proxy_data, redis
    )

    if not project_data:
        return NotFoundError("Project data does not exist")

    stages, target, contracts, total_balance, current_stage = project_data

    return {
        "ok": True,
        "data": {
            "stages": stages.get("data"),
            "target": target.get("data"),
            "contracts": contracts.get("data"),
            "total_balance": total_balance.get("data"),
            "current_stage": current_stage.get("data"),
        },
    }


@router.get(
    "/{id_or_slug}/{address}/balance", response_model=AddressBalanceResponse | ErrorResponse
)
async def get_balance(
    id_or_slug: str | int,
    projects_crud: LaunchpadProjectCrudDep,
    redis: RedisDep,
    address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
):
    async def get_proxy_data():
        project = await projects_crud.find_by_id_or_slug(id_or_slug)
        if not project:
            return None

        base_url = project.proxy_link.base_url

        try:
            return await fetch_data(base_url + f"/crypto/{address}/balance")
        except Exception:
            return None

    balance = await get_data_with_cache(
        f"project-proxy-data-balance:{id_or_slug}:{address}", get_proxy_data, redis
    )
    if not balance:
        return NotFoundError("Project does not exist")

    if not balance.get("data"):
        return {"ok": False, "error": f"No data received for balance: {balance}"}

    return {"ok": True, "data": balance.get("data")}


@router.post("/{id_or_slug}/transactions", response_model=SaveTransactionResponse | ErrorResponse)
async def save_transaction(
    request: Request,
    id_or_slug: str | int,
    projects_crud: LaunchpadProjectCrudDep,
    payload: SaveTransactionDataRequest = Body(embed=False),
):
    payload_json = payload.model_dump()
    payload_json["source"] = "launchpad"
    try:
        payload_json["ip"] = get_ip_from_request(request)
    except Exception:
        pass

    project = await projects_crud.find_by_id_or_slug(id_or_slug)
    if not project:
        return NotFoundError("Project does not exist")

    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{base_url}/users/transactions", json=payload_json)
        json_response = response.json()

    return json_response


@router.post("/{id_or_slug}/onramp/payment-link")
async def get_onramp_payment_link(
    request: Request,
    id_or_slug: str | int,
    projects_crud: LaunchpadProjectCrudDep,
    payload: OnrampOrderRequest = Body(embed=False),
):
    payload_json = payload.model_dump()
    try:
        payload_json["ip"] = get_ip_from_request(request)
    except Exception:
        pass
    payload_json["source"] = "launchpad"
    project = await projects_crud.find_by_id_or_slug(id_or_slug)
    if not project:
        return NotFoundError("Project does not exist")

    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{base_url}/onramp/payment-link", json=payload_json)
        json_response = response.json()

    return json_response


@router.get(
    "/{id_or_slug}/onramp/order/{order_id}", response_model=OnrampOrderResponse | ErrorResponse
)
async def get_onramp_order_status(
    id_or_slug: str | int, projects_crud: LaunchpadProjectCrudDep, order_id: UUID = Path()
):
    project = await projects_crud.find_by_id_or_slug(id_or_slug)
    if not project:
        return NotFoundError("Project does not exist")

    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(base_url + f"/onramp/order/{order_id}")
        json_response = response.json()

    return json_response
