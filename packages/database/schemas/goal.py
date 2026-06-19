from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    roadmap_type: str = "career_skills"
    target_date: Optional[str] = None
    hours_per_day: float = 2.0
    days_per_week: float = 5.0
    intensity: str = "medium"
    category: Optional[str] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    roadmap_type: Optional[str] = None
    target_date: Optional[str] = None
    hours_per_day: Optional[float] = None
    days_per_week: Optional[float] = None
    intensity: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    category: Optional[str] = None


class GoalResponse(GoalBase):
    id: str
    user_id: str
    status: str
    progress: int
    created_at: datetime

    class Config:
        from_attributes = True
