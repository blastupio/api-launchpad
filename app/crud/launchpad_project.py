from typing import Sequence, Union

from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload, contains_eager

from app.base import BaseCrud
from app.models import LaunchpadProject, StatusProject, ProxyLink


class LaunchpadProjectCrud(BaseCrud):

    async def all_with_proxy(self, limit: int = 100, offset: int = 0, status: StatusProject = None) -> \
            Sequence[LaunchpadProject]:
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(contains_eager(LaunchpadProject.proxy_link))
            .join(LaunchpadProject.proxy_link)
            .order_by(LaunchpadProject.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            st = st.where(LaunchpadProject.status == status)

        result = await self.session.execute(st)

        return result.scalars().all()

    async def retrieve(self, id_or_slug: Union[int, str]):
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(joinedload(LaunchpadProject.proxy_link))
            .options(selectinload(LaunchpadProject.token_details))
            .where(ProxyLink.id != None)
            .where(or_(LaunchpadProject.id == id_or_slug, LaunchpadProject.slug == id_or_slug))
        )

        query = await self.session.execute(st)

        return query.scalars().first()
