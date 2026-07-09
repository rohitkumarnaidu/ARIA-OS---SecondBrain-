"""API Gateway — ties together API key auth, tier-based rate limiting, and audit.

Usage in route files:
    from config.core.api_gateway import gateway

    @router.get("/items")
    async def list_items(request: Request):
        await gateway.check(request, "items", require_auth=True)
        ...
"""

import hashlib
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from fastapi import Request, HTTPException
from config.core.supabase import get_supabase_client
from shared.utils.audit import log_audit, action_from_method
from database.schemas.api_key import TIER_LIMITS


class ApiGateway:
    """Enterprise API Gateway — key auth + tier rate limiting + audit logging."""

    TIERS = TIER_LIMITS

    def __init__(self):
        self._requests: Dict[str, Dict[str, List[float]]] = {}

    async def authenticate(self, api_key: str) -> Tuple[str, str]:
        """Validate API key and return (user_id, tier). Raises 401 on failure."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        supabase = get_supabase_client()

        result = (
            supabase.from_("api_keys")
            .select("user_id, tier, expires_at, is_active")
            .eq("key_hash", key_hash)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            raise HTTPException(status_code=401, detail="Invalid API key")

        key_data = rows[0]
        if not key_data.get("is_active", True):
            raise HTTPException(status_code=401, detail="API key is deactivated")

        expires = key_data.get("expires_at")
        if expires:
            expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            if expires_dt < datetime.now(timezone.utc):
                raise HTTPException(status_code=401, detail="API key has expired")

        return key_data["user_id"], key_data.get("tier", "free")

    async def check(self, request: Request, resource: str, require_auth: bool = False):
        """Check rate limits and optional API key auth. Sets request.state.user_id."""
        client_ip = request.client.host if request.client else "unknown"
        tier = "internal"
        user_id = None

        api_key = request.headers.get("X-API-Key")
        if api_key:
            user_id, tier = await self.authenticate(api_key)
            request.state.user_id = user_id
        elif require_auth:
            raise HTTPException(status_code=401, detail="Missing X-API-Key header")

        limits = self.TIERS.get(tier, self.TIERS["free"])
        key = f"{tier}:{client_ip}"
        now = time.time()
        window_start = now - limits["window_seconds"]

        if key not in self._requests:
            self._requests[key] = []
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= limits["max_requests"]:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Tier '{tier}': {limits['max_requests']} req/{limits['window_seconds']}s",
            )

        self._requests[key].append(now)
        request.state.tier = tier
        request.state.rate_limit_remaining = limits["max_requests"] - len(self._requests[key])

    async def audit(self, request: Request, response_status: int, user_id: Optional[str] = None):
        """Log audit entry for mutation requests."""
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        if response_status >= 400:
            return

        uid = user_id or getattr(request.state, "user_id", None)
        if not uid:
            return

        resource = str(request.url.path).replace("/api/v1/", "").split("/")[0]
        await log_audit(
            user_id=uid,
            action=action_from_method(request.method),
            resource=resource,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )


gateway = ApiGateway()
