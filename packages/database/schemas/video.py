from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class VideoCreate(BaseModel):
    url: str
    title: str
    thumbnail_url: Optional[str] = None
    ai_summary: Optional[str] = None
    status: str = "saved"


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ai_summary: Optional[str] = None
    status: Optional[str] = None


class VideoResponse(BaseModel):
    id: str
    user_id: str
    url: str
    title: str
    thumbnail_url: Optional[str] = None
    ai_summary: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
