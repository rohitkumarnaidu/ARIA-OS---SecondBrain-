from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any, List


class FeatureFlagCreate(BaseModel):
    key: str
    enabled: bool = False
    rollout_percentage: int = 0
    user_segments: Optional[List[str]] = None
    metadata: Optional[dict] = None


class FeatureFlagUpdate(BaseModel):
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None
    user_segments: Optional[List[str]] = None
    metadata: Optional[dict] = None


class FeatureFlagResponse(BaseModel):
    id: str
    key: str
    enabled: bool
    rollout_percentage: int
    user_segments: Optional[List[str]] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
