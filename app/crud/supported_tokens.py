from sqlalchemy import select, Sequence, Row

from app.base import BaseCrud
from app.models import SupportedTokens


class SupportedTokensCrud(BaseCrud):
    async def get_supported_tokens(self) -> Sequence[Row]:
        st = select(SupportedTokens)
        result = (await self.session.scalars(st)).all()
        return result
