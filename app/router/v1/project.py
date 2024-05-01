from typing import Optional

from fastapi import APIRouter, Query
from httpx import AsyncClient

from app.dependencies import RedisDep, LaunchpadProjectCrudDep
from app.models import StatusProject
from app.schema import (
    AllLaunchpadProjectsResponse,
    LaunchpadProjectResponse,
    ErrorResponse,
    NotFoundError,
    InternalServerError,
    LaunchpadProject,
)
from app.utils import get_data_with_cache

router = APIRouter(prefix="/projects", tags=["launchpad projects"])


@router.get("/list", response_model=AllLaunchpadProjectsResponse)
async def list_launchpad_projects(
    projects_crud: LaunchpadProjectCrudDep,
    redis: RedisDep,
    status: Optional[StatusProject] = Query(None, description="Filter projects by status"),
):
    projects = await projects_crud.all(status=status)
    for project in projects:
        if project.proxy_link:

            async def get_proxy_data():
                async with AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{project.proxy_link.base_url}/crypto/total-balance"  # noqa
                    )
                    return response.json()

            total_balance = await get_data_with_cache(
                f"projects-list-raised-data:{project.slug}", get_proxy_data, redis
            )
            if total_balance:
                project.raised = total_balance.get("data", {}).get("usd", "0")

    return {"ok": True, "data": {"projects": projects}}


@router.get("/{id_or_slug}", response_model=LaunchpadProjectResponse | ErrorResponse)
async def retrieve_launchpad_project(
    id_or_slug: str | int, projects_crud: LaunchpadProjectCrudDep, redis: RedisDep
):
    try:
        project = await projects_crud.find_by_id_or_slug(id_or_slug=id_or_slug)
        if not project:
            return NotFoundError("Project does not exist")

        if project.proxy_link:
            base_url = project.proxy_link.base_url

            async def get_proxy_data():
                async with AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{base_url}/crypto/total-balance")
                    return response.json()

            total_balance = await get_data_with_cache(
                f"projects-list-raised-data:{project.slug}", get_proxy_data, redis
            )
            if total_balance:
                project.raised = total_balance.get("data", {}).get("usd")
    except Exception:
        return InternalServerError("Failed to get proxy data")
    return {"ok": True, "data": {"project": LaunchpadProject.parse_obj(project)}}
