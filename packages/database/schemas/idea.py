from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    market_research: Optional[str] = None
    competitors: Optional[str] = None


class IdeaResponse(IdeaBase):
    id: str
    user_id: str
    status: str
    market_research: Optional[str] = None
    competitors: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
