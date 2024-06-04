from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import TmpProfile


class ProfilesCrud(BaseCrud[TmpProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TmpProfile)

    async def first_by_address(self, address: str) -> TmpProfile | None:
        query = await self.session.scalars(
            select(TmpProfile).where(TmpProfile.address == address.lower()).limit(1)
        )
        return query.first()

    async def first_by_address_or_fail_with_lock(
        self, address: str, session: AsyncSession | None
    ) -> TmpProfile | None:
        session = session or self.session
        query = await session.scalars(
            select(TmpProfile).where(TmpProfile.address == address.lower()).with_for_update()
        )
        return query.one()

    async def get_or_create_profile(
        self, address: str, points: int | None = None, referrer: str | None = None
    ) -> TmpProfile:
        if (profile := await self.first_by_address(address)) is None:
            kwargs = {
                "address": address.lower(),
            }
            if points is not None:
                kwargs["points"] = points
            if referrer is not None:
                kwargs["referrer"] = referrer.lower()

            profile = await self.persist(TmpProfile(**kwargs))
        return profile

    async def get_by_id(self, id_: int, session: AsyncSession | None = None) -> TmpProfile | None:
        session = session or self.session
        query = await session.execute(select(TmpProfile).where(TmpProfile.id == id_))
        return query.scalars().one_or_none()

    async def count_referrals(self, referrer: str) -> int:
        """Get the number of referrals for a given referrer"""
        query = await self.session.execute(
            select(func.count(TmpProfile.id)).where(TmpProfile.referrer == referrer.lower())
        )
        return int(query.scalars().one_or_none())

    async def update_referrer(self, address: str, referrer: str) -> None:
        await self.session.execute(
            update(TmpProfile)
            .where(TmpProfile.address == address.lower())
            .values(referrer=referrer.lower())
        )

    async def get_leaderboard_rank(self, profile_points: int) -> int:
        query = await self.session.execute(
            select(func.count(TmpProfile.id)).where(TmpProfile.points > profile_points)
        )
        return int(query.scalars().one_or_none()) + 1
