from app.base import BaseCrud
from app.models import TmpPointsHistory


class PointsHistoryCrud(BaseCrud):
    async def persist(self, points_history: TmpPointsHistory) -> TmpPointsHistory:
        if points_history.id is None:
            self.session.add(points_history)

        await self.session.flush()
        return points_history
