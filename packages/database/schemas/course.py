from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class CourseBase(BaseModel):
    title: str
    platform: str
    url: Optional[str] = None
    total_videos: Optional[int] = 0
    deadline: Optional[str] = None
    why_enrolled: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    total_videos: Optional[int] = None
    completed_videos: Optional[int] = None
    deadline: Optional[str] = None
    why_enrolled: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(CourseBase):
    id: str
    user_id: str
    completed_videos: int = 0
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
