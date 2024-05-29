from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from app.base import BaseCrud
from app.models import HistoryStake, HistoryStakeType
from app.schema import CreateHistoryStake


class HistoryStakingCrud(BaseCrud):
    async def add_history(self, params: CreateHistoryStake) -> None:
        values = params.dict()
        values["user_address"] = values["user_address"].lower()
        values["token_address"] = values["token_address"].lower()
        st = (
            insert(HistoryStake)
            .values(values)
            .on_conflict_do_nothing(constraint="ux_stake_history_txn_hash")
        )
        await self.session.execute(st)

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

    async def get_user_addresses_by_token_address(self) -> dict[str, list[str]]:
        stmt = (
            select(HistoryStake.token_address, func.array_agg(HistoryStake.user_address))
            .where(HistoryStake.type == HistoryStakeType.STAKE.value)
            .group_by(HistoryStake.token_address)
        )

        results = (await self.session.execute(stmt)).all()
        return dict(results)
