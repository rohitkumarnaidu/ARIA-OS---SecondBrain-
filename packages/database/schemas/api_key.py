from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ApiKeyTier(str):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"


TIER_LIMITS = {
    ApiKeyTier.FREE: {"max_requests": 10, "window_seconds": 60, "concurrent": 1},
    ApiKeyTier.PRO: {"max_requests": 100, "window_seconds": 60, "concurrent": 10},
    ApiKeyTier.ENTERPRISE: {"max_requests": 1000, "window_seconds": 60, "concurrent": 100},
    ApiKeyTier.INTERNAL: {"max_requests": 10000, "window_seconds": 60, "concurrent": 500},
}


class ApiKeyCreate(BaseModel):
    name: str
    tier: str = ApiKeyTier.FREE
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    tier: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    tier: Optional[str] = None
