from typing import Sequence

from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, contains_eager

from app.base import BaseCrud
from app.models import LaunchpadProject, StatusProject


class LaunchpadProjectCrud(BaseCrud):

    async def all(  # noqa
        self, limit: int = 100, offset: int = 0, status: StatusProject = None
    ) -> Sequence[LaunchpadProject]:
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(contains_eager(LaunchpadProject.proxy_link))
            .join(LaunchpadProject.proxy_link, isouter=True)
            .order_by(LaunchpadProject.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            st = st.where(LaunchpadProject.status == status)

        result = await self.session.scalars(st)

        return result.all()

    async def find_by_id_or_slug(self, id_or_slug: int | str):
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(selectinload(LaunchpadProject.token_details))
            .options(contains_eager(LaunchpadProject.proxy_link))
            .join(LaunchpadProject.proxy_link, isouter=True)
            .where(or_(LaunchpadProject.id == id_or_slug, LaunchpadProject.slug == id_or_slug))
        )
        query = await self.session.scalars(st)

        return query.first()
