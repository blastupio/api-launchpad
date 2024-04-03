from fastapi import APIRouter, Depends, Query
from typing import Union, Optional

from app.dependencies import get_launchpad_projects_crud
from app.crud import LaunchpadProjectCrud
from app.models import StatusProject

from app.schema import AllLaunchpadProjectsResponse, LaunchpadProjectResponse, ErrorResponse

router = APIRouter(prefix="/projects", tags=["launchpad projects"])


@router.get("/list", response_model=AllLaunchpadProjectsResponse)
async def list_launchpad_projects(
        status: Optional[StatusProject] = Query(None, description="Filter projects by status"),
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud)
):

    return {
        "ok": True,
        "data": {
            "projects": await projects_crud.all(status=status)
        }
    }


@router.get("/{id_or_slug}", response_model=LaunchpadProjectResponse | ErrorResponse)
async def retrieve_launchpad_project(
        id_or_slug: Union[str, int],
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud)
):

    try:
        project = await projects_crud.retrieve(id_or_slug=id_or_slug)
    except Exception:
        return {"ok": False, "error": "Project does not exist"}

    return {
        "ok": True,
        "data": {
            "project": project
        }
    }
