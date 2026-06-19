from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class WeeklyReviewRead(BaseModel):
    id: str
    user_id: str
    week_start: str
    week_end: str
    summary: Optional[str] = None
    tasks_completed: Optional[int] = None
    tasks_added: Optional[int] = None
    habits_consistency: Optional[float] = None
    focus_hours: Optional[float] = None
    highlights: Optional[list[str]] = None
    challenges: Optional[list[str]] = None
    next_week_focus: Optional[list[str]] = None
    ai_insights: Optional[str] = None
    mood_trend: Optional[str] = None
    generated_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyReviewListResponse(BaseModel):
    data: list[WeeklyReviewRead]
    count: int
