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

    async def get_or_create_with_lock(
        self, profile_id: int, project_id: str, session: AsyncSession | None
    ) -> TmpExtraPoints:
        session = session or self.session
        model = await self.get_with_lock(profile_id, project_id, session=session)
        if not model:
            await self.persist(
                TmpExtraPoints(profile_id=profile_id, project_id=project_id), session=session
            )
            model = await self.get_with_lock(profile_id, project_id, session=session)

        return model

    async def get_with_lock(
        self, profile_id: int, project_id: str, session: AsyncSession | None
    ) -> TmpExtraPoints | None:
        session = session or self.session
        query = await session.scalars(
            select(TmpExtraPoints)
            .where(
                and_(
                    TmpExtraPoints.profile_id == profile_id, TmpExtraPoints.project_id == project_id
                )
            )
            .with_for_update()
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
