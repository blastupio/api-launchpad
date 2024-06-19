from fastapi import APIRouter

from app.dependencies import HistoryBlpStakingCrudDep
from app.schema import BlpParticipantsCountResponse, ParticipantsCount
from app.tasks import add_blp_staking_points

router = APIRouter(prefix="/blp-staking", tags=["blp staking"])


@router.get("/participants-count", response_model=BlpParticipantsCountResponse)
async def get_participants_count(blp_crud: HistoryBlpStakingCrudDep):
    participants_count = await blp_crud.count_participants()
    return BlpParticipantsCountResponse(data=ParticipantsCount(total=participants_count))


@router.get("/test-add-blp-points")
async def test_add_blp_points():
    # todo: remove before prod
    add_blp_staking_points.apply_async()
