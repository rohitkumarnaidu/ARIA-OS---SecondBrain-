from pydantic import BaseModel
from typing import Optional


class CourseBase(BaseModel):
    title: str
    platform: Optional[str] = None
    url: Optional[str] = None
    instructor: Optional[str] = None
    total_hours: Optional[int] = None
    hours_completed: int = 0
    progress: int = 0
    notes: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    instructor: Optional[str] = None
    total_hours: Optional[int] = None
    hours_completed: Optional[int] = None
    progress: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(CourseBase):
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
