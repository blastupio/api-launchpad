from fastapi import APIRouter, Path

from app.schema import BlastBoxResponse

router = APIRouter(prefix="/blastboxes", tags=["BlastBoxes"])


@router.get("/{token_id}", response_model=BlastBoxResponse)
async def blastbox_info_by_token_id(token_id: int = Path(ge=1, le=9999)):
    info = {
        "description": f"BlastBox #{token_id}",
        "external_url": f"https://app-api.blastup.io/v1/blastboxes/{token_id}",
        "image": "https://blastup.ams3.cdn.digitaloceanspaces.com/blastbox-nft-v1.png",
        "name": f"BlastBox #{token_id}",
    }
    return info
