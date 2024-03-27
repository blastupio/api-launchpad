from pydantic import BaseModel
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


class LaunchpadProject(BaseModel):
    id: int
    name: str
    short_description: str
    token_price: Decimal
    total_raise: Decimal
    raised: str = "0"

    registration_start_at: datetime
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
    projects: List[LaunchpadProject]


class AllLaunchpadProjectsResponse(BaseResponse):
    data: LaunchpadProjectsData
