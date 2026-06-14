from pydantic import BaseModel
from typing import Optional


class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None
    frequency: str = "daily"
    target_streak: int = 30
    current_streak: int = 0
    best_streak: int = 0


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    target_streak: Optional[int] = None
    current_streak: Optional[int] = None
    best_streak: Optional[int] = None
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    id: str
    user_id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
