from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TimeEntryCreate(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = "work"


class TimeEntryUpdate(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None


class TimeEntryResponse(BaseModel):
    id: str
    user_id: str
    task_id: Optional[str]
    project_id: Optional[str]
    start_time: str
    end_time: Optional[str]
    duration_minutes: Optional[int]
    description: Optional[str]
    category: str
    created_at: str
