from typing import Sequence, Any

from sqlalchemy import select, or_, Row, update, func
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from app.base import BaseCrud
from app.models import (
    LaunchpadProject,
    StatusProject,
    ProjectType,
    LaunchpadContractEvents,
    LaunchpadContractEventType,
    ProxyLink,
    TokenDetails,
)
from app.types import ProjectIdWithRaised


class LaunchpadProjectCrud(BaseCrud[LaunchpadProject]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LaunchpadProject)

    async def all(  # noqa
        self,
        limit: int = 100,
        offset: int = 0,
        status: StatusProject = None,
        project_type: ProjectType | None = None,
    ) -> Sequence[LaunchpadProject]:
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(contains_eager(LaunchpadProject.proxy_link))
            .join(LaunchpadProject.proxy_link, isouter=True)
            .where(LaunchpadProject.is_visible.is_(True))
            .order_by(LaunchpadProject.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            st = st.where(LaunchpadProject.status == status)
        if project_type:
            st = st.where(LaunchpadProject.project_type == project_type)

        result = await self.session.scalars(st)

        return result.all()

    async def find_by_id_or_slug(self, id_or_slug: int | str) -> LaunchpadProject | None:
        st = (
            select(LaunchpadProject)
            .options(selectinload(LaunchpadProject.profile_images))
            .options(selectinload(LaunchpadProject.links))
            .options(selectinload(LaunchpadProject.token_details))
            .options(contains_eager(LaunchpadProject.proxy_link))
            .options(selectinload(LaunchpadProject.access_token))
            .join(LaunchpadProject.proxy_link, isouter=True)
            .where(or_(LaunchpadProject.id == id_or_slug, LaunchpadProject.slug == id_or_slug))
        )
        query = await self.session.scalars(st)
        return query.first()

    async def find_by_contract_project_id(
        self, contract_project_id: int
    ) -> LaunchpadProject | None:
        st = select(LaunchpadProject).where(
            LaunchpadProject.contract_project_id == contract_project_id
        )
        query = await self.session.scalars(st)
        return query.first()

    async def get_data_for_total_raised_recalculating(self) -> Sequence[Row]:
        st = (
            select(
                LaunchpadProject.id,
                LaunchpadProject.contract_project_id,
                LaunchpadProject.raise_goal_on_launchpad,
                LaunchpadProject.project_type,
                ProxyLink.base_url,
            )
            .join(LaunchpadProject.proxy_link, isouter=True)
            .where(LaunchpadProject.is_visible.is_(True))
        )
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

    async def get_project_info_by_contract_project_id(
        self, conn: AsyncConnection
    ) -> dict[int, dict[str, Any]]:
        st = select(
            LaunchpadProject.contract_project_id,
            LaunchpadProject.name,
            LaunchpadProject.token_price,
        ).where(
            LaunchpadProject.project_type == ProjectType.DEFAULT,
            LaunchpadProject.contract_project_id.is_not(None),
            LaunchpadProject.is_visible.is_(True),
        )
        result = await conn.execute(st)
        return {
            row.contract_project_id: {"name": row.name, "price": row.token_price}
            for row in result.fetchall()
        }

    async def get_info_for_user_projects(self) -> Sequence[Row]:
        # todo: cache
        st = (
            select(
                LaunchpadProject.id,
                LaunchpadProject.contract_project_id,
                LaunchpadProject.project_type,
                ProxyLink.base_url,
            )
            .join(LaunchpadProject.proxy_link, isouter=True)
            .where(LaunchpadProject.is_visible.is_(True))
        )
        result = await self.session.execute(st)
        return result.fetchall()

    async def get_projects_by_ids(
        self, project_ids: list[int], page: int, size: int
    ) -> Sequence[Row]:
        offset = (page - 1) * size
        st = (
            select(
                LaunchpadProject.id,
                LaunchpadProject.name,
                LaunchpadProject.logo_url,
                LaunchpadProject.contract_project_id,
                LaunchpadProject.slug,
                LaunchpadProject.project_type,
                LaunchpadProject.status,
                TokenDetails.tge_date,
                TokenDetails.tge_percent,
                TokenDetails.ticker,
                TokenDetails.vesting_start,
                TokenDetails.vesting_end,
            )
            .join(LaunchpadProject.token_details, isouter=True)
            .where(LaunchpadProject.id.in_(project_ids))
            .order_by(LaunchpadProject.created_at.desc())
            .limit(size)
            .offset(offset)
        )
        return (await self.session.execute(st)).all()

    async def get_user_project_ids_from_events(
        self, user_address: str, page: int, size: int
    ) -> tuple[Sequence[Row], int]:
        offset = (page - 1) * size
        general_st = (
            select(LaunchpadProject.id)
            .join(
                LaunchpadContractEvents,
                LaunchpadProject.contract_project_id == LaunchpadContractEvents.contract_project_id,
            )
            .where(
                LaunchpadContractEvents.user_address == user_address.lower(),
                LaunchpadContractEvents.event_type == LaunchpadContractEventType.USER_REGISTERED,
            )
            .order_by(LaunchpadProject.created_at.desc())
        )
        paginated_st = general_st.limit(size).offset(offset)
        count_st = select(func.count()).select_from(general_st)
        count: int = await self.session.scalar(count_st)
        project_ids = (await self.session.scalars(paginated_st)).all()
        return project_ids, count
