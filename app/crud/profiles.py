from sqlalchemy import select

from app.base import BaseCrud
from app.models import Profile


class ProfilesCrud(BaseCrud):
    async def persist(self, profile: Profile) -> Profile:
        if profile.id is None:
            self.session.add(profile)

        await self.session.flush()
        return profile

    async def first_by_address(self, address: str) -> Profile | None:
        query = await self.session.scalars(
            select(Profile).where(Profile.address == address.lower()).limit(1)
        )
        return query.first()

    async def get_or_create_profile(self, address: str, points: int | None = None) -> Profile:
        if (profile := await self.first_by_address(address)) is None:
            kwargs = {
                "address": address.lower(),
            }
            if points is not None:
                kwargs["points"] = points

            profile = await self.persist(Profile(**kwargs))
        return profile
