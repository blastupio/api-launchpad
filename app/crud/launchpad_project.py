from typing import Sequence
from sqlalchemy import select
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
