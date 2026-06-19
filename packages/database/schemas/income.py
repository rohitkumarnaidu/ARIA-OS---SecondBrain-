from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class IncomeBase(BaseModel):
    source_type: str
    amount: float
    platform: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    hours_spent: Optional[float] = None


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    source_type: Optional[str] = None
    amount: Optional[float] = None
    platform: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    hours_spent: Optional[float] = None


class IncomeResponse(IncomeBase):
    id: str
    user_id: str
    effective_hourly_rate: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
