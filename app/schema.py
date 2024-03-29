from pydantic import BaseModel, Field
from typing import Dict, List
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


class LinkModel(BaseModel):
    name: str
    url: str

    class Config:
        orm_mode = True


class ProjectTypeEnum(str, Enum):
    DEFAULT = 'default'
    PARTNERSHIP_PRESALE = "partnership_presale"


class LaunchpadProjectList(BaseModel):
    id: int
    slug: str
    name: str
    short_description: str
    links: List[LinkModel]
    token_price: Decimal
    total_raise: Decimal
    raised: str = "0"
    registration_end_at: datetime

    class Config:
        orm_mode = True


class LaunchpadProject(LaunchpadProjectList):

    registration_end_at: datetime
    start_at: datetime
    end_at: datetime
    fcfs_opens_at: datetime

    project_type: ProjectTypeEnum

    created_at: datetime
    updated_at: datetime

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
