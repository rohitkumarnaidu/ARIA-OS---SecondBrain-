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


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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


def rotate_api_key(old_key: str) -> dict:
    """Rotate API key: generate new key, cache old for 24h grace period."""
    new_key = generate_api_key(prefix="sb")

    key_hash = hashlib.sha256(old_key.encode()).hexdigest()
    rotated_keys_cache[f"rotated:{key_hash}"] = {
        "expires": datetime.now(timezone.utc) + timedelta(hours=24),
    }

    return {
        "new_key": new_key,
        "old_key_expires": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    }
