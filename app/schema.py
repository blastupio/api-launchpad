from pydantic import BaseModel, Field
from typing import Dict, List, Union, Optional
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
    short_description: str
    logo_url: str | None
    links: List[LinkModel]
    token_price: Decimal
    total_raise: Decimal
    raised: str = "0"
    registration_end_at: datetime

    class Config:
        orm_mode = True


class LaunchpadProject(LaunchpadProjectList):
    ticker: str
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


class ProjectData(BaseModel):
    stages: Optional[list[StagesData]] = None
    target: Optional[TargetData] = None
    total_balance: Optional[TotalBalanceAggData] = None
    current_stage: Optional[CurrentStageData] = None


class ProjectDataResponse(BaseModel):
    ok: bool
    data: ProjectData
