import logging
from asyncio import current_task

from logtail import LogtailHandler
from sqlalchemy import BigInteger
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


class BaseCrud:
    def __init__(self, session: AsyncSession):
        self.session = session
