"""Tests for skills infrastructure: Neo4j sync, Redis cache, event outbox, crons."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.mark.asyncio
async def test_neo4j_initialization_no_config():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    with patch.dict("os.environ", {}, clear=True):
        await svc.initialize()
        assert not svc._enabled
    await svc.close()


@pytest.mark.asyncio
async def test_neo4j_sync_skill_noop_when_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.sync_skill_node({"skill_id": "test"})
    assert result is None


@pytest.mark.asyncio
async def test_neo4j_delete_skill_noop_when_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.delete_node("Skill", "skill_id", "test")
    assert result is None


@pytest.mark.asyncio
async def test_neo4j_find_related_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.find_related_skills("test")
    assert result == []


@pytest.mark.asyncio
async def test_neo4j_bulk_sync_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.bulk_sync_skills([{"skill_id": "a"}, {"skill_id": "b"}])
    assert result is None


@pytest.mark.asyncio
async def test_redis_initialization_no_config():
    from shared.utils.redis_cache import RedisCacheLayer
    cache = RedisCacheLayer()
    with patch.dict("os.environ", {"REDIS_URL": ""}, clear=True):
        await cache.initialize()
        assert not cache._enabled
    await cache.close()


@pytest.mark.asyncio
async def test_redis_cache_fallback_to_memory():
    from shared.utils.redis_cache import RedisCacheLayer
    cache = RedisCacheLayer()
    cache._enabled = False
    await cache.set("test:key", {"hello": "world"})
    result = await cache.get("test:key")
    assert result == {"hello": "world"}
    await cache.delete("test:key")
    result = await cache.get("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_redis_cache_clear_via_invalidate():
    from shared.utils.redis_cache import RedisCacheLayer
    cache = RedisCacheLayer()
    cache._enabled = False
    await cache.set("skills:a", 1)
    await cache.set("skills:b", 2)
    await cache.invalidate_prefix("skills")
    assert await cache.get("skills:a") is None
    assert await cache.get("skills:b") is None


@pytest.mark.asyncio
async def test_redis_bulk_ops_fallback():
    from shared.utils.redis_cache import RedisCacheLayer
    cache = RedisCacheLayer()
    cache._enabled = False
    await cache.bulk_set({"k1": "v1", "k2": "v2"})
    result = await cache.bulk_get(["k1", "k2", "k3"])
    assert result == {"k1": "v1", "k2": "v2"}


@pytest.mark.asyncio
async def test_event_outbox_emit_when_supabase_fails():
    from shared.utils.event_outbox import EventOutboxProcessor
    processor = EventOutboxProcessor()
    with patch("config.core.supabase.get_supabase_client", side_effect=Exception("no db")):
        result = await processor.emit("test.event", "skill", "abc", {"key": "val"})
        assert result is None


@pytest.mark.asyncio
async def test_event_outbox_register_and_dispatch():
    from shared.utils.event_outbox import EventOutboxProcessor
    processor = EventOutboxProcessor()
    handler = AsyncMock()
    processor.register_handler("skill.updated", handler)
    assert "skill.updated" in processor._handlers
    assert len(processor._handlers["skill.updated"]) == 1


@pytest.mark.asyncio
async def test_event_outbox_register_all():
    from shared.utils.event_outbox import EventOutboxProcessor
    processor = EventOutboxProcessor()
    handler1 = AsyncMock()
    handler2 = AsyncMock()
    processor.register_all({"skill.created": [handler1], "skill.deleted": [handler2]})
    assert len(processor._handlers["skill.created"]) == 1
    assert len(processor._handlers["skill.deleted"]) == 1


@pytest.mark.asyncio
async def test_event_outbox_poll_no_db():
    from shared.utils.event_outbox import EventOutboxProcessor
    processor = EventOutboxProcessor()
    with patch("config.core.supabase.get_supabase_client", side_effect=Exception("no db")):
        result = await processor.poll_once()
        assert result == (0, 0)


@pytest.mark.asyncio
async def test_mv_refresh_runs():
    from services.scheduler.crons.skill_mv_refresh import run_skill_mv_refresh
    with patch("config.core.supabase.get_supabase_client", side_effect=Exception("no db")):
        result = await run_skill_mv_refresh()
        assert result is None


@pytest.mark.asyncio
async def test_retention_cleanup_runs():
    from services.scheduler.crons.skill_retention_cleanup import run_skill_retention_cleanup
    with patch("config.core.supabase.get_supabase_client", side_effect=Exception("no db")):
        result = await run_skill_retention_cleanup()
        assert result is None


@pytest.mark.asyncio
async def test_neoj4_bulk_relationships_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.bulk_sync_relationships([{"from_skill_id": "a", "to_skill_id": "b"}])
    assert result is None


@pytest.mark.asyncio
async def test_neoj4_sync_category_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.sync_category_node({"category_id": "c1"})
    assert result is None


@pytest.mark.asyncio
async def test_neoj4_sync_user_skill_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.sync_user_skill_edges({"user_id": "u1", "skill_id": "s1"})
    assert result is None


@pytest.mark.asyncio
async def test_neoj4_sync_relationship_disabled():
    from shared.utils.neo4j_sync import Neo4jSyncService
    svc = Neo4jSyncService()
    svc._enabled = False
    result = await svc.sync_relationship_edge({"from_skill_id": "a", "to_skill_id": "b"})
    assert result is None
