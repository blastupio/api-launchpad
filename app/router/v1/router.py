from fastapi import APIRouter

from .project import router as project_router

router = APIRouter(prefix="/v1")
router.include_router(project_router)
