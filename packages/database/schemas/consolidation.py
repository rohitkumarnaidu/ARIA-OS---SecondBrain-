from pydantic import BaseModel
from typing import Optional, Any, List


class MemoryToCreate(BaseModel):
    type: str
    key: str
    value: Any
    importance: str = "medium"
    tags: Optional[List[str]] = None


class MemoryToUpdate(BaseModel):
    id: str
    updates: dict


class MemoryToDiscard(BaseModel):
    id: str
    reason: str


class ConsolidationResult(BaseModel):
    consolidation_type: str
    memories_created: int
    memories_updated: int
    memories_discarded: int
    patterns_detected: int
    summary: str
    details: Optional[dict] = None
