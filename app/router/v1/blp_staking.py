from fastapi import APIRouter

from app.dependencies import HistoryBlpStakingCrudDep
from app.schema import BlpParticipantsCountResponse, ParticipantsCount

router = APIRouter(prefix="/blp-staking", tags=["blp staking"])


@router.get("/participants-count", response_model=BlpParticipantsCountResponse)
async def get_participants_count(blp_crud: HistoryBlpStakingCrudDep):
    participants_count = await blp_crud.count_participants()
    return BlpParticipantsCountResponse(data=ParticipantsCount(total=participants_count))
