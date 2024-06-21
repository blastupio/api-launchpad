from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import HistoryBlpStake, HistoryBlpStakeType
from app.schema import CreateBlpHistoryStake


class HistoryBlpStakingCrud(BaseCrud[HistoryBlpStake]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HistoryBlpStake)

    async def add_history(self, params: CreateBlpHistoryStake) -> None:
        values = params.dict()
        values["user_address"] = values["user_address"].lower()
        st = (
            insert(HistoryBlpStake)
            .values(values)
            .on_conflict_do_nothing(constraint="ux_stake_blp_history_txn_hash")
        )
        await self.session.execute(st)

    async def count_participants(self) -> int:
        query = select(
            func.count(func.distinct(HistoryBlpStake.user_address)).label("unique_user_count")
        ).where(HistoryBlpStake.type == HistoryBlpStakeType.STAKE)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def get_user_address_by_pool_id(self) -> dict[int, list[str]]:
        stmt = (
            select(
                HistoryBlpStake.pool_id, func.array_agg(func.distinct(HistoryBlpStake.user_address))
            )
            .where(HistoryBlpStake.type == HistoryBlpStakeType.STAKE.value)
            .group_by(HistoryBlpStake.pool_id)
        )

        results = (await self.session.execute(stmt)).all()
        return dict(results)
