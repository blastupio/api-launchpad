from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import Profile


class ProfilesCrud(BaseCrud[Profile]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Profile)

    async def first_by_address(self, address: str) -> Profile | None:
        query = await self.session.scalars(
            select(Profile).where(Profile.address == address.lower()).limit(1)
        )
        return query.first()

    async def first_by_address_or_fail_with_lock(
        self, address: str, session: AsyncSession | None
    ) -> Profile | None:
        session = session or self.session
        query = await session.scalars(
            select(Profile).where(Profile.address == address.lower()).with_for_update()
        )
        return query.one()

    async def get_or_create_profile(
        self, address: str, points: int | None = None, referrer: str | None = None
    ) -> Profile:
        if (profile := await self.first_by_address(address)) is None:
            kwargs = {
                "address": address.lower(),
            }
            if points is not None:
                kwargs["points"] = points
            if referrer is not None:
                kwargs["referrer"] = referrer.lower()

            profile = await self.persist(Profile(**kwargs))
        return profile

    async def get_by_id(self, id_: int, session: AsyncSession | None = None) -> Profile | None:
        session = session or self.session
        query = await session.execute(select(Profile).where(Profile.id == id_))
        return query.scalars().one_or_none()

    async def count_referrals(self, referrer: str) -> int:
        """Get the number of referrals for a given referrer"""
        query = await self.session.execute(
            select(func.count(Profile.id)).where(Profile.referrer == referrer.lower())
        )
        return int(query.scalars().one_or_none())

    async def update_referrer(self, address: str, referrer: str) -> None:
        await self.session.execute(
            update(Profile)
            .where(Profile.address == address.lower())
            .values(referrer=referrer.lower())
        )
