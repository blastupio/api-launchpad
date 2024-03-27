from uuid import uuid4

from sqlalchemy import Column, UUID, Text, DateTime, func, JSON, text

from app.base import Base


ONRAMP_STATUS_NEW = "new"
ONRAMP_STATUS_COMPLETE = "complete"
ONRAMP_STATUS_ERROR = "error"


class OnRampOrder(Base):
    __tablename__ = 'onramp_orders'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    address = Column(Text(), nullable=False, index=True)
    hash = Column(Text(), nullable=True, unique=True)
    amount = Column(Text(), nullable=False)
    currency = Column(Text(), nullable=True)
    status = Column(Text(), default=ONRAMP_STATUS_NEW, server_default=ONRAMP_STATUS_NEW)
    extra = Column(JSON(), default=lambda: {}, server_default=text("'{}'::jsonb"))

    created_at = Column(DateTime(), nullable=False, default=func.now())
    updated_at = Column(DateTime(), nullable=True)
