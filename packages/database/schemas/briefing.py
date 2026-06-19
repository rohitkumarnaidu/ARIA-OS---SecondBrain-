from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class BriefingRead(BaseModel):
    id: str
    user_id: str
    date: str
    title: Optional[str] = None
    summary: Optional[str] = None
    opening: Optional[str] = None
    top_priority: Optional[str] = None
    tasks_count: Optional[int] = None
    habits_streak: Optional[int] = None
    sleep_score: Optional[float] = None
    ai_insight: Optional[str] = None
    productivity_tip: Optional[str] = None
    focus_area: Optional[str] = None
    generated_by: Optional[str] = None
    read: bool = False
    raw_json: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BriefingListResponse(BaseModel):
    data: list[BriefingRead]
    count: int


class BriefingTriggerResponse(BaseModel):
    status: str
    message: str
