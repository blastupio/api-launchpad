from datetime import datetime

from fastapi import Depends

from app.base import logger
from app.common import Command, CommandResult
from app.crud import LaunchpadProjectCrud
from app.dependencies import get_launchpad_projects_crud
from app.models import StatusProject, LaunchpadProject


class ChangeProjectsStatus(Command):
    _LIMIT: int = 1000

    async def command(
        self,
        crud: LaunchpadProjectCrud = Depends(get_launchpad_projects_crud),
    ) -> CommandResult:
        await self._process_ongoing(crud)
        await self._process_upcoming(crud)
        return CommandResult(success=True)

    async def _process_ongoing(self, crud: LaunchpadProjectCrud):
        for project in await crud.all(status=StatusProject.ONGOING, limit=self._LIMIT):
            await self._change_ongoing(crud, project)

    async def _process_upcoming(self, crud: LaunchpadProjectCrud):
        for project in await crud.all(status=StatusProject.UPCOMING, limit=self._LIMIT):
            await self._change_upcoming(crud, project)

    @staticmethod
    async def _change_ongoing(crud: LaunchpadProjectCrud, project: LaunchpadProject):
        if project.end_at <= datetime.utcnow():
            project.status = StatusProject.COMPLETED
            await crud.persist(project)
            logger.info(f"Project '{project.slug}' status changed ONGOING -> COMPLETED")

    @staticmethod
    async def _change_upcoming(crud: LaunchpadProjectCrud, project: LaunchpadProject):
        if project.start_at <= datetime.utcnow():
            project.status = StatusProject.ONGOING
            await crud.persist(project)
            logger.info(f"Project '{project.slug}' status changed UPCOMING -> ONGOING")
