from pydantic import BaseModel
from typing import Optional


class SleepBase(BaseModel):
    bedtime: Optional[str] = None
    wake_time: Optional[str] = None
    hours_slept: Optional[float] = None
    quality: int = 50
    notes: Optional[str] = None


class SleepCreate(SleepBase):
    pass


class SleepUpdate(BaseModel):
    bedtime: Optional[str] = None
    wake_time: Optional[str] = None
    hours_slept: Optional[float] = None
    quality: Optional[int] = None
    notes: Optional[str] = None


class SleepResponse(SleepBase):
    id: str
    user_id: str
    date: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
