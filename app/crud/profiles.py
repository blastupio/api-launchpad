from sqlalchemy import select
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

    async def get_or_create_profile(self, address: str, points: int | None = None) -> TmpProfile:
        if (profile := await self.first_by_address(address)) is None:
            kwargs = {
                "address": address.lower(),
            }
            if points is not None:
                kwargs["points"] = points

            profile = await self.persist(TmpProfile(**kwargs))
        return profile

    async def get_by_id(self, id_: int, session: AsyncSession | None = None) -> TmpProfile | None:
        session = session or self.session
        query = await session.execute(select(TmpProfile).where(TmpProfile.id == id_))
        return query.scalars().one_or_none()
