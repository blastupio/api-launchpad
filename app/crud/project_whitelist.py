from sqlalchemy import select, exists

from app.base import BaseCrud
from app.models import ProjectWhitelist


class ProjectWhitelistCrud(BaseCrud):
    async def user_is_in_whitelist(self, project_id: str, user_address: str) -> bool:
        exists_stmt = exists().where(
            (ProjectWhitelist.project_id == project_id)
            & (ProjectWhitelist.user_address == user_address)
        )
        st = select(exists_stmt)
        return await self.session.scalar(st)
