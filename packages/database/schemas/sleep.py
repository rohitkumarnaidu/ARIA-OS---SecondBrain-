from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class SleepBase(BaseModel):
    bedtime: str
    wake_time: str
    quality_rating: int


class SleepCreate(SleepBase):
    pass


class SleepUpdate(BaseModel):
    bedtime: Optional[str] = None
    wake_time: Optional[str] = None
    quality_rating: Optional[int] = None


class SleepResponse(SleepBase):
    id: str
    user_id: str
    duration_hours: float = 0.0
    sleep_score: int = 0
    sleep_debt: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True
