from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import TmpPointsHistory, TmpExtraPoints


class PointsHistoryCrud(BaseCrud[TmpPointsHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TmpPointsHistory)


class ExtraPointsCrud(BaseCrud[TmpExtraPoints]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TmpExtraPoints)

    async def get_or_create_with_lock(self, profile_id: int, project_id: str) -> TmpExtraPoints:
        model = await self.get_with_lock(profile_id, project_id)
        if not model:
            await self.persist(TmpExtraPoints(profile_id=profile_id, project_id=project_id))
            model = await self.get_with_lock(profile_id, project_id)

        return model

    async def get_with_lock(self, profile_id: int, project_id: str) -> TmpExtraPoints | None:
        query = await self.session.scalars(
            select(TmpExtraPoints)
            .where(
                and_(
                    TmpExtraPoints.profile_id == profile_id, TmpExtraPoints.project_id == project_id
                )
            )
            .with_for_update(of=TmpExtraPoints)
        )
        return query.first()

    async def get(self, profile_id: int, project_id: int) -> TmpExtraPoints | None:
        query = await self.session.scalars(
            select(TmpExtraPoints).where(
                and_(
                    TmpExtraPoints.profile_id == profile_id, TmpExtraPoints.project_id == project_id
                )
            )
        )
        return query.first()
