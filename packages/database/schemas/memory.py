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


class BufferEntry(BaseModel):
    role: str
    content: str
    metadata: dict[str, Any] = {}
    timestamp: str = ""


class WorkingMemoryEntry(BaseModel):
    key: str
    value: Any
    ttl: int = 43200
    created_at: str = ""
    expires_at: str = ""


class EpisodicMemoryCreate(BaseModel):
    user_id: str
    session_id: str
    summary: str
    episodes: list[dict[str, Any]] = []
    importance: str = "medium"
    tags: list[str] = []


class EpisodicMemoryResponse(BaseModel):
    id: str
    user_id: str
    type: str = "episodic"
    key: str
    value: dict[str, Any]
    importance: str
    tags: list[str] = []
    created_at: str = ""
    updated_at: str = ""


class SemanticFact(BaseModel):
    user_id: str
    key: str
    value: str
    source: str = "inference"
    confidence: float = 0.8
    category: str = "general"
    tags: list[str] = []


class ProceduralPattern(BaseModel):
    user_id: str
    pattern_type: str
    data: dict[str, Any]
    confidence: float = 0.6
    observation_count: int = 1
    tags: list[str] = []
