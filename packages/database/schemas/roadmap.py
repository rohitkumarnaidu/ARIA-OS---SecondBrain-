from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class RoadmapMilestoneCreate(BaseModel):
    skill: str
    category: str
    target_date: Optional[str] = None
    progress: float = 0.0
    status: str = "not_started"
    is_recommended: bool = False


class RoadmapMilestoneUpdate(BaseModel):
    skill: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[str] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    is_recommended: Optional[bool] = None


class RoadmapMilestoneResponse(BaseModel):
    id: str
    user_id: str
    skill: str
    category: str
    target_date: Optional[str] = None
    progress: float
    status: str
    is_recommended: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
