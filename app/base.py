import logging
from asyncio import current_task
from typing import Generic, TypeVar, Type
from uuid import UUID

from logtail import LogtailHandler
from sqlalchemy import BigInteger, select, func
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from .env import settings, LOG_LEVEL

if not settings.logtail_token:
    logger = logging.getLogger("app")
else:
    handler = LogtailHandler(source_token=settings.logtail_token)
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    logger.handlers = []
    logger.addHandler(handler)


engine = create_async_engine(str(settings.database_url), future=True, echo=False)
async_session = async_scoped_session(
    sessionmaker(engine, expire_on_commit=False, class_=AsyncSession),
    scopefunc=current_task,
)
Base = declarative_base()

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), "postgresql")
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), "sqlite")


Model = TypeVar("Model")


class BaseCrud(Generic[Model]):
    def __init__(self, session: AsyncSession, entity_type: Type[Model]) -> None:
        self.session = session
        self.entity_type = entity_type

    async def persist(self, model: Model, session: AsyncSession | None = None) -> Model:
        session = session or self.session

        if model.id is None:
            session.add(model)

        await session.flush()
        return model

    async def delete(self, model: Model) -> Model:
        await self.session.delete(model)
        await self.session.flush()
        return model

    async def find_by_id(self, id_: int | UUID) -> Model | None:
        query = await self.session.scalars(
            select(self.entity_type).where(self.entity_type.id == id_)
        )
        return query.one_or_none()

    async def count(self) -> int:
        query = select(func.count(self.entity_type.id))
        result = await self.session.execute(query)

        return int(result.scalar_one())
