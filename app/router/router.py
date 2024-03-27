from fastapi import APIRouter

from .v1.router import router as v1router

router = APIRouter(prefix="/api")
router.include_router(v1router)
