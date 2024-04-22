from fastapi import APIRouter, Path

from app.schema import TierInfoResponse, UserInfoResponse

router = APIRouter(prefix="/info", tags=["info"])


@router.get("/user/{address}", response_model=UserInfoResponse)
async def get_user_info(
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    )
):
    return {}


@router.get("/tiers", response_model=TierInfoResponse)
async def get_all_tiers():
    # todo: remove hardcode
    return {
        "tiers": [
            {
                "order": 1,
                "title": "Bronze",
                "blp_amount": 2000,
            },
            {
                "order": 2,
                "title": "Silver",
                "blp_amount": 5000,
            },
            {
                "order": 3,
                "title": "Gold",
                "blp_amount": 10_000,
            },
            {
                "order": 4,
                "title": "Titanium",
                "blp_amount": 20_000,
            },
            {
                "order": 5,
                "title": "Platinum",
                "blp_amount": 50_000,
            },
            {
                "order": 6,
                "title": "Diamond",
                "blp_amount": 150_000,
            },
        ]
    }
