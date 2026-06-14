from pydantic import BaseModel
from typing import Optional


class ResourceBase(BaseModel):
    title: str
    url: str
    resource_type: str = "article"
    description: Optional[str] = None
    tags: Optional[list] = []
    notes: Optional[str] = None
    is_favorite: bool = False


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


class ResourceResponse(ResourceBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
