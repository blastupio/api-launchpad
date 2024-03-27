from pydantic import BaseModel
from typing import Dict, List

from datetime import datetime


class BaseResponse(BaseModel):
    ok: bool
    data: Dict


class File(BaseModel):
    id: int
    title: str
    url: str

    class Config:
        orm_mode = True


class LaunchpadProject(BaseModel):
    id: int
    name: str
    short_description: str
    token_price: str
    total_raise: str

    registration_start_at: datetime
    registration_end_at: datetime
    start_at: datetime
    end_at: datetime
    fcfs_opens_at: datetime

    created_at: datetime
    updated_at: datetime

    profile_images: List[File]

    class Config:
        orm_mode = True


class LaunchpadProjectsData(BaseModel):
    projects: List[LaunchpadProject]


class AllLaunchpadProjectsResponse(BaseResponse):
    data: LaunchpadProjectsData
