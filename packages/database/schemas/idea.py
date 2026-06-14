from pydantic import BaseModel
from typing import Optional


class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "general"
    tags: Optional[list] = []
    notes: Optional[str] = None


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class IdeaResponse(IdeaBase):
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
