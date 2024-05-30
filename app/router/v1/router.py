from fastapi import APIRouter

from .project import router as project_router
from .crypto import router as crypto_router
from .proxy import router as proxy_router
from .ido import router as ido_router
from .info import router as info_router
from .staking import router as staking_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(project_router)
router.include_router(crypto_router)
router.include_router(proxy_router)
router.include_router(ido_router)
router.include_router(info_router)
router.include_router(staking_router)
router.include_router(users_router)
