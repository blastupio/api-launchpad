from sqlalchemy import select, Sequence, Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import BaseCrud
from app.models import SupportedTokens


class SupportedTokensCrud(BaseCrud[SupportedTokens]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SupportedTokens)

    async def get_supported_tokens(self) -> Sequence[Row]:
        st = select(SupportedTokens)
        result = (await self.session.scalars(st)).all()
        return result
