import enum
from decimal import Decimal
from uuid import uuid4

import shortuuid
from sqlalchemy import Enum, CheckConstraint, UniqueConstraint
from sqlalchemy import (
    String,
    DECIMAL,
    ForeignKey,
    Column,
    UUID,
    Text,
    DateTime,
    func,
    JSON,
    text,
    Integer,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.base import Base, BigIntegerType


class HistoryStakeType(enum.Enum):
    UNSTAKE = "UNSTAKE"
    STAKE = "STAKE"
    CLAIM_REWARDS = "CLAIM_REWARDS"


class ProjectType(enum.Enum):
    DEFAULT = "default"
    PRIVATE_PRESALE = "private_presale"


class ProjectLinkType(enum.Enum):
    DEFAULT = "default"
    TWITTER = "twitter"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class StatusProject(enum.Enum):
    ONGOING = "ongoing"
    UPCOMING = "upcoming"
    COMPLETED = "completed"


ONRAMP_STATUS_NEW = "new"
ONRAMP_STATUS_COMPLETE = "complete"
ONRAMP_STATUS_ERROR = "error"


class LaunchpadProject(Base):
    __tablename__ = "launchpad_project"

    id = Column(String, primary_key=True, default=lambda: str(shortuuid.uuid()))  # noqa
    slug = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    short_description = Column(Text(), nullable=False)
    ticker = Column(String, nullable=True)
    is_active = Column(Boolean, server_default="false", default=False, nullable=True)

    logo_url = Column(Text(), nullable=True)

    description = Column(Text(), nullable=True)
    token_sale_details = Column(Text(), nullable=True)
    token_address = Column(String, nullable=True)

    contract_project_id = Column(BigIntegerType, nullable=True)

    approve_for_registration_is_required = Column(Boolean, nullable=True)
    kys_required = Column(Boolean, server_default="false", default=False, nullable=False)
    whitelist_required = Column(Boolean, server_default="false", default=False, nullable=False)

    badges = Column(JSONB(), server_default="{}", nullable=False)

    raise_goal = Column(DECIMAL, default=Decimal("0"), nullable=True)
    raise_goal_on_launchpad = Column(DECIMAL, default=Decimal("0"), nullable=True)
    total_raised = Column(DECIMAL, default=Decimal("0"), nullable=True)
    token_price = Column(DECIMAL, nullable=True)

    project_type = Column(Enum(ProjectType))
    status = Column(Enum(StatusProject))

    registration_start_at = Column(DateTime(), nullable=False)
    registration_end_at = Column(DateTime(), nullable=False)
    start_at = Column(DateTime(), nullable=False)
    end_at = Column(DateTime(), nullable=False)
    fcfs_opens_at = Column(DateTime(), nullable=False)
    points_reward_start_at = Column(DateTime(), nullable=True)
    points_reward_end_at = Column(DateTime(), nullable=True)

    created_at = Column(DateTime(), nullable=False, default=func.now())
    updated_at = Column(DateTime(), nullable=True)

    profile_images = relationship(
        "ProjectImage",
        back_populates="project",
        order_by="ProjectImage.ordering_key, ProjectImage.id",
    )
    links = relationship("ProjectLink", back_populates="project")
    proxy_link = relationship("ProxyLink", back_populates="project", uselist=False)
    token_details = relationship("TokenDetails", back_populates="project", uselist=False)
    whitelist_addresses = relationship("ProjectWhitelist", back_populates="project")

    @property
    def total_raise(self):
        return self.raise_goal


class ProjectImage(Base):
    __tablename__ = "project_image"

    id = Column(BigIntegerType, primary_key=True)  # noqa
    ordering_key = Column(Integer, nullable=True, index=True)

    title = Column(String, nullable=True)
    url = Column(String, nullable=False)

    project_id = Column(String, ForeignKey("launchpad_project.id"))
    project = relationship("LaunchpadProject", back_populates="profile_images")


class ProjectLink(Base):
    __tablename__ = "project_link"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    name = Column(String, nullable=True)
    url = Column(String, nullable=False)
    type = Column(  # noqa
        Enum(ProjectLinkType), default=ProjectLinkType.DEFAULT, server_default="DEFAULT"
    )

    project_id = Column(String, ForeignKey("launchpad_project.id"))
    project = relationship("LaunchpadProject", back_populates="links")


class OnRampOrder(Base):
    __tablename__ = "onramp_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)  # noqa
    address = Column(Text(), nullable=False, index=True)
    hash = Column(Text(), nullable=True, unique=True)  # noqa
    amount = Column(Text(), nullable=False)
    received_amount = Column(Text(), nullable=True)
    currency = Column(Text(), nullable=True)
    munzen_txn_hash = Column(Text(), nullable=True)
    status = Column(Text(), default=ONRAMP_STATUS_NEW, server_default=ONRAMP_STATUS_NEW)
    extra = Column(JSON(), default=lambda: {}, server_default=text("'{}'::jsonb"))

    created_at = Column(DateTime(), nullable=False, default=func.now())
    updated_at = Column(DateTime(), nullable=True)


class ProxyLink(Base):
    __tablename__ = "proxy_link"

    id = Column(BigIntegerType, primary_key=True)  # noqa
    project_id = Column(String, ForeignKey("launchpad_project.id"), nullable=False)
    base_url = Column(String, nullable=False)

    project = relationship("LaunchpadProject", back_populates="proxy_link")


class TokenDetails(Base):
    __tablename__ = "token_details"

    id = Column(String, primary_key=True, default=lambda: str(shortuuid.uuid()))  # noqa

    tge_date = Column(DateTime(), nullable=False)
    tge_percent = Column(Integer, nullable=False)
    cliff = Column(String, nullable=False)
    vesting = Column(String, nullable=False)
    icon = Column(String, nullable=True)

    ticker = Column(String, nullable=False)
    token_description = Column(String, nullable=False)
    total_supply = Column(Integer, nullable=False)
    initial_supply = Column(String, nullable=False)
    market_cap = Column(String, nullable=False)

    project_id = Column(String, ForeignKey("launchpad_project.id"), nullable=False)
    project = relationship("LaunchpadProject", back_populates="token_details")


class HistoryStake(Base):
    __tablename__ = "stake_history"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    type = Column(Enum(HistoryStakeType), nullable=False)  # noqa
    token_address = Column(String, nullable=False)
    chain_id = Column(String, nullable=False)
    amount = Column(Text(), nullable=False)
    user_address = Column(String, nullable=False, index=True)

    txn_hash = Column(String, unique=True, nullable=True)
    block_number = Column(BigIntegerType, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (CheckConstraint(amount >= 0, name="check_positive_amount"), {})


class ProjectWhitelist(Base):
    __tablename__ = "project_whitelist"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    user_address = Column(String, index=True, nullable=False)

    project_id = Column(String, ForeignKey("launchpad_project.id"), nullable=False)
    project = relationship("LaunchpadProject", back_populates="whitelist_addresses")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "user_address", name="uc_project_id_user_address"),
    )
