import hashlib
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config.core.config import settings
from shared.utils.cache import cached
from shared.utils.security import generate_api_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


@cached(ttl=60, key_prefix="verify_token")
def _verify_supabase_token(token: str):
    from config.core.supabase import get_supabase_client

    supabase = get_supabase_client()
    return supabase.auth.get_user(token)


async def get_current_user(authorization: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = authorization

    if token.startswith("sb_"):
        from config.core.api_key_auth import authenticate_with_api_key

        try:
            user = await authenticate_with_api_key(token)
            return user
        except HTTPException:
            raise credentials_exception

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await _verify_supabase_token(token)
    return user


# In-memory store for rotated keys (replace with Redis in production)
# Maps SHA-256 hash of old key -> {expires: datetime}
rotated_keys_cache: dict = {}


def rotate_api_key(user_id: str) -> dict:
    """Rotate API key: generate new key, store in Supabase, return new key + old expiry."""
    from config.core.supabase import get_supabase_client

    new_key = generate_api_key(prefix="sb")
    key_hash = hashlib.sha256(new_key.encode()).hexdigest()

    expires_at = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    old_expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    supabase = get_supabase_client()
    supabase.from_("api_keys").insert(
        {
            "user_id": user_id,
            "key_hash": key_hash,
            "is_active": True,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ).execute()

    cache_key = f"rotated:{key_hash}"
    rotated_keys_cache[cache_key] = {
        "user_id": user_id,
        "expires": datetime.now(timezone.utc) + timedelta(hours=24),
    }

    return {
        "new_key": new_key,
        "old_key_expires_at": old_expires,
    }


def refresh_jwt_token(refresh_token: str) -> dict:
    """Validate refresh token and issue new JWT + refresh token pair."""
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access = create_access_token(data={"sub": user_id, "type": "access"})
    new_refresh = create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=30),
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }
