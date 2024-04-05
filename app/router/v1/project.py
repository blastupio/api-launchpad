from fastapi import APIRouter, Depends, Query
from typing import Union, Optional

from httpx import AsyncClient
from redis.asyncio import Redis
from starlette.responses import JSONResponse

from app.dependencies import get_launchpad_projects_crud, get_redis
from app.crud import LaunchpadProjectCrud
from app.models import StatusProject

from app.schema import AllLaunchpadProjectsResponse, LaunchpadProjectResponse, ErrorResponse
from app.utils import get_data_with_cache

router = APIRouter(prefix="/projects", tags=["launchpad projects"])


@router.get("/list", response_model=AllLaunchpadProjectsResponse)
async def list_launchpad_projects(
        status: Optional[StatusProject] = Query(None, description="Filter projects by status"),
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis)
):
    projects = await projects_crud.all_with_proxy(status=status)
    for project in projects:
        base_url = project.proxy_link.base_url

        async def get_proxy_data():
            async with AsyncClient(timeout=30.) as client:
                response = await client.get(f"{base_url}/crypto/total-balance")
                return response.json()

        total_balance = await get_data_with_cache(f"projects-list-raised-data:{project.slug}", get_proxy_data, redis)
        project.raised = total_balance.get("data", {}).get("usd", "0")

    return {
        "ok": True,
        "data": {
            "projects": projects
        }
    }


@router.get("/{id_or_slug}", response_model=LaunchpadProjectResponse | ErrorResponse)
async def retrieve_launchpad_project(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
        redis: Redis = Depends(get_redis)
):
    try:
        project = await projects_crud.retrieve(id_or_slug=id_or_slug)
        if not project:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "error": "Project does not exist"},
            )

        base_url = project.proxy_link.base_url

        async def get_proxy_data():
            async with AsyncClient(timeout=30.) as client:
                response = await client.get(f"{base_url}/crypto/total-balance")
                return response.json()

        total_balance = await get_data_with_cache(f"projects-list-raised-data:{project.slug}", get_proxy_data, redis)
        project.raised = total_balance.get("data", {}).get("usd")
    except Exception:
        return {"ok": False, "error": "Project does not exist"}

    return {
        "ok": True,
        "data": {
            "project": project
        }
    }
