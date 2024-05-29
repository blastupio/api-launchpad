from app.base import BaseCrud
from app.models import PointsHistory


class PointsHistoryCrud(BaseCrud):
    async def persist(self, points_history: PointsHistory) -> PointsHistory:
        if points_history.id is None:
            self.session.add(points_history)

        await self.session.flush()
        return points_history
