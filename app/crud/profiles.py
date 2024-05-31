from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import Profile


class ProfilesCrud(BaseCrud):
    async def persist(self, profile: Profile) -> Profile:
        if profile.id is None:
            self.session.add(profile)

        await self.session.flush()
        return profile

    async def persist_with_id(self, profile: Profile) -> Profile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def first_by_address(self, address: str) -> Profile | None:
        query = await self.session.scalars(
            select(Profile).where(Profile.address == address.lower()).limit(1)
        )
        return query.first()

    async def get_or_create_profile(
        self, address: str, profile_id: int | None = None, points: int | None = None
    ) -> Profile:
        if (profile := await self.first_by_address(address)) is None:
            kwargs = {
                "address": address.lower(),
            }
            if points is not None:
                kwargs["points"] = points
            if profile_id is not None:
                kwargs["id"] = profile_id

            if profile_id is not None:
                profile = await self.persist_with_id(Profile(**kwargs))
            else:
                profile = await self.persist(Profile(**kwargs))
        return profile

    async def get_by_id(self, id_: int, session: AsyncSession | None = None) -> Profile | None:
        session = session or self.session
        query = await session.execute(select(Profile).where(Profile.id == id_))
        return query.scalars().one_or_none()
