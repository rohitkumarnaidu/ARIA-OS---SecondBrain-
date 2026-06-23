import hashlib
from fastapi import HTTPException
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def authenticate_with_api_key(api_key: str):
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    supabase = get_supabase_client()

    try:
        result = supabase.from_("api_keys").select("user_id, expires_at, is_active").eq("key_hash", key_hash).limit(1).execute()
        rows = result.data or []
        if not rows:
            raise HTTPException(status_code=401, detail="Invalid API key")

        key_data = rows[0]
        if not key_data.get("is_active", True):
            raise HTTPException(status_code=401, detail="API key is deactivated")

        from datetime import datetime, timezone
        expires = key_data.get("expires_at")
        if expires:
            expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            if expires_dt < datetime.now(timezone.utc):
                raise HTTPException(status_code=401, detail="API key has expired")

        user_id = key_data["user_id"]
        result = supabase.from_("users").select("*").eq("id", user_id).limit(1).execute()
        users = result.data or []
        if not users:
            raise HTTPException(status_code=401, detail="User not found")

        user = users[0]
        user.id = user_id
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API key authentication failed", error=str(e))
        raise HTTPException(status_code=500, detail="Authentication service error")
