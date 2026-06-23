from pydantic import BaseModel
from typing import Optional


class FeedbackCreate(BaseModel):
    source: str
    target_id: str
    rating: int
    comment: Optional[str] = None
    metadata: Optional[dict] = None


class FeedbackResponse(BaseModel):
    id: str
    source: str
    target_id: str
    rating: int
    comment: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: str


class FeedbackSummary(BaseModel):
    total: int
    positive: int
    negative: int
    positive_rate: float
    by_source: dict[str, int]
