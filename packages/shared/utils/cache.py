from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta, timezone
import asyncio
import hashlib


class SimpleCache:
    """In-memory cache with TTL support"""

    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from args/kwargs"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now(timezone.utc) < entry["expires"]:
                    return entry["value"]
                else:
                    del self.cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            self.cache[key] = {
                "value": value,
                "expires": datetime.now(timezone.utc) + timedelta(seconds=ttl),
            }

    async def delete(self, key: str):
        """Delete specific key from cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]

    async def clear(self):
        """Clear all cache"""
        async with self._lock:
            self.cache.clear()

    async def get_or_set(self, key: str, fn: Callable, ttl: Optional[int] = None) -> Any:
        """Get from cache or execute fn and cache result"""
        value = await self.get(key)
        if value is not None:
            return value

        value = await fn() if asyncio.iscoroutinefunction(fn) else fn()
        await self.set(key, value, ttl)
        return value


# Global cache instance
cache = SimpleCache(default_ttl_seconds=300)


# Decorator for caching async functions
def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache async function results"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix or func.__name__}:{args}:{sorted(kwargs.items())}"
            key_hash = hashlib.md5(cache_key.encode()).hexdigest()
            return await cache.get_or_set(key_hash, lambda: func(*args, **kwargs), ttl)

        return wrapper

    return decorator


# Helper to invalidate cache by pattern
async def invalidate_cache(pattern: str):
    """Remove cache entries matching pattern"""
    keys_to_delete = [k for k in cache.cache.keys() if pattern in k]
    for key in keys_to_delete:
        await cache.delete(key)
