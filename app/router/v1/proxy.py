import asyncio
from typing import Union
from uuid import UUID

import httpx
from fastapi import APIRouter, Request, Path, Depends, Body
from redis.asyncio import Redis

from app.crud import LaunchpadProjectCrud
from app.dependencies import get_launchpad_projects_crud, get_redis
from app.models import LaunchpadProject
from app.schema import ProjectDataResponse, ErrorResponse, AddressBalanceResponse, SaveTransactionResponse, \
    OnrampOrderResponseData, OnrampOrderRequest
from app.utils import get_data_with_cache
from app.base import logger

router = APIRouter(prefix="/proxy", tags=["proxy"])


async def fetch_data(api_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        return response.json()


def get_ip_from_request(request: Request) -> str:
    try:
        ip = request.headers.get('cf-connecting-ip')
        if not ip:
            ip = request.headers.get('x-forwarded-for')
        if not ip:
            ip = request.client.host
    except Exception as e:
        raise RuntimeError("Cannot get ip from request: {}".format(e))
    return ip


@router.get("/{id_or_slug}/project-data", response_model=ProjectDataResponse | ErrorResponse)
async def get_project_data(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis)
):
    async def get_proxy_data():
        try:
            project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
            base_url = project.proxy_link.base_url
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
            logger.info(f"Failed get project data: {exec}")
            return None

    project_data = await get_data_with_cache(
        f"project-proxy-data:{id_or_slug}",
        get_proxy_data,
        redis
    )
    if not project_data:
        return {"ok": False, "data": {
            "stages": {},
            "target": {},
            "contracts": {},
            "total_balance": {},
            "current_stage": {}
        }}
    stages, target, contracts, total_balance, current_stage = project_data

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
            base_url = project.proxy_link.base_url
            return await fetch_data(base_url + f"/crypto/{address}/balance")
        except Exception as exec:
            return {}

    balance = await get_data_with_cache(
        f"project-proxy-data-balance:{id_or_slug}:{address}",
        get_proxy_data,
        redis
    )

    return {"ok": True, "data": balance.get('data')}


@router.post("/{id_or_slug}/transactions", response_model=SaveTransactionResponse | ErrorResponse)
async def save_transaction(
        request: Request,
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        payload: dict = Body(embed=False)
):
    payload["source"] = "launchpad"
    try:
        payload["ip"] = get_ip_from_request(request)
    except:
        pass

    project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient() as client:
        response = await client.post(base_url + f"/users/transactions", json=payload)
        json_response = response.json()

    if not json_response.get("ok"):
        return json_response

    return {"ok": True, "data": json_response.get("data")}


@router.post("/{id_or_slug}/onramp/payment-link")
async def get_onramp_payment_link(
        request: Request,
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        payload: OnrampOrderRequest = Body(embed=False)
):
    payload_json = payload.model_dump()
    try:
        payload_json["ip"] = get_ip_from_request(request)
    except:
        pass
    payload_json["source"] = "launchpad"
    project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient() as client:
        response = await client.post(base_url + f"/onramp/payment-link", json=payload_json)
        json_response = response.json()

    return json_response


@router.get("/{id_or_slug}/onramp/order/{order_id}", response_model=OnrampOrderResponseData | ErrorResponse)
async def get_onramp_order_status(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        order_id: UUID = Path()
):
    project: LaunchpadProject = await projects_crud.retrieve(id_or_slug=id_or_slug)
    base_url = project.proxy_link.base_url

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url + f"/onramp/order/{order_id}")
        json_response = response.json()

    return json_response
