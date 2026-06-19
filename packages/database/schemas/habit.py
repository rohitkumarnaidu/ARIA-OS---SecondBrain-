from pydantic import BaseModel
from typing import Optional, List


class HabitBase(BaseModel):
    name: str
    frequency: str = "daily"


class HabitCreate(HabitBase):
    custom_days: Optional[List[int]] = None
    time_target_minutes: Optional[int] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    frequency: Optional[str] = None
    time_target_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    id: str
    user_id: str
    is_active: bool
    time_target_minutes: Optional[int] = None
    current_streak: int = 0
    best_streak: int = 0
    consistency_percentage: float = 0

    class Config:
        from_attributes = True
