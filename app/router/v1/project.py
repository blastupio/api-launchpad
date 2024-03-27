from fastapi import APIRouter, Depends

from app.dependencies import get_launchpad_projects_crud
from app.crud import LaunchpadProjectCrud

from app.schema import AllLaunchpadProjectsResponse

router = APIRouter(prefix="/projects", tags=["launchpad projects"])


@router.get("/list", response_model=AllLaunchpadProjectsResponse)
async def list_launchpad_projects(
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud)
):

    return {
        "ok": True,
        "data": {
            "projects": await projects_crud.all()
        }
    }
