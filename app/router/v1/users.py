from fastapi import APIRouter, Path
from starlette.responses import JSONResponse

from app.base import logger
from app.dependencies import ProfileCrudDep
from app.env import settings
from app.router.v1.proxy import fetch_data
from app.schema import ProfileResponse, InternalServerError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile/{address}", response_model=ProfileResponse)
async def get_profile(
    profile_crud: ProfileCrudDep,
    address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
):
    if not (profile := await profile_crud.first_by_address(address)):
        return JSONResponse(content={"ok": False, "error": "Profile not found"}, status_code=404)

    url = f"{settings.presale_api_url}/users/profile/{address}"

    try:
        for _ in range(5):
            presale_data = await fetch_data(url, timeout=5)
            if presale_data["ok"]:
                break
            elif "not found" in presale_data["error"]:
                presale_data = {
                    "data": {"points": 0},
                    "ok": True,
                }
                break

    except Exception as e:
        logger.error(f"Can't get presale profile for {address}, {url=}: {e}")
        return InternalServerError(err="Can't get profile")

    presale_data["data"]["points"] += profile.points
    return presale_data
