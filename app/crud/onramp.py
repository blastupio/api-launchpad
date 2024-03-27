from datetime import datetime

from sqlalchemy import UUID, select, update, and_

from app.base import BaseCrud
from app.models import OnRampOrder


class OnRampCrud(BaseCrud):
    async def get_by_id(self, id_: UUID) -> OnRampOrder | None:
        query = await self.session.execute(select(OnRampOrder).where(OnRampOrder.id == id_))
        return query.scalars().one_or_none()

    async def persist(self, entity: OnRampOrder) -> OnRampOrder:
        if entity.id:
            return await self._update(entity)

        entity.address = entity.address.lower()
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def _update(self, entity: OnRampOrder) -> OnRampOrder:
        query = (
            update(OnRampOrder)
            .where(and_(OnRampOrder.id == entity.id))
            .values(
                address=entity.address.lower() if entity.address else entity.address,
                hash=entity.hash.lower() if entity.hash else entity.hash,
                amount=entity.amount,
                currency=entity.currency,
                status=entity.status,
                updated_at=datetime.utcnow(),
            )
        )

        await self.session.execute(query)
        await self.session.flush()
        return entity
