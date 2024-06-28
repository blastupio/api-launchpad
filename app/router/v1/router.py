from fastapi import APIRouter

from .project import router as project_router
from .crypto import router as crypto_router
from .proxy import router as proxy_router
from .ido import router as ido_router
from .info import router as info_router
from .staking import router as staking_router
from .blp_staking import router as blp_staking_router
from .points import router as points_router
from .blastboxes import router as blastboxes_router
from .transactions import router as transactions_router

router = APIRouter(prefix="/v1")
router.include_router(project_router)
router.include_router(crypto_router)
router.include_router(proxy_router)
router.include_router(ido_router)
router.include_router(info_router)
router.include_router(staking_router)
router.include_router(points_router)
router.include_router(blp_staking_router)
router.include_router(blastboxes_router)
router.include_router(transactions_router)
