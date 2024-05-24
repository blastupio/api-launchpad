from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Literal, NewType, Any

import numpy as np
from fastapi_pagination import Page
from pydantic import BaseModel, Field, field_validator
from starlette.responses import JSONResponse

from app.models import HistoryStakeType, LaunchpadContractEventType, StatusProject
from app.types import BadgeType

Address = NewType("Address", str)

ChainId = NewType("ChainId", int)

RatesForChainAndToken = NewType("RatesForChainAndToken", dict[ChainId, dict[Address, float | None]])


class TokenInChain(BaseModel):
    address: Address = Field(pattern=r"0x[0-9a-fA-F]{40}")
    chain_id: ChainId


class Language(BaseModel):
    current: str | None = Field(default=None)
    all: list[str] = Field(default=[])  # noqa


class NotFoundError(JSONResponse):
    def __init__(self, err: str):
        super().__init__(content={"ok": False, "error": err}, status_code=404)


class InternalServerError(JSONResponse):
    def __init__(self, err: str):
        super().__init__(content={"ok": False, "error": err}, status_code=500)


class BaseResponse(BaseModel):
    ok: bool
    data: Dict


class FileModel(BaseModel):
    id: int  # noqa
    title: str
    url: str

    class Config:
        from_attributes = True


class ProjectLinkTypeEnum(str, Enum):
    DEFAULT = "default"
    TWITTER = "twitter"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class ProjectStatusEnum(str, Enum):
    ONGOING = "ongoing"
    UPCOMING = "upcoming"
    COMPLETED = "completed"


class LinkModel(BaseModel):
    name: str
    url: str
    type: ProjectLinkTypeEnum  # noqa

    class Config:
        from_attributes = True


class ProjectTypeEnum(str, Enum):
    DEFAULT = "default"
    PRIVATE_PRESALE = "private_presale"


class Badge(BaseModel):
    type: BadgeType  # noqa


class KybInfo(BaseModel):
    proof_of_identity: Any | None = None
    company_name: Any | None = None
    legal_form: Any | None = None

    jurisdiction: Any | None = None
    business_proof_file: Any | None = None
    register_entry_file: Any | None = None


class LaunchpadProjectList(BaseModel):
    id: str  # noqa
    slug: str
    name: str
    is_active: bool
    status: ProjectStatusEnum
    project_type: ProjectTypeEnum
    short_description: str
    logo_url: str | None
    links: List[LinkModel]
    token_price: Decimal
    raise_goal: Decimal
    total_raise: Decimal
    raise_goal_on_launchpad: Decimal | None
    total_raised: Decimal | None
    raised: str = "0"
    contract_project_id: int | None
    registration_end_at: datetime
    start_at: datetime
    end_at: datetime
    points_reward_start_at: datetime | None
    points_reward_end_at: datetime | None
    fcfs_opens_at: datetime
    badges: list[Badge] = Field(default_factory=list)

    kys_required: bool
    kyb_info: KybInfo | None
    whitelist_required: bool

    class Config:
        from_attributes = True

    @field_validator("badges", mode="before")
    @classmethod
    def check_badges_is_list(cls, value) -> list[Badge]:
        if value == {}:
            return []
        elif isinstance(value, (dict, Badge)):
            return [value]
        return value

    @field_validator("raise_goal")
    @classmethod
    def convert_raise_goal(cls, value):
        if value is None:
            return Decimal(0)
        return np.format_float_positional(value, trim="0")

    @field_validator("total_raise")
    @classmethod
    def convert_total_raise(cls, value):
        if value is None:
            return Decimal(0)
        return np.format_float_positional(value, trim="0")

    @field_validator("raise_goal_on_launchpad")
    @classmethod
    def convert_raise_goal_on_launchpad(cls, value):
        if value is None:
            return Decimal(0)
        return np.format_float_positional(value, trim="0")

    @field_validator("total_raised")
    @classmethod
    def convert_total_raised(cls, value):
        if value is None:
            return Decimal(0)
        return np.format_float_positional(value, trim="0")


class TokenDetailsData(BaseModel):
    icon: str
    tge_date: datetime
    tge_full_date: str | None
    tge_percent: int
    cliff: str
    vesting: str
    ticker: str
    token_description: str
    total_supply: int
    initial_supply: str
    market_cap: int


class LaunchpadProject(LaunchpadProjectList):
    ticker: str
    description: str | None

    created_at: datetime
    updated_at: datetime | None

    profile_images: List[FileModel]
    token_details: TokenDetailsData | None
    token_address: str | None
    approve_for_registration_is_required: bool | None

    seo_title: str | None
    seo_description: str | None

    claim_start_at: datetime | None
    claim_end_at: datetime | None

    urls: dict[str, Any] | None

    class Config:
        from_attributes = True


class LaunchpadProjectsData(BaseModel):
    projects: List[LaunchpadProjectList]


class LaunchpadProjectData(BaseModel):
    project: LaunchpadProject


class AllLaunchpadProjectsResponse(BaseResponse):
    data: LaunchpadProjectsData


class LaunchpadProjectResponse(BaseResponse):
    data: LaunchpadProjectData


class ErrorResponse(BaseModel):
    ok: bool = Field(default=False)
    error: str


class AddressBalanceResponseData(BaseModel):
    polygon: int
    eth: int
    bsc: int
    blast: int
    base: int | None
    total: int


class AddressBalanceResponse(BaseModel):
    ok: bool
    data: AddressBalanceResponseData


class PriceFeedResponseData(BaseModel):
    latest_answer: int = Field(alias="latestAnswer")
    decimals: int


class PriceFeedResponse(BaseModel):
    ok: bool
    data: PriceFeedResponseData


class CurrentStageData(BaseModel):
    stage: str
    target_amount: str
    current_amount: str
    current_amount_usd: str


class TotalBalanceAggData(BaseModel):
    usd: str
    token: str


class TargetData(BaseModel):
    target: int
    target_usd: int


class StagesData(BaseModel):
    price: str
    target: int
    target_usd: int


class ContractsData(BaseModel):
    environment: Literal["testnet", "mainnet"]
    contracts: dict[str, str]


class ProjectData(BaseModel):
    stages: Optional[list[StagesData]] = None
    target: Optional[TargetData] = None
    total_balance: Optional[TotalBalanceAggData] = None
    contracts: ContractsData
    current_stage: Optional[CurrentStageData] = None


class ProjectDataResponse(BaseModel):
    ok: bool
    data: ProjectData


class SaveTransactionDataRequest(BaseModel):
    tx_hash: str = Field(alias="tx_hash")
    utm: str | None = Field(default=None)
    language: Language | None = Field(default=None)
    wallet_address: str = Field(pattern="^(0x)[0-9a-fA-F]{40}$")
    chain: Literal["polygon", "ethereum", "bsc", "blast", "base"] = Field()
    currency: Literal["USDT", "USDC", "USDB", "BNB", "MATIC", "ETH"] = Field()
    amount: str = Field()
    first_login: str | None = Field(alias="first_login", default=None)
    ref_code: str | None = Field(alias="refCode", default=None)
    browser: str | None = Field(alias="browser", default=None)
    device_resolution: str | None = Field(alias="deviceResolution", default=None)
    device_type: str | None = Field(alias="deviceType", default=None)
    referrer: str | None = Field(default=None)


class SaveTransactionResponseData(BaseModel):
    transaction_id: str


class SaveTransactionResponse(BaseModel):
    ok: bool
    data: SaveTransactionResponseData


class OnrampOrderResponseData(BaseModel):
    order_id: str = Field(alias="orderId")
    blockchain_network_tx_id: str | None = Field(alias="blockchainNetworkTxId", default=None)
    merchant_order_id: str = Field(alias="merchantOrderId")
    customer_id: str = Field(alias="customerId")
    from_currency: str = Field(alias="fromCurrency")
    from_amount: float | int = Field(alias="fromAmount")
    from_amount_without_fees: float | int = Field(alias="fromAmountWithoutFees")
    to_currency: str = Field(alias="toCurrency")
    to_amount: float | int = Field(alias="toAmount")
    to_wallet: str = Field(alias="toWallet")
    exchange_rate: float | int = Field(alias="exchangeRate")
    provider_fee: float | int = Field(alias="providerFee")
    network_fee: float | int = Field(alias="networkFee")
    network_fee_fiat: float | int = Field(alias="networkFeeFiat")
    status: str
    created_at: str = Field(alias="createdAt")


class OnrampOrderResponse(BaseModel):
    ok: bool
    data: OnrampOrderResponseData


class OnrampOrderRequest(BaseModel):
    amount: str = Field()
    recipient: str = Field(pattern="^(0x)[0-9a-fA-F]{40}$")
    utm: str | None = Field(default=None)
    language: Language | None = Field(default=None)
    first_login: str = Field(alias="first_login")
    ref_code: str | None = Field(alias="refCode", default=None)
    browser: str | None = Field(alias="browser", default=None)
    device_resolution: str | None = Field(alias="deviceResolution", default=None)
    device_type: str | None = Field(alias="deviceType", default=None)
    referrer: str | None = Field(default=None)


class SignUserBalanceResponse(BaseModel):
    ok: bool = True
    error: str | None = None
    signature: str | None = None


class SignApprovedUserResponse(BaseModel):
    ok: bool = True
    error: str | None = None
    signature: str | None = None


class TierInfo(BaseModel):
    order: int
    title: str
    blp_amount: int


class TierInfoResponse(BaseModel):
    tiers: list[TierInfo]


class UserInfoResponse(BaseModel):
    tier: TierInfo | None = None
    blastup_balance: dict[ChainId, int] | None = None


class TokenPriceResponse(BaseModel):
    price: dict[Address, float]


class Any2AnyPriceResponse(BaseModel):
    rate: RatesForChainAndToken


class GetPointsData(BaseModel):
    points: int
    extra_points: int | None = None


class GetPointsResponse(BaseModel):
    ok: bool
    data: GetPointsData


class GetHistoryStake(BaseModel):
    id: int  # noqa
    type: HistoryStakeType  # noqa
    token_address: str
    amount: str
    chain_id: int
    txn_hash: str | None
    block_number: int | None
    user_address: str
    created_at: datetime


class CreateHistoryStake(BaseModel):
    type: HistoryStakeType  # noqa
    token_address: str
    amount: str
    chain_id: str
    txn_hash: str
    block_number: int
    user_address: str


class YieldPercentageResponse(BaseModel):
    native: float
    stablecoin: float


class CreateLaunchpadEvent(BaseModel):
    user_address: str
    token_address: str
    contract_project_id: int | None
    txn_hash: str
    block_number: int
    event_type: LaunchpadContractEventType
    extra: dict[Any, Any] = Field(default_factory=dict)


class UserProject(BaseModel):
    id: str  # noqa
    slug: str
    name: str
    logo_url: str | None
    contract_project_id: int | None
    status: StatusProject

    class Config:
        from_attributes = True


class GetUserProjectsResponse(BaseModel):
    data: Page[UserProject]
    ok: bool = True
    error: str | None = None
