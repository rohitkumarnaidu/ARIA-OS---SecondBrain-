"""Comprehensive tests for all cache utility modules: SimpleCache, cached decorator,
invalidate_cache, ResponseCacheMiddleware, RedisCacheLayer, and AICache."""

# ruff: noqa: E402

import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.utils.cache import SimpleCache, cached, invalidate_cache
from shared.utils.cache_middleware import ResponseCacheMiddleware
from shared.utils.redis_cache import RedisCacheLayer, CACHE_TTL
from shared.utils.ai_cache import AICache

pytestmark = pytest.mark.asyncio


# ════════════════════════════════════════════
# SimpleCache
# ════════════════════════════════════════════


class TestSimpleCache:

    async def test_init_default_ttl(self):
        c = SimpleCache()
        assert c.default_ttl == 300

    async def test_init_custom_ttl(self):
        c = SimpleCache(default_ttl_seconds=600)
        assert c.default_ttl == 600

    async def test_make_key_deterministic(self):
        c = SimpleCache()
        a = c._make_key("p", "arg1", kw="val")
        b = c._make_key("p", "arg1", kw="val")
        assert a == b

    async def test_make_key_different_args(self):
        c = SimpleCache()
        a = c._make_key("p", "arg1", kw="val")
        b = c._make_key("p", "arg2", kw="val")
        assert a != b

    async def test_get_hit(self):
        c = SimpleCache()
        await c.set("k", "v")
        assert await c.get("k") == "v"

    async def test_get_miss(self):
        c = SimpleCache()
        assert await c.get("nonexistent") is None

    async def test_get_expired_auto_removes(self):
        c = SimpleCache()
        past = datetime.now(timezone.utc) - timedelta(seconds=10)
        c.cache["k"] = {"value": "v", "expires": past}
        result = await c.get("k")
        assert result is None
        assert "k" not in c.cache

    async def test_set_default_ttl(self):
        c = SimpleCache(default_ttl_seconds=300)
        await c.set("k", "v")
        entry = c.cache["k"]
        remaining = (entry["expires"] - datetime.now(timezone.utc)).total_seconds()
        assert 295 < remaining < 305
        assert entry["value"] == "v"

    async def test_set_custom_ttl(self):
        c = SimpleCache()
        await c.set("k", "v", ttl=60)
        remaining = (c.cache["k"]["expires"] - datetime.now(timezone.utc)).total_seconds()
        assert 55 < remaining < 65

    async def test_delete_existing_key(self):
        c = SimpleCache()
        await c.set("k", "v")
        await c.delete("k")
        assert await c.get("k") is None

    async def test_delete_nonexistent_key(self):
        c = SimpleCache()
        await c.delete("does-not-exist")

    async def test_clear_removes_all(self):
        c = SimpleCache()
        await c.set("a", 1)
        await c.set("b", 2)
        await c.clear()
        assert len(c.cache) == 0
        assert await c.get("a") is None
        assert await c.get("b") is None

    async def test_get_or_set_cache_hit_returns_cached(self):
        c = SimpleCache()
        await c.set("k", "cached_val")
        fn = AsyncMock(return_value="new_val")
        result = await c.get_or_set("k", fn)
        assert result == "cached_val"
        fn.assert_not_awaited()

    async def test_get_or_set_cache_miss_sync_fn(self):
        c = SimpleCache()
        fn = MagicMock(return_value=42)
        result = await c.get_or_set("k", fn)
        assert result == 42
        fn.assert_called_once()

    async def test_get_or_set_cache_miss_async_fn(self):
        c = SimpleCache()
        fn = AsyncMock(return_value=99)
        result = await c.get_or_set("k", fn)
        assert result == 99
        fn.assert_awaited_once()

    async def test_get_or_set_with_custom_ttl(self):
        c = SimpleCache()
        fn = AsyncMock(return_value="x")
        await c.get_or_set("k", fn, ttl=10)
        remaining = (c.cache["k"]["expires"] - datetime.now(timezone.utc)).total_seconds()
        assert 8 < remaining < 12

    async def test_get_or_set_error_does_not_cache(self):
        c = SimpleCache()
        fn = AsyncMock(side_effect=ValueError("oops"))
        with pytest.raises(ValueError):
            await c.get_or_set("k", fn)
        assert "k" not in c.cache


# ════════════════════════════════════════════
# cached decorator
# ════════════════════════════════════════════


class TestCachedDecorator:

    async def test_caches_result(self):
        call_count = 0

        @cached(ttl=300, key_prefix="test_prefix")
        def compute(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        r1 = await compute(5)
        assert r1 == 10
        assert call_count == 1

        r2 = await compute(5)
        assert r2 == 10
        assert call_count == 1

    async def test_different_args_produce_different_keys(self):
        call_count = 0

        @cached(ttl=300)
        def add_(a, b):
            nonlocal call_count
            call_count += 1
            return a + b

        assert await add_(1, 2) == 3
        assert call_count == 1
        assert await add_(3, 4) == 7
        assert call_count == 2

    async def test_default_key_prefix_uses_function_name(self):
        call_count = 0

        @cached(ttl=300)
        def my_func():
            nonlocal call_count
            call_count += 1
            return "done"

        assert await my_func() == "done"
        assert call_count == 1
        assert await my_func() == "done"
        assert call_count == 1

    async def test_expiry_via_invalidation(self):
        call_count = 0

        @cached(ttl=300, key_prefix="exp")
        def quick():
            nonlocal call_count
            call_count += 1
            return "fresh"

        assert await quick() == "fresh"
        assert call_count == 1
        # simulate expiry by clearing the underlying cache
        import shared.utils.cache as cache_mod
        await cache_mod.cache.clear()
        assert await quick() == "fresh"
        assert call_count == 2


# ════════════════════════════════════════════
# invalidate_cache
# ════════════════════════════════════════════


class TestInvalidateCache:

    async def test_invalidate_matching_pattern(self):
        c = SimpleCache()
        await c.set("user:1:data", "a")
        await c.set("user:2:data", "b")
        await c.set("other:key", "c")
        import shared.utils.cache as cache_mod

        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("user:")
            assert await c.get("user:1:data") is None
            assert await c.get("user:2:data") is None
            assert await c.get("other:key") == "c"
        finally:
            cache_mod.cache = orig

    async def test_invalidate_no_match(self):
        c = SimpleCache()
        await c.set("a", 1)
        import shared.utils.cache as cache_mod

        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("zzz")
            assert await c.get("a") == 1
        finally:
            cache_mod.cache = orig

    async def test_invalidate_empty_cache(self):
        c = SimpleCache()
        import shared.utils.cache as cache_mod

        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("anything")
        finally:
            cache_mod.cache = orig


# ════════════════════════════════════════════
# ResponseCacheMiddleware
# ════════════════════════════════════════════


class TestResponseCacheMiddleware:

    def test_init_defaults(self):
        mw = ResponseCacheMiddleware(MagicMock())
        assert mw.default_ttl == 60
        assert mw.max_size == 256
        assert mw._skip_paths == {"/health", "/metrics", "/api/v1/chat"}

    def test_init_custom_values(self):
        mw = ResponseCacheMiddleware(MagicMock(), default_ttl=120, max_size=512)
        assert mw.default_ttl == 120
        assert mw.max_size == 512

    async def test_dispatch_skips_non_get(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/v1/tasks"
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        result = await mw.dispatch(request, call_next)
        assert result == response
        call_next.assert_awaited_once()

    async def test_dispatch_skips_health_path(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/health"
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        result = await mw.dispatch(request, call_next)
        assert result == response

    async def test_dispatch_skips_metrics_path(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/metrics"
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        result = await mw.dispatch(request, call_next)
        assert result == response

    async def test_dispatch_skips_chat_path(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/chat"
        request.headers = {}
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        result = await mw.dispatch(request, call_next)
        assert result == response

    async def test_dispatch_skips_no_cache_header(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.headers.get.return_value = "no-cache"
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        result = await mw.dispatch(request, call_next)
        assert result == response

    async def test_dispatch_cache_hit_returns_cached(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.headers.get.return_value = ""
        request.query_params.items.return_value = []
        cached_body = b'{"data":"test"}'
        with patch(
            "shared.utils.cache_middleware.cache.get",
            AsyncMock(
                return_value={
                    "body": cached_body,
                    "status": 200,
                    "media_type": "application/json",
                    "headers": {"content-type": "application/json"},
                }
            ),
        ):
            result = await mw.dispatch(request, AsyncMock())
            assert result.status_code == 200
            assert result.headers["X-Cache"] == "HIT"

    async def test_dispatch_cache_miss_stores_and_returns(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.headers.get.return_value = ""
        request.query_params.items.return_value = []

        async def _iter():
            yield b'{"data":"ok"}'

        response = MagicMock()
        response.status_code = 200
        response.headers.get.return_value = "13"
        response.media_type = "application/json"
        response.body_iterator = _iter()
        call_next = AsyncMock(return_value=response)
        with patch("shared.utils.cache_middleware.cache.get", AsyncMock(return_value=None)):
            with patch("shared.utils.cache_middleware.cache.set", AsyncMock()) as mock_set:
                result = await mw.dispatch(request, call_next)
                assert result.status_code == 200
                mock_set.assert_awaited_once()

    async def test_dispatch_cache_miss_large_body_skips_cache(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.headers.get.return_value = ""
        request.query_params.items.return_value = []
        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-length": "999999"}
        call_next = AsyncMock(return_value=response)
        with patch("shared.utils.cache_middleware.cache.get", AsyncMock(return_value=None)):
            with patch("shared.utils.cache_middleware.cache.set", AsyncMock()) as mock_set:
                result = await mw.dispatch(request, call_next)
                assert result == response
                mock_set.assert_not_called()

    async def test_dispatch_cache_miss_error_status_skips_cache(self):
        mw = ResponseCacheMiddleware(MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.headers.get.return_value = ""
        request.query_params.items.return_value = []
        response = MagicMock()
        response.status_code = 500
        call_next = AsyncMock(return_value=response)
        with patch("shared.utils.cache_middleware.cache.get", AsyncMock(return_value=None)):
            with patch("shared.utils.cache_middleware.cache.set", AsyncMock()) as mock_set:
                result = await mw.dispatch(request, call_next)
                assert result == response
                mock_set.assert_not_called()

    def test_cache_key_deterministic(self):
        r1 = MagicMock()
        r1.method = "GET"
        r1.url.path = "/api/v1/tasks"
        r1.query_params.items.return_value = [("page", "1")]
        r2 = MagicMock()
        r2.method = "GET"
        r2.url.path = "/api/v1/tasks"
        r2.query_params.items.return_value = [("page", "1")]
        assert ResponseCacheMiddleware._cache_key(r1) == ResponseCacheMiddleware._cache_key(r2)

    def test_cache_key_different_params(self):
        r1 = MagicMock()
        r1.method = "GET"
        r1.url.path = "/api/v1/tasks"
        r1.query_params.items.return_value = [("page", "1")]
        r2 = MagicMock()
        r2.method = "GET"
        r2.url.path = "/api/v1/tasks"
        r2.query_params.items.return_value = [("page", "2")]
        assert ResponseCacheMiddleware._cache_key(r1) != ResponseCacheMiddleware._cache_key(r2)

    def test_cache_key_format(self):
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/v1/tasks"
        request.query_params.items.return_value = [("page", "1")]
        key = ResponseCacheMiddleware._cache_key(request)
        assert key.startswith("rm:")
        assert len(key) == 35


# ════════════════════════════════════════════
# RedisCacheLayer
# ════════════════════════════════════════════


class TestRedisCacheLayer:

    async def test_init_defaults(self):
        layer = RedisCacheLayer()
        assert layer._redis is None
        assert layer._pubsub is None
        assert layer._pubsub_task is None
        assert layer._enabled is False
        assert layer.default_ttl == 300
        assert layer._prefix == "skills"
        assert layer._notify_running is False

    async def test_init_custom_ttl(self):
        layer = RedisCacheLayer(default_ttl=600)
        assert layer.default_ttl == 600

    async def test_initialize_no_redis_url(self):
        with patch.dict(os.environ, {}, clear=True):
            layer = RedisCacheLayer()
            await layer.initialize()
            assert layer._enabled is False

    async def test_initialize_import_error(self):
        with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
            with patch("builtins.__import__", side_effect=ImportError("no module named redis.asyncio")):
                layer = RedisCacheLayer()
                await layer.initialize()
                assert layer._enabled is False

    async def test_initialize_redis_unavailable(self):
        with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
            fake_redis = MagicMock()
            fake_redis.ping = AsyncMock(side_effect=Exception("Connection refused"))
            with patch("redis.asyncio.from_url", return_value=fake_redis):
                layer = RedisCacheLayer()
                await layer.initialize()
                assert layer._enabled is False

    async def test_initialize_redis_available(self):
        with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
            fake_redis = MagicMock()
            fake_redis.ping = AsyncMock(return_value=True)
            with patch("redis.asyncio.from_url", return_value=fake_redis):
                layer = RedisCacheLayer()
                await layer.initialize()
                assert layer._enabled is True
                assert layer._redis is fake_redis
                assert layer._notify_running is True

    async def test_start_notify_listener_already_running(self):
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._notify_running = True
        layer._start_notify_listener()
        assert layer._notify_running is True

    async def test_start_notify_listener_not_running(self):
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._notify_running = False
        layer._start_notify_listener()
        assert layer._notify_running is True

    async def test_start_notify_listener_not_enabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        layer._notify_running = False
        layer._start_notify_listener()
        assert layer._notify_running is False

    async def test_close_with_redis(self):
        fake_redis = AsyncMock()
        layer = RedisCacheLayer()
        layer._redis = fake_redis
        layer._enabled = True
        await layer.close()
        assert layer._redis is None
        assert layer._enabled is False
        assert layer._notify_running is False
        fake_redis.close.assert_awaited_once()

    async def test_close_without_redis(self):
        layer = RedisCacheLayer()
        layer._enabled = True
        await layer.close()
        assert layer._notify_running is False
        assert layer._redis is None
        # _enabled only set to False inside if self._redis block
        assert layer._enabled is True

    async def test_health_check_not_enabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        result = await layer.health_check()
        assert result is False

    async def test_health_check_enabled_no_redis(self):
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = None
        result = await layer.health_check()
        assert result is False

    async def test_health_check_ping_succeeds(self):
        fake_redis = AsyncMock()
        fake_redis.ping = AsyncMock(return_value=True)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.health_check()
        assert result is True

    async def test_health_check_ping_fails(self):
        fake_redis = AsyncMock()
        fake_redis.ping = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.health_check()
        assert result is False
        assert layer._enabled is False

    async def test_make_key_format(self):
        layer = RedisCacheLayer()
        key = layer._make_key("user_skills", "user_123")
        assert key.startswith("skills:user_skills:")
        expected_digest = hashlib.md5("user_skills:('user_123',):[]".encode()).hexdigest()
        assert key == f"skills:user_skills:{expected_digest}"

    async def test_make_key_with_kwargs(self):
        layer = RedisCacheLayer()
        key = layer._make_key("taxonomy", domain="tech")
        assert key.startswith("skills:taxonomy:")
        expected_digest = hashlib.md5("taxonomy:():[('domain', 'tech')]".encode()).hexdigest()
        assert key == f"skills:taxonomy:{expected_digest}"

    async def test_make_raw_key_format(self):
        layer = RedisCacheLayer()
        key = layer._make_raw_key(["user_skills", "user_123"])
        assert key == "skills:user_skills:user_123"

    async def test_make_raw_key_single_part(self):
        layer = RedisCacheLayer()
        key = layer._make_raw_key(["all"])
        assert key == "skills:all"

    async def test_get_redis_enabled_success(self):
        fake_redis = AsyncMock()
        fake_redis.get = AsyncMock(return_value=json.dumps({"name": "test"}))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.get("skills:test:abc")
        assert result == {"name": "test"}

    async def test_get_redis_returns_none(self):
        fake_redis = AsyncMock()
        fake_redis.get = AsyncMock(return_value=None)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.get("skills:test:abc")
        assert result is None

    async def test_get_redis_exception_falls_back(self):
        fake_redis = AsyncMock()
        fake_redis.get = AsyncMock(side_effect=Exception("timeout"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch.object(layer, "_enabled", True):
            with patch("shared.utils.redis_cache.memory_cache.get", AsyncMock(return_value="fallback")):
                result = await layer.get("skills:test:abc")
                assert result == "fallback"

    async def test_get_redis_disabled_falls_back(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.get", AsyncMock(return_value="mem")):
            result = await layer.get("skills:test:abc")
            assert result == "mem"

    async def test_set_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.setex = AsyncMock()
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        await layer.set("k", {"data": 1}, ttl=300)
        fake_redis.setex.assert_awaited_once()

    async def test_set_redis_exception_falls_back(self):
        fake_redis = AsyncMock()
        fake_redis.setex = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.set", AsyncMock()) as mock_set:
            await layer.set("k", "v", ttl=60)
            mock_set.assert_awaited_once_with("k", "v", 60)

    async def test_set_redis_disabled_falls_back(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.set", AsyncMock()) as mock_set:
            await layer.set("k", "v", ttl=60)
            mock_set.assert_awaited_once_with("k", "v", 60)

    async def test_set_uses_default_ttl_when_none(self):
        fake_redis = AsyncMock()
        layer = RedisCacheLayer(default_ttl=500)
        layer._enabled = True
        layer._redis = fake_redis
        await layer.set("k", "v")
        call_kwargs = fake_redis.setex.call_args
        assert call_kwargs is not None

    async def test_delete_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.delete = AsyncMock(return_value=1)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.delete", AsyncMock()):
            await layer.delete("k")
            fake_redis.delete.assert_awaited_once_with("k")

    async def test_delete_redis_exception_falls_back(self):
        fake_redis = AsyncMock()
        fake_redis.delete = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.delete", AsyncMock()) as mock_del:
            await layer.delete("k")
            mock_del.assert_awaited_once_with("k")

    async def test_delete_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.delete", AsyncMock()) as mock_del:
            await layer.delete("k")
            mock_del.assert_awaited_once_with("k")

    async def test_exists_redis_enabled_true(self):
        fake_redis = AsyncMock()
        fake_redis.exists = AsyncMock(return_value=1)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.exists("k")
        assert result is True

    async def test_exists_redis_enabled_false(self):
        fake_redis = AsyncMock()
        fake_redis.exists = AsyncMock(return_value=0)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.exists("k")
        assert result is False

    async def test_exists_redis_exception_falls_back(self):
        fake_redis = AsyncMock()
        fake_redis.exists = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache", spec=["exists"]) as mock_mem:
            mock_mem.exists = AsyncMock(return_value=True)
            result = await layer.exists("k")
            assert result is True

    async def test_exists_redis_disabled_falls_back(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache", spec=["exists"]) as mock_mem:
            mock_mem.exists = AsyncMock(return_value=True)
            result = await layer.exists("k")
            assert result is True

    async def test_exists_memory_cache_no_exists_method(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        import shared.utils.redis_cache as redis_mod

        orig = redis_mod.memory_cache
        redis_mod.memory_cache = MagicMock(spec=[])  # no exists method
        try:
            result = await layer.exists("k")
            assert result is False
        finally:
            redis_mod.memory_cache = orig

    async def test_ttl_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.ttl = AsyncMock(return_value=42)
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.ttl("k")
        assert result == 42

    async def test_ttl_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.ttl = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.ttl("k")
        assert result is None

    async def test_ttl_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        result = await layer.ttl("k")
        assert result is None

    async def test_expire_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.expire = AsyncMock()
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        await layer.expire("k", 60)
        fake_redis.expire.assert_awaited_once_with("k", 60)

    async def test_expire_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.expire = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        await layer.expire("k", 60)

    async def test_expire_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        await layer.expire("k", 60)

    async def test_invalidate_prefix_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.scan = AsyncMock(side_effect=[(0, ["k1", "k2"])])
        fake_redis.delete = AsyncMock()
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.clear", AsyncMock()) as mock_clear:
            await layer.invalidate_prefix("user_skills")
            fake_redis.scan.assert_awaited_once_with(0, match="skills:user_skills:*", count=100)
            fake_redis.delete.assert_awaited_once_with("k1", "k2")
            mock_clear.assert_awaited_once()

    async def test_invalidate_prefix_redis_scan_cursor_nonzero(self):
        fake_redis = AsyncMock()
        fake_redis.scan = AsyncMock(side_effect=[(1, ["k1"]), (0, [])])
        fake_redis.delete = AsyncMock()
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.clear", AsyncMock()):
            await layer.invalidate_prefix("test")
            assert fake_redis.scan.await_count == 2

    async def test_invalidate_prefix_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.scan = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.clear", AsyncMock()) as mock_clear:
            await layer.invalidate_prefix("test")
            mock_clear.assert_awaited_once()

    async def test_invalidate_prefix_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.clear", AsyncMock()) as mock_clear:
            await layer.invalidate_prefix("test")
            mock_clear.assert_awaited_once()

    async def test_invalidate_all_calls_invalidate_prefix(self):
        layer = RedisCacheLayer()
        with patch.object(layer, "invalidate_prefix", AsyncMock()) as mock_inv:
            with patch("shared.utils.redis_cache.logger"):
                await layer.invalidate_all()
                mock_inv.assert_awaited_once_with("")

    async def test_get_or_set_hit(self):
        layer = RedisCacheLayer()
        with patch.object(layer, "get", AsyncMock(return_value="cached")):
            fn = AsyncMock()
            result = await layer.get_or_set("k", fn)
            assert result == "cached"
            fn.assert_not_awaited()

    async def test_get_or_set_miss_sync_fn(self):
        layer = RedisCacheLayer()
        with patch.object(layer, "get", AsyncMock(return_value=None)):
            with patch.object(layer, "set", AsyncMock()):
                fn = MagicMock(return_value="computed")
                result = await layer.get_or_set("k", fn)
                assert result == "computed"

    async def test_get_or_set_miss_async_fn(self):
        layer = RedisCacheLayer()
        with patch.object(layer, "get", AsyncMock(return_value=None)):
            with patch.object(layer, "set", AsyncMock()):
                fn = AsyncMock(return_value="async_computed")
                result = await layer.get_or_set("k", fn)
                assert result == "async_computed"

    async def test_get_or_set_with_prefix(self):
        layer = RedisCacheLayer()
        with patch.object(layer, "_make_key", return_value="skills:pref:digest") as mock_key:
            with patch.object(layer, "get", AsyncMock(return_value=None)):
                with patch.object(layer, "set", AsyncMock()):
                    fn = MagicMock(return_value="v")
                    result = await layer.get_or_set("raw_key", fn, prefix="pref")
                    assert result == "v"
                    mock_key.assert_called_once_with("pref", "raw_key")

    async def test_bulk_get_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.mget = AsyncMock(return_value=[json.dumps({"a": 1}), None, json.dumps({"c": 3})])
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        result = await layer.bulk_get(["k1", "k2", "k3"])
        assert result == {"k1": {"a": 1}, "k3": {"c": 3}}

    async def test_bulk_get_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.mget = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.get", AsyncMock(side_effect=["mem1", None])):
            result = await layer.bulk_get(["k1", "k2"])
            assert result == {"k1": "mem1"}

    async def test_bulk_get_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.get", AsyncMock(side_effect=["a", None, "c"])):
            result = await layer.bulk_get(["k1", "k2", "k3"])
            assert result == {"k1": "a", "k3": "c"}

    async def test_bulk_set_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.pipeline = MagicMock()
        pipe = AsyncMock()
        pipe.setex = AsyncMock()
        pipe.execute = AsyncMock()
        fake_redis.pipeline.return_value.__aenter__.return_value = pipe
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        await layer.bulk_set({"k1": "v1", "k2": "v2"})
        assert pipe.setex.await_count == 2
        pipe.execute.assert_awaited_once()

    async def test_bulk_set_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.pipeline = MagicMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        with patch("shared.utils.redis_cache.memory_cache.set", AsyncMock()) as mock_set:
            await layer.bulk_set({"k1": "v1"})
            mock_set.assert_awaited_once_with("k1", "v1", 300)

    async def test_bulk_set_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        with patch("shared.utils.redis_cache.memory_cache.set", AsyncMock()) as mock_set:
            await layer.bulk_set({"k1": "v1", "k2": "v2"})
            assert mock_set.await_count == 2

    async def test_get_stats_redis_enabled(self):
        fake_redis = AsyncMock()
        fake_redis.info = AsyncMock(return_value={"keyspace_hits": 80, "keyspace_misses": 20})
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        stats = await layer.get_stats()
        assert stats["enabled"] is True
        assert stats["backend"] == "redis"
        assert stats["hits"] == 80
        assert stats["misses"] == 20
        assert stats["hit_rate"] == 80.0
        assert stats["ttl_presets"] == CACHE_TTL

    async def test_get_stats_redis_enabled_zero_requests(self):
        fake_redis = AsyncMock()
        fake_redis.info = AsyncMock(return_value={"keyspace_hits": 0, "keyspace_misses": 0})
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        stats = await layer.get_stats()
        assert stats["hit_rate"] == 0

    async def test_get_stats_redis_exception(self):
        fake_redis = AsyncMock()
        fake_redis.info = AsyncMock(side_effect=Exception("down"))
        layer = RedisCacheLayer()
        layer._enabled = True
        layer._redis = fake_redis
        stats = await layer.get_stats()
        assert stats["enabled"] is True
        assert stats["backend"] == "redis"
        assert "hits" not in stats

    async def test_get_stats_redis_disabled(self):
        layer = RedisCacheLayer()
        layer._enabled = False
        stats = await layer.get_stats()
        assert stats["enabled"] is False
        assert stats["backend"] == "memory"
        assert stats["ttl_presets"] == CACHE_TTL

    async def test_cache_ttl_presets_contents(self):
        assert CACHE_TTL["taxonomy_tree"] == 3600
        assert CACHE_TTL["market_data"] == 14400
        assert CACHE_TTL["user_skills"] == 300
        assert CACHE_TTL["user_session"] == 86400
        assert CACHE_TTL["analytics"] == 1800
        assert CACHE_TTL["default"] == 300


# ════════════════════════════════════════════
# Global instances
# ════════════════════════════════════════════


class TestGlobalInstances:

    def test_global_simple_cache(self):
        from shared.utils.cache import cache as g_cache

        assert g_cache.default_ttl == 300

    def test_global_redis_cache(self):
        from shared.utils.redis_cache import redis_cache as g_redis

        assert g_redis.default_ttl == 300
        assert g_redis._enabled is False

    def test_global_ai_cache(self):
        from shared.utils.ai_cache import ai_cache as g_ai

        assert g_ai.max_size == 1000
        assert g_ai.ttl == 3600


# ════════════════════════════════════════════
# AICache — Semantic AI Response Cache
# ════════════════════════════════════════════


class TestAICache:

    def test_init_defaults(self):
        cache = AICache()
        assert cache.max_size == 1000
        assert cache.ttl == 3600
        assert len(cache._exact_cache) == 0
        assert len(cache._semantic_cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0
        assert cache._token_savings == 0

    def test_init_custom_values(self):
        cache = AICache(max_size=500, ttl_seconds=1800)
        assert cache.max_size == 500
        assert cache.ttl == 1800

    def test_make_key_deterministic(self):
        cache = AICache()
        a = cache._make_key("sys", "user", "model")
        b = cache._make_key("sys", "user", "model")
        assert a == b

    def test_make_key_different(self):
        cache = AICache()
        a = cache._make_key("sys1", "user", "model")
        b = cache._make_key("sys2", "user", "model")
        assert a != b

    def test_get_exact_hit(self):
        cache = AICache()
        cache.set("sys", "user", "m", "response")
        result = cache.get("sys", "user", "m")
        assert result == "response"
        assert cache._hits == 1
        assert cache._misses == 0

    def test_get_exact_miss(self):
        cache = AICache()
        result = cache.get("sys", "nonexistent", "m")
        assert result is None
        assert cache._hits == 0
        assert cache._misses == 1

    def test_get_semantic_hit(self):
        cache = AICache()
        cache.set("system prompt", "what is the weather in paris today", "m", "sunny")
        result = cache.get("system prompt", "what is weather in Paris today", "m", similarity_threshold=0.7)
        assert result == "sunny"
        assert cache._hits == 1

    def test_get_semantic_below_threshold(self):
        cache = AICache()
        cache.set("system prompt", "weather in paris", "m", "sunny")
        result = cache.get("system prompt", "quantum physics explained", "m", similarity_threshold=0.9)
        assert result is None
        assert cache._misses == 1

    def test_get_semantic_model_mismatch(self):
        cache = AICache()
        cache.set("s", "hello world", "model_a", "response_a")
        result = cache.get("s", "hello world", "model_b", similarity_threshold=0.5)
        assert result is None

    def test_get_semantic_ttl_expired_skips(self):
        cache = AICache(ttl_seconds=0)
        cache.set("s", "long user query about something important", "m", "response")
        time.sleep(0.01)
        result = cache.get("s", "long user query about something", "m", similarity_threshold=0.7)
        assert result is None

    def test_get_expired_exact_entry_removed(self):
        cache = AICache(ttl_seconds=0)
        cache.set("s", "u", "m", "r")
        time.sleep(0.01)
        result = cache.get("s", "u", "m")
        assert result is None
        assert len(cache._exact_cache) == 0

    def test_set_normal(self):
        cache = AICache()
        cache.set("sys", "user", "m", "response", estimated_tokens=50)
        assert len(cache._exact_cache) == 1
        assert len(cache._semantic_cache) == 1
        assert cache._token_savings == 50

    def test_set_exact_cache_eviction(self):
        cache = AICache(max_size=2)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        assert len(cache._exact_cache) == 2
        assert cache.get("s1", "u1", "m") is None

    def test_set_semantic_cache_eviction(self):
        cache = AICache(max_size=4)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        cache.set("s4", "u4", "m", "r4")
        cache.set("s5", "u5", "m", "r5")
        # semantic cap = max_size // 2 = 2, after 5 inserts only last 2 remain
        assert len(cache._semantic_cache) == 2
        assert cache._semantic_cache[0]["user_prompt"] == "u4"

    def test_set_overwrites_same_key(self):
        cache = AICache()
        cache.set("s", "u", "m", "r1")
        cache.set("s", "u", "m", "r2")
        assert len(cache._exact_cache) == 1
        assert cache.get("s", "u", "m") == "r2"

    def test_move_to_end_on_hit(self):
        cache = AICache(max_size=3)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        cache.get("s1", "u1", "m")  # moves to end
        cache.set("s4", "u4", "m", "r4")
        assert cache.get("s2", "u2", "m") is None  # s2 evicted
        assert cache.get("s1", "u1", "m") == "r1"  # s1 still present

    def test_stats_property(self):
        cache = AICache()
        cache._hits = 75
        cache._misses = 25
        cache._token_savings = 10000
        stats = cache.stats
        assert stats["hit_rate"] == 75.0
        assert stats["token_savings"] == 10000
        assert stats["estimated_cost_saved"] == pytest.approx(0.03, rel=0.01)
        assert stats["exact_entries"] == 0
        assert stats["semantic_entries"] == 0
        assert stats["max_size"] == 1000
        assert stats["ttl_seconds"] == 3600

    def test_stats_empty_no_data(self):
        cache = AICache()
        stats = cache.stats
        assert stats["hit_rate"] == 0.0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_clear_removes_everything(self):
        cache = AICache()
        cache.set("s", "u", "m", "r")
        cache.clear()
        assert len(cache._exact_cache) == 0
        assert len(cache._semantic_cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0
        assert cache._token_savings == 0

    def test_invalidate_with_prefix_filters_semantic_and_clears_exact(self):
        cache = AICache()
        cache.set("s", "create task: buy groceries", "m", "ok")
        cache.set("s", "create task: do homework", "m", "ok")
        cache.set("s", "what is the weather", "m", "sunny")
        assert len(cache._semantic_cache) == 3
        assert len(cache._exact_cache) == 3
        cache.invalidate("create task")
        assert len(cache._semantic_cache) == 1
        assert cache._semantic_cache[0]["user_prompt"] == "what is the weather"
        assert len(cache._exact_cache) == 0

    def test_invalidate_without_prefix_clears_all(self):
        cache = AICache()
        cache.set("s", "u", "m", "r")
        cache.invalidate()
        assert len(cache._exact_cache) == 0
        assert len(cache._semantic_cache) == 0

    def test_get_similarity_identical_strings(self):
        cache = AICache()
        sim = cache._get_similarity("hello world", "hello world")
        assert sim == 1.0

    def test_get_similarity_partial(self):
        cache = AICache()
        sim = cache._get_similarity("hello world foo", "hello world bar")
        assert sim == 2 / 4

    def test_get_similarity_empty_strings(self):
        cache = AICache()
        assert cache._get_similarity("", "") == 0.0
        assert cache._get_similarity("hello", "") == 0.0
        assert cache._get_similarity("", "world") == 0.0

    def test_get_similarity_case_insensitive(self):
        cache = AICache()
        sim = cache._get_similarity("HELLO WORLD", "hello world")
        assert sim == 1.0

    def test_set_empty_response(self):
        cache = AICache()
        cache.set("s", "u", "m", "", estimated_tokens=0)
        result = cache.get("s", "u", "m")
        assert result == ""

    def test_semantic_cache_ttl_expired_entries_skipped(self):
        cache = AICache(ttl_seconds=0)
        cache.set("s", "hello world test query", "m", "response")
        time.sleep(0.01)
        result = cache.get("s", "hello world", "m", similarity_threshold=0.5)
        assert result is None
