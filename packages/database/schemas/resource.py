from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class ResourceBase(BaseModel):
    title: str
    url: str
    resource_type: str = "article"
    tags: Optional[list] = []
    notes: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None
    tags: Optional[list] = None
    notes: Optional[str] = None
    is_archived: Optional[bool] = None


class ResourceResponse(ResourceBase):
    id: str
    user_id: str
    is_archived: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
