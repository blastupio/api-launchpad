from typing import Sequence, Union
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.base import BaseCrud
from app.models import LaunchpadProject


class LaunchpadProjectCrud(BaseCrud):

    async def all(self, limit: int = 100, offset: int = 0) -> Sequence[LaunchpadProject]:
        query = await self.session.execute(
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .order_by(LaunchpadProject.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return query.scalars().all()

    async def retrieve(self, id_or_slug: Union[int, str]):
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
        )

        st = st.where(LaunchpadProject.id == id_or_slug) if isinstance(id_or_slug, int) \
            else st.where(LaunchpadProject.slug == id_or_slug)
        query = await self.session.execute(st)
        return query.scalars().first()
