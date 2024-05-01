from sqlalchemy import select, func

from app.base import BaseCrud
from app.models import HistoryStake


class HistoryStakingCrud(BaseCrud):
    async def get_history(self, user_address: str, page: int, size: int):
        offset = (page - 1) * size
        st = (
            select(HistoryStake)
            .where(HistoryStake.user_address == user_address.lower())
            .order_by(HistoryStake.created_at.desc())
            .limit(size)
            .offset(offset)
        )
        result = (await self.session.scalars(st)).all()
        return result

    async def history_count(self, user_address: str) -> int:
        # todo: cache it
        query = (
            select(func.count())
            .where(HistoryStake.user_address == user_address.lower())
            .select_from(HistoryStake)
        )
        count: int = await self.session.scalar(query)
        return count
