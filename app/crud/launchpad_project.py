from decimal import Decimal, Context
from typing import Sequence

from sqlalchemy import select, or_, Row, case, update
from sqlalchemy.orm import selectinload, contains_eager

from app.base import BaseCrud
from app.models import LaunchpadProject, StatusProject, ProjectType
from app.types import ProjectIdWithRaised


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
            .where(LaunchpadProject.slug != "testpepe")
            .order_by(LaunchpadProject.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            st = st.where(LaunchpadProject.status == status)

        result = await self.session.scalars(st)

        return result.all()

    async def find_by_id_or_slug(self, id_or_slug: int | str) -> LaunchpadProject | None:
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

    async def get_data_for_total_raised_recalculating(self) -> Sequence[Row]:
        st = select(
            LaunchpadProject.id,
            LaunchpadProject.contract_project_id,
            LaunchpadProject.raise_goal_on_launchpad,
        ).where(LaunchpadProject.project_type == ProjectType.DEFAULT)
        result = await self.session.execute(st)
        return result.fetchall()

    async def update_raised_value(self, data: list[ProjectIdWithRaised]) -> None:
        # todo: update with one query
        for x in data:
            await self.session.execute(
                update(LaunchpadProject)
                .where(LaunchpadProject.id == x.project_id)
                .values(total_raised=str(x.raised))
            )
