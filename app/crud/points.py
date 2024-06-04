from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import PointsHistory, ExtraPoints


class PointsHistoryCrud(BaseCrud[PointsHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PointsHistory)


class ExtraPointsCrud(BaseCrud[ExtraPoints]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ExtraPoints)

    async def get_or_create_with_lock(
        self, profile_id: int, project_id: str, session: AsyncSession | None
    ) -> ExtraPoints:
        session = session or self.session
        model = await self.get_with_lock(profile_id, project_id, session=session)
        if not model:
            await self.persist(
                ExtraPoints(profile_id=profile_id, project_id=project_id), session=session
            )
            model = await self.get_with_lock(profile_id, project_id, session=session)

        return model

    async def get_with_lock(
        self, profile_id: int, project_id: str, session: AsyncSession | None
    ) -> ExtraPoints | None:
        session = session or self.session
        query = await session.scalars(
            select(ExtraPoints)
            .where(and_(ExtraPoints.profile_id == profile_id, ExtraPoints.project_id == project_id))
            .with_for_update()
        )
        return query.first()

    async def get(self, profile_id: int, project_id: int) -> ExtraPoints | None:
        query = await self.session.scalars(
            select(ExtraPoints).where(
                and_(ExtraPoints.profile_id == profile_id, ExtraPoints.project_id == project_id)
            )
        )
        return query.first()
