import enum
from decimal import Decimal
from uuid import uuid4

import shortuuid
from sqlalchemy import Enum, CheckConstraint, UniqueConstraint, Index
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


class HistoryBlpStakeType(enum.Enum):
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


class LaunchpadContractEventType(enum.Enum):
    TOKENS_BOUGHT = "tokens_bought"
    USER_REGISTERED = "user_registered"


class OperationType(enum.Enum):
    ADD = "add"
    ADD_REF = "add_ref"
    ADD_REF_BONUS = "add_ref_bonus"
    ADD_SYNC = "add_sync"
    ADD_REF_SYNC = "add_ref_sync"
    ADD_EXTRA = "add_extra"
    ADD_MANUAL = "add_manual"
    ADD_IDO_POINTS = "add_ido_points"
    ADD_BLP_STAKING_POINTS = "add_blp_staking_points"


class OperationReason(str, enum.Enum):
    ERR_COMPENSATION = "err_compensation"
    BLASTBOX = "blastbox"
    OTHER_GIVEAWAY = "other_giveaway"
    IDO_FARMING = "ido_farming"
    BLP_STAKING = "blp_staking"
    BLASTBOX_BUY = "blastbox_buy"


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

    seo_title = Column(Text(), nullable=True)
    seo_description = Column(Text(), nullable=True)

    kyb_info = Column(JSON(), nullable=True)
    urls = Column(JSON(), nullable=True)

    registration_start_at = Column(DateTime(), nullable=False)
    registration_end_at = Column(DateTime(), nullable=False)
    start_at = Column(DateTime(), nullable=False)
    end_at = Column(DateTime(), nullable=False)
    fcfs_opens_at = Column(DateTime(), nullable=False)
    points_reward_start_at = Column(DateTime(), nullable=True)
    points_reward_end_at = Column(DateTime(), nullable=True)

    claim_start_at = Column(DateTime(), nullable=True)
    claim_end_at = Column(DateTime(), nullable=True)

    is_visible = Column(Boolean, server_default="true", default=True, nullable=False, index=True)

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
    access_token = relationship("ProjectAccessToken", back_populates="project", uselist=False)

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
    munzen_order_id = Column(Text(), nullable=True)
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
    tge_full_date = Column(String, nullable=True)
    tge_percent = Column(Integer, nullable=False)
    cliff = Column(String, nullable=False)

    vesting = Column(String, nullable=False)
    vesting_start = Column(DateTime(), nullable=True)
    vesting_end = Column(DateTime(), nullable=True)

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


class LaunchpadContractEvents(Base):
    __tablename__ = "launchpad_contract_events"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    event_type = Column(Enum(LaunchpadContractEventType), nullable=False)
    user_address = Column(String, index=True, nullable=False)
    token_address = Column(String, nullable=False)

    contract_project_id = Column(BigIntegerType, nullable=True)
    extra = Column(JSON, default={}, server_default=text("'{}'::json"))
    txn_hash = Column(String, unique=True, nullable=False)
    block_number = Column(BigIntegerType, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index(
            "_user_contract_event_uc",
            "user_address",
            "contract_project_id",
            "event_type",
            unique=True,
            postgresql_where=(event_type == "USER_REGISTERED"),
        ),
    )


class SupportedTokens(Base):
    __tablename__ = "supported_tokens"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    token_address = Column(String, nullable=False)
    chain_id = Column(BigIntegerType, nullable=False)

    __table_args__ = (
        UniqueConstraint("token_address", "chain_id", name="uc_token_address_chain_id"),
    )


class ProjectAccessToken(Base):
    __tablename__ = "project_access_token"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    token = Column(Text, nullable=False)

    project_id = Column(String, ForeignKey("launchpad_project.id"), nullable=False)
    project = relationship("LaunchpadProject", back_populates="access_token")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(BigIntegerType, primary_key=True)  # noqa
    # todo: add foreign key to profiles.address
    address = Column(Text(), nullable=False, index=True, unique=True)
    referrer = Column(Text(), index=True, nullable=True)

    utm = Column(Text(), nullable=True)
    language = Column(Text(), nullable=True)
    first_login = Column(DateTime, nullable=True)
    browser = Column(Text(), nullable=True)
    terms_accepted = Column(Boolean, default=False, nullable=False)

    points = Column(DECIMAL(10, 2), default=0, server_default=text("0::decimal"))
    ref_points = Column(DECIMAL(10, 2), default=0, server_default=text("0::decimal"))
    ref_percent = Column(Integer, default=20, server_default=text("20::int"))
    ref_bonus_used = Column(Boolean, default=False, server_default="false", nullable=False)


class PointsHistory(Base):
    __tablename__ = "points_history"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    operation_type = Column(
        Enum(OperationType),
        default=OperationType.ADD,
        nullable=False,
    )
    # use for add_manual operation
    operation_reason = Column(Enum(OperationReason), nullable=True)

    points_before = Column(
        DECIMAL(10, 2), default=0, server_default=text("0::decimal"), nullable=False
    )
    amount = Column(DECIMAL(10, 2), default=0, server_default=text("0::decimal"), nullable=False)
    points_after = Column(
        DECIMAL(10, 2), default=0, server_default=text("0::decimal"), nullable=False
    )

    created_at = Column(DateTime(), nullable=False, default=func.now())

    # for this profile ref_points are awarded
    referring_profile_id = Column(ForeignKey("profiles.id"), nullable=True)

    profile_id = Column(ForeignKey("profiles.id"), nullable=False)
    project_id = Column(ForeignKey("launchpad_project.id"), nullable=True)


class ExtraPoints(Base):
    __tablename__ = "extra_points"

    id = Column(BigIntegerType, primary_key=True)  # noqa
    profile_id = Column(BigIntegerType, ForeignKey("profiles.id"), nullable=False)
    project_id = Column(String(), ForeignKey("launchpad_project.id"), nullable=False)

    points = Column(DECIMAL(10, 2), default=0, server_default=text("0::decimal"), nullable=False)

    created_at = Column(DateTime(), nullable=False, default=func.now())
    updated_at = Column(DateTime(), default=func.now(), onupdate=func.now())

    __table_args__ = tuple(  # noqa
        [Index("idx_extra_points_profile_id_project_id", "profile_id", "project_id", unique=True)]
    )


class Refcode(Base):
    __tablename__ = "refcodes"

    id = Column(BigIntegerType, primary_key=True)  # noqa
    address = Column(Text(), nullable=False, index=True)
    refcode = Column(Text(), nullable=False, index=True)


class HistoryBlpStake(Base):
    __tablename__ = "stake_blp_history"

    id = Column(BigIntegerType, primary_key=True)  # noqa

    type = Column(Enum(HistoryBlpStakeType), nullable=False)  # noqa
    amount = Column(Text(), nullable=False)
    user_address = Column(String, nullable=False, index=True)
    pool_id = Column(Integer, nullable=False)

    chain_id = Column(String, nullable=False)
    txn_hash = Column(String, unique=True, nullable=True)
    block_number = Column(BigIntegerType, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
