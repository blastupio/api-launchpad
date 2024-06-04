from sqlalchemy import select

from app.base import BaseCrud
from app.models import Refcode
from app.services.refcodes import generate_code


class RefcodesCrud(BaseCrud[Refcode]):
    async def get_by_address(self, address: str) -> Refcode | None:
        query = await self.session.scalars(
            select(Refcode).where(Refcode.address == address.lower()).limit(1)
        )
        return query.first()

    async def get_by_refcode(self, refcode: str) -> Refcode | None:
        query = await self.session.execute(
            select(Refcode).where(Refcode.refcode == refcode).limit(1)
        )
        return query.scalars().one_or_none()

    async def generate_refcode_if_not_exists(self, address: str) -> Refcode:
        if (refcode := await self.get_by_address(address)) is None:
            while True:
                code = generate_code()
                if not await self.get_by_refcode(code):
                    break
            refcode = await self.persist(Refcode(address=address.lower(), refcode=code))
        return refcode
