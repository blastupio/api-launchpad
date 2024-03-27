from fastapi import APIRouter, Depends

from app.dependencies import get_launchpad_projects_crud
from app.crud import LaunchpadProjectCrud

router = APIRouter(prefix="/projects", tags=["launchpad projects"])


@router.get("/list", response_model=None)
async def list_launchpad_projects(
        projects_crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud)
):

    return {
        "ok": True,
        "data": {
            "projects": await projects_crud.all()
        }
    }
