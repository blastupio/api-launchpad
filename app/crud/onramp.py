from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import OnRampOrder


class OnRampCrud(BaseCrud[OnRampOrder]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OnRampOrder)

    async def persist(self, model: OnRampOrder, session: AsyncSession | None = None) -> OnRampOrder:
        model.address = model.address.lower()
        return await super().persist(model, session)
