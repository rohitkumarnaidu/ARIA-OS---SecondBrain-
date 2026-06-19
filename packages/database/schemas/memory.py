from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any


class MemoryCreate(BaseModel):
    type: str
    key: str
    value: Any
    importance: str = "medium"
    tags: Optional[list[str]] = None
    expires_at: Optional[str] = None


class MemoryUpdate(BaseModel):
    type: Optional[str] = None
    key: Optional[str] = None
    value: Optional[Any] = None
    importance: Optional[str] = None
    tags: Optional[list[str]] = None


class MemoryResponse(BaseModel):
    id: str
    user_id: str
    type: str
    key: str
    value: Any
    importance: str
    tags: Optional[list[str]] = None
    expires_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
