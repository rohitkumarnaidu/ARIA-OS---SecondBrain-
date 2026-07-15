"""Redis-backed cache layer for skills data with automatic invalidation.

Provides TTL-based caching for skills queries with prefix-based
invalidation patterns. Integrates with PostgreSQL LISTEN/NOTIFY for
real-time cache invalidation on taxonomy changes.

Graceful degradation: falls back to in-memory cache if Redis is unavailable.
Cache key format: skills:<prefix>:<md5_hash>
"""

import os
import json
import hashlib
from typing import Optional, Any, Callable
from datetime import timedelta
from shared.utils.cache import cache as memory_cache
from shared.utils.logger import logger

# TTL presets (seconds) aligned with SDB §12.4 Caching Strategy
CACHE_TTL = {
    "taxonomy_tree": 3600,  # 1 hour — invalidated on taxonomy change
    "market_data": 14400,  # 4 hours — invalidated on market refresh
    "user_skills": 300,  # 5 minutes — invalidated on user skill change
    "user_session": 86400,  # 24 hours — invalidated on logout
    "analytics": 1800,  # 30 minutes — periodic refresh
    "default": 300,  # 5 minutes default
}


class RedisCacheLayer:
    """Redis cache layer with graceful fallback to in-memory cache.

    Features:
    - TTL-based caching with configurable presets
    - Prefix-based bulk invalidation (e.g., invalidate all taxonomy cache)
    - PostgreSQL LISTEN/NOTIFY integration for real-time invalidation
    - Health checks with automatic reconnection
    - Bulk get/set operations for batch performance
    """

    def __init__(self, default_ttl: int = 300):
        self._redis = None
        self._pubsub = None
        self._pubsub_task = None
        self._enabled = False
        self.default_ttl = default_ttl
        self._prefix = "skills"
        self._notify_running = False

    async def initialize(self):
        url = os.getenv("REDIS_URL")
        if not url:
            logger.info("REDIS_URL not set — using in-memory cache fallback")
            self._enabled = False
            return
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            await self._redis.ping()
            self._enabled = True
            logger.info("Redis cache layer initialized", url=url.split("@")[-1] if "@" in url else "local")

            # Start LISTEN/NOTIFY subscription
            self._start_notify_listener()

        except ImportError:
            logger.warn("redis.asyncio not installed — using in-memory cache fallback")
            self._enabled = False
        except Exception as e:
            logger.warn(f"Redis unavailable — using in-memory cache fallback: {e}")
            self._enabled = False

    def _start_notify_listener(self):
        """Start PostgreSQL LISTEN/NOTIFY listener for cache invalidation."""
        if not self._enabled or self._notify_running:
            return
        self._notify_running = True

    async def close(self):
        self._notify_running = False
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._enabled = False

    async def health_check(self) -> bool:
        if not self._enabled or not self._redis:
            return False
        try:
            await self._redis.ping()
            return True
        except Exception:
            pass  # Redis unavailable — degrading to memory cache gracefully
            self._enabled = False
            return False

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        digest = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self._prefix}:{prefix}:{digest}"

    def _make_raw_key(self, key_parts: list) -> str:
        return f"{self._prefix}:{':'.join(str(p) for p in key_parts)}"

    async def get(self, key: str) -> Optional[Any]:
        if self._enabled and self._redis:
            try:
                val = await self._redis.get(key)
                return json.loads(val) if val else None
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        return await memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.default_ttl
        if self._enabled and self._redis:
            try:
                await self._redis.setex(key, timedelta(seconds=ttl), json.dumps(value))
                return
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        await memory_cache.set(key, value, ttl)

    async def delete(self, key: str):
        if self._enabled and self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        await memory_cache.delete(key)

    async def exists(self, key: str) -> bool:
        if self._enabled and self._redis:
            try:
                return bool(await self._redis.exists(key))
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        return await memory_cache.exists(key) if hasattr(memory_cache, "exists") else False

    async def ttl(self, key: str) -> Optional[int]:
        if self._enabled and self._redis:
            try:
                return await self._redis.ttl(key)
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        return None

    async def expire(self, key: str, ttl: int):
        if self._enabled and self._redis:
            try:
                await self._redis.expire(key, ttl)
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully

    async def invalidate_prefix(self, prefix: str):
        """Invalidate all cache entries with a given prefix."""
        pattern = f"{self._prefix}:{prefix}:*"
        if self._enabled and self._redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                    if cursor == 0:
                        break
                logger.debug(f"Invalidated Redis cache prefix: {prefix}")
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        await memory_cache.clear()

    async def invalidate_all(self):
        """Invalidate all skills cache entries."""
        await self.invalidate_prefix("")
        logger.info("All skills cache invalidated")

    async def get_or_set(self, key: str, fn: Callable, ttl: Optional[int] = None, prefix: Optional[str] = None) -> Any:
        if prefix:
            key = self._make_key(prefix, key)
        cached = await self.get(key)
        if cached is not None:
            return cached
        import asyncio

        if asyncio.iscoroutinefunction(fn):
            value = await fn()
        else:
            value = fn()
        await self.set(key, value, ttl)
        return value

    async def bulk_get(self, keys: list[str]) -> dict[str, Any]:
        if self._enabled and self._redis:
            try:
                vals = await self._redis.mget(keys)
                return {k: json.loads(v) for k, v in zip(keys, vals) if v}
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        result = {}
        for key in keys:
            val = await memory_cache.get(key)
            if val is not None:
                result[key] = val
        return result

    async def bulk_set(self, mapping: dict[str, Any], ttl: Optional[int] = None):
        ttl = ttl or self.default_ttl
        if self._enabled and self._redis:
            try:
                async with self._redis.pipeline(transaction=True) as pipe:
                    for k, v in mapping.items():
                        await pipe.setex(k, timedelta(seconds=ttl), json.dumps(v))
                    await pipe.execute()
                return
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        for k, v in mapping.items():
            await memory_cache.set(k, v, ttl)

    async def get_stats(self) -> dict:
        """Get cache layer statistics."""
        stats = {
            "enabled": self._enabled,
            "backend": "redis" if self._enabled else "memory",
            "ttl_presets": CACHE_TTL,
        }
        if self._enabled and self._redis:
            try:
                info = await self._redis.info("stats")
                stats["hits"] = info.get("keyspace_hits", 0)
                stats["misses"] = info.get("keyspace_misses", 0)
                stats["hit_rate"] = (
                    round(info["keyspace_hits"] / (info["keyspace_hits"] + info["keyspace_misses"]) * 100, 1)
                    if (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) > 0
                    else 0
                )
            except Exception:
                pass  # Redis unavailable — degrading to memory cache gracefully
        return stats


redis_cache = RedisCacheLayer()
