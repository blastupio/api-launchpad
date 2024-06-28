from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import Transaction
from app.schema import CreateLaunchpadTransactionParams


class TransactionsCrud(BaseCrud[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def get_by_hash(self, txn_hash: str) -> Transaction | None:
        query = await self.session.execute(
            select(Transaction).where(Transaction.hash == txn_hash.lower()).limit(1)
        )
        return query.scalars().one_or_none()

    async def get_first_transaction(self, address: str) -> Transaction | None:
        query = await self.session.execute(
            select(Transaction)
            .where(Transaction.address == address.lower())
            .order_by(Transaction.created_at.asc())
            .limit(1)
        )
        return query.scalars().one_or_none()

    async def add_transaction(
        self, params: CreateLaunchpadTransactionParams, session: AsyncSession | None = None
    ) -> None:
        values = params.dict()
        values["user_address"] = values["user_address"].lower()
        if values.get("token_address"):
            values["token_address"] = values["token_address"].lower()
        if values.get("hash"):
            values["hash"] = values["hash"].lower()
        if values.get("payment_token_address"):
            values["payment_token_address"] = values["payment_token_address"].lower()
        st = (
            insert(Transaction)
            .values(values)
            .on_conflict_do_nothing(constraint="ux_transactions_txn_hash")
        )
        session = session or self.session
        await session.execute(st)
        await session.flush()
