from pydantic import BaseModel
from typing import Optional


class IncomeBase(BaseModel):
    title: str
    amount: float
    income_type: str = "freelance"
    date: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    income_type: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None


class IncomeResponse(IncomeBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
