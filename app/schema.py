from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Literal
from enum import Enum
from decimal import Decimal

from datetime import datetime


class BaseResponse(BaseModel):
    ok: bool
    data: Dict


class FileModel(BaseModel):
    id: int
    title: str
    url: str

    class Config:
        orm_mode = True


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
    type: ProjectLinkTypeEnum

    class Config:
        orm_mode = True


class ProjectTypeEnum(str, Enum):
    DEFAULT = 'default'
    PARTNERSHIP_PRESALE = "partnership_presale"


class LaunchpadProjectList(BaseModel):
    id: str
    slug: str
    name: str
    is_active: bool
    status: ProjectStatusEnum
    short_description: str
    logo_url: str | None
    links: List[LinkModel]
    token_price: Decimal
    total_raise: Decimal
    raised: str = "0"
    registration_end_at: datetime

    @field_validator('total_raise')
    @classmethod
    def convert_total_raise(cls, value):
        if isinstance(value, Decimal):
            return str(int(value))
        return str(int(value))

    class Config:
        orm_mode = True


class TokenDetailsData(BaseModel):
    icon: str
    tge_date: datetime
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
    description: str
    start_at: datetime
    end_at: datetime
    points_reward_start_at: datetime
    points_reward_end_at: datetime
    fcfs_opens_at: datetime

    project_type: ProjectTypeEnum

    created_at: datetime
    updated_at: datetime | None

    profile_images: List[FileModel]
    links: List[LinkModel]
    token_details: TokenDetailsData

    class Config:
        orm_mode = True


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


class Language(BaseModel):
    current: str | None = Field(default=None)
    all: list[str] = Field(default=[])


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
