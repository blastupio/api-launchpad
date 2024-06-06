import json
from datetime import datetime
import dateutil.parser as dt

from sqlalchemy import select, func, update, desc
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

    async def get_or_create_profile(self, address: str, **kwargs) -> tuple[Profile, bool]:
        is_new = False
        if (profile := await self.first_by_address(address)) is None:
            is_new = True
            data = {"address": address.lower()}
            if first_login := kwargs.get("first_login"):
                data["first_login"] = dt.parse(first_login.split("(")[0]).replace(tzinfo=None)
            else:
                data["first_login"] = datetime.utcnow()

            if utm := kwargs.get("utm"):
                data["utm"] = utm
            if browser := kwargs.get("browser"):
                data["browser"] = browser
            if points := kwargs.get("points"):
                data["points"] = points
            if referrer := kwargs.get("referrer"):
                data["referrer"] = referrer.lower()
            if language := kwargs.get("language"):
                data["language"] = json.dumps(
                    {
                        "current": language.current,
                        "all": language.all,
                    }
                )

            profile = await self.persist(Profile(**data))
        return profile, is_new

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

    async def get_leaderboard_rank(self, user_address: str) -> int:
        subquery = select(
            Profile.address, func.dense_rank().over(order_by=desc(Profile.points)).label("rank")
        ).subquery()

        rank_query = select(subquery.c.rank).where(subquery.c.address == user_address.lower())

        result = await self.session.execute(rank_query)
        rank = result.scalars().one_or_none()
        return rank or 0
