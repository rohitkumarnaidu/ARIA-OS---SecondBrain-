"""Tests for skills infrastructure: Neo4j sync, Redis cache, event outbox, crons."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


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
async def test_event_outbox_emit_insert_fails():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Insert failed")
    processor._supabase = mock_supabase
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


# ── Event Outbox Enabled Path Tests ──


@pytest.mark.asyncio
async def test_event_outbox_emit_with_supabase():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"outbox_id": "o1"}])
    processor._supabase = mock_supabase

    await processor.emit("test.event", "skill", "abc", {"key": "val"})
    mock_supabase.table.assert_called_with("skill_event_outbox")
    mock_supabase.table.return_value.insert.assert_called_once()


@pytest.mark.asyncio
async def test_event_outbox_poll_once_no_data():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(data=[])
    processor._supabase = mock_supabase

    processed, failed = await processor.poll_once()
    assert processed == 0
    assert failed == 0


@pytest.mark.asyncio
async def test_event_outbox_poll_once_skip_scheduled():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    future_ms = 99999999999999
    mock_supabase.table.return_value.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
        data=[{"outbox_id": "o1", "event_type": "test", "aggregate_type": "skill", "aggregate_id": "abc", "payload": "{}", "headers": "{}", "retry_count": 0, "max_retries": 3, "scheduled_at": future_ms}]
    )
    processor._supabase = mock_supabase

    processed, failed = await processor.poll_once()
    assert processed == 0
    assert failed == 0


@pytest.mark.asyncio
async def test_event_outbox_poll_once_success():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
        data=[{"outbox_id": "o1", "event_type": "test.event", "aggregate_type": "skill", "aggregate_id": "abc", "payload": '{"key":"val"}', "headers": "{}", "retry_count": 0, "max_retries": 3, "scheduled_at": None}]
    )
    # Make the processing update return success
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    processor._supabase = mock_supabase

    processed, failed = await processor.poll_once()
    assert processed == 1
    assert failed == 0


@pytest.mark.asyncio
async def test_event_outbox_poll_once_processing_error():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()

    # Make the skill_events insert fail
    def insert_side_effect(data):
        if isinstance(data, dict) and data.get("event_id"):
            raise Exception("Event sourcing failed")
        return MagicMock(data=[{"outbox_id": "o1"}])

    mock_table = MagicMock()
    mock_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
        data=[{"outbox_id": "o1", "event_type": "test.event", "aggregate_type": "skill", "aggregate_id": "abc", "payload": "{}", "headers": "{}", "retry_count": 0, "max_retries": 3, "scheduled_at": None}]
    )
    # First update (mark processing) succeeds
    mock_table.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    # The insert into skill_events fails
    skill_events_mock = MagicMock()
    skill_events_mock.insert.return_value.execute.side_effect = Exception("Event sourcing failed")

    def table_side(tbl):
        if tbl == "skill_event_outbox":
            return mock_table
        elif tbl == "skill_events":
            return skill_events_mock
        return MagicMock()

    mock_supabase.table.side_effect = table_side
    processor._supabase = mock_supabase

    processed, failed = await processor.poll_once()
    assert processed == 0
    assert failed == 1


@pytest.mark.asyncio
async def test_event_outbox_poll_once_outer_exception():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = Exception("Outer error")
    processor._supabase = mock_supabase

    processed, failed = await processor.poll_once()
    assert processed == 0
    assert failed == 0


@pytest.mark.asyncio
async def test_event_outbox_dispatch_with_handlers():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    handler = AsyncMock()
    processor.register_handler("test.event", handler)

    await processor._dispatch({"event_type": "test.event", "data": {}})
    handler.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_outbox_dispatch_handler_error():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    handler = AsyncMock(side_effect=Exception("Handler error"))
    processor.register_handler("test.event", handler)

    await processor._dispatch({"event_type": "test.event", "data": {}})
    handler.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_outbox_route_to_webhooks():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"subscription_id": "sub-1", "event_types": ["test.event"], "url": "https://hooks.example.com", "headers": {}, "retry_policy": {"max_retries": 3}}]
    )
    processor._supabase = mock_supabase

    await processor._route_to_webhooks({"event_type": "test.event", "aggregate_type": "skill", "aggregate_id": "abc", "payload": "{}"}, mock_supabase)

    # Should have inserted into skill_webhook_queue
    mock_supabase.table.assert_called_with("skill_webhook_queue")


@pytest.mark.asyncio
async def test_event_outbox_route_to_webhooks_no_match():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"subscription_id": "sub-1", "event_types": ["other.event"], "url": "https://hooks.example.com", "headers": {}, "retry_policy": {}}]
    )
    processor._supabase = mock_supabase

    await processor._route_to_webhooks({"event_type": "test.event"}, mock_supabase)

    # No insert since event_types don't match


@pytest.mark.asyncio
async def test_event_outbox_route_to_webhooks_no_subs():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    processor._supabase = mock_supabase

    await processor._route_to_webhooks({"event_type": "test.event"}, mock_supabase)
    # exits early at line 260-261


@pytest.mark.asyncio
async def test_event_outbox_route_to_webhooks_exception():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Route error")
    processor._supabase = mock_supabase

    await processor._route_to_webhooks({"event_type": "test.event"}, mock_supabase)
    # exception caught at line 290-291


@pytest.mark.asyncio
async def test_event_outbox_reprocess_dead_letters():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"outbox_id": "dead1"}])
    processor._supabase = mock_supabase

    count = await processor.reprocess_dead_letters()
    assert count == 1


@pytest.mark.asyncio
async def test_event_outbox_reprocess_dead_letters_no_supabase():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    with patch("config.core.supabase.get_supabase_client", return_value=None):
        count = await processor.reprocess_dead_letters()
        assert count == 0


@pytest.mark.asyncio
async def test_event_outbox_get_queue_depth():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()

    def select_side(*a, **kw):
        m = MagicMock()
        m.count = 3
        return m

    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = select_side
    processor._supabase = mock_supabase

    stats = await processor.get_queue_depth()
    assert stats["pending"] == 3


@pytest.mark.asyncio
async def test_event_outbox_get_queue_depth_no_supabase():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    with patch("config.core.supabase.get_supabase_client", return_value=None):
        stats = await processor.get_queue_depth()
        assert stats["pending"] == 0


@pytest.mark.asyncio
async def test_event_outbox_get_queue_depth_exception():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = Exception("Stats error")
    processor._supabase = mock_supabase

    stats = await processor.get_queue_depth()
    assert stats["pending"] == -1


@pytest.mark.asyncio
async def test_event_outbox_background_polling():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    await processor.start_background_polling()
    assert processor._running is True
    assert processor._task is not None
    await processor.stop_background_polling()


@pytest.mark.asyncio
async def test_event_outbox_background_polling_with_data():
    import asyncio
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    processor.poll_once = AsyncMock(return_value=(2, 1))
    original_interval = processor.poll_interval
    processor.poll_interval = 0.01
    await processor.start_background_polling()
    await asyncio.sleep(0.05)
    await processor.stop_background_polling()
    processor.poll_interval = original_interval
    assert processor.poll_once.call_count >= 1


@pytest.mark.asyncio
async def test_event_outbox_background_polling_twice():
    from shared.utils.event_outbox import EventOutboxProcessor

    processor = EventOutboxProcessor()
    processor._running = True
    processor._task = AsyncMock()
    await processor.start_background_polling()


# ── Neo4j Sync Enabled Path Tests ──


@pytest.mark.asyncio
async def test_neo4j_initialize_with_config():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    mock_neo4j = MagicMock()
    mock_driver = MagicMock()
    mock_driver.close = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session.run = AsyncMock(return_value=MagicMock(__aiter__=lambda self: iter([])))
    mock_driver.session.return_value = mock_session_cm
    mock_neo4j.GraphDatabase.driver.return_value = mock_driver

    with patch.dict("os.environ", {"NEO4J_URI": "bolt://localhost:7687", "NEO4J_PASSWORD": "testpass"}):
        with patch.dict("sys.modules", {"neo4j": mock_neo4j}):
            await svc.initialize()
            assert svc._enabled is True
    await svc.close()


@pytest.mark.asyncio
async def test_neo4j_initialize_import_error():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    with patch.dict("os.environ", {"NEO4J_URI": "bolt://localhost:7687", "NEO4J_PASSWORD": "testpass"}):
        with patch.dict("sys.modules", {"neo4j": None}):
            await svc.initialize()
            assert svc._enabled is False


@pytest.mark.asyncio
async def test_neo4j_initialize_connection_error():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    mock_neo4j = MagicMock()
    mock_neo4j.GraphDatabase.driver.side_effect = Exception("Connection refused")

    with patch.dict("os.environ", {"NEO4J_URI": "bolt://localhost:7687", "NEO4J_PASSWORD": "testpass"}):
        with patch.dict("sys.modules", {"neo4j": mock_neo4j}):
            await svc.initialize()
            assert svc._enabled is False


@pytest.mark.asyncio
async def test_neo4j_sync_enabled_run():
    from shared.utils.neo4j_sync import Neo4jSyncService

    async def async_iter():
        yield {"skill_id": "s1"}

    svc = Neo4jSyncService()
    svc._enabled = True
    mock_driver = MagicMock()
    mock_session_cm = AsyncMock()
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session_cm.__aenter__.return_value = mock_session
    mock_driver.session.return_value = mock_session_cm

    mock_session.run = AsyncMock(return_value=MagicMock(__aiter__=lambda self: async_iter()))
    svc._driver = mock_driver

    result = await svc._run("MATCH (n) RETURN n")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_neo4j_sync_enabled_run_error_disables():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._retry_count = 5
    mock_driver = MagicMock()
    mock_session_cm = AsyncMock()
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session_cm.__aenter__.return_value = mock_session
    mock_driver.session.return_value = mock_session_cm
    mock_session.run.side_effect = Exception("Query failed")
    svc._driver = mock_driver

    result = await svc._run("MATCH (n) RETURN n")
    assert result == []
    assert svc._enabled is False


@pytest.mark.asyncio
async def test_neo4j_sync_skill_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_skill_node({"skill_id": "s1", "name": "Python", "slug": "python"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_category_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_category_node({"category_id": "c1", "name": "Backend"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_user_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_user_node({"id": "u1", "email": "test@example.com", "settings": {}})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_user_skill_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_user_skill_node({"user_skill_id": "us1", "user_id": "u1", "skill_id": "s1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_evidence_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_evidence_node({"evidence_id": "e1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_target_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_target_node({"target_id": "t1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_assessment_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_assessment_node({"assessment_id": "a1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_belongs_to():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_belongs_to({"skill_id": "s1", "category_id": "c1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_user_skill_edges():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_user_skill_edges({"user_id": "u1", "skill_id": "s1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_evidence_edges():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_evidence_edges({"evidence_id": "e1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_target_edges():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_target_edges({"target_id": "t1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_assessment_edges():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_assessment_edges({"assessment_id": "a1", "user_skill_id": "us1"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_sync_relationship_edge():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_relationship_edge({"from_skill_id": "s1", "to_skill_id": "s2", "relationship_type": "prerequisite"})
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_delete_node():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.delete_node("Skill", "skill_id", "s1")
    svc._run.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_bulk_sync_user_skills():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.bulk_sync_user_skills([{"user_skill_id": "us1", "user_id": "u1", "skill_id": "s1"}])
    assert svc._run.call_count >= 2


@pytest.mark.asyncio
async def test_neo4j_full_rebuild():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.full_rebuild(
        skills=[{"skill_id": "s1"}],
        categories=[{"category_id": "c1"}],
        relationships=[{"from_skill_id": "s1", "to_skill_id": "s2"}],
        user_skills=[{"user_skill_id": "us1", "user_id": "u1", "skill_id": "s1"}],
        evidence=[{"evidence_id": "e1", "user_skill_id": "us1"}],
        targets=[{"target_id": "t1", "user_skill_id": "us1"}],
        assessments=[{"assessment_id": "a1", "user_skill_id": "us1"}],
    )
    assert svc._run.call_count >= 5


@pytest.mark.asyncio
async def test_neo4j_find_related_skills():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[{"skill_id": "s2", "name": "Related", "depth": 1}])
    result = await svc.find_related_skills("s1")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_neo4j_recommend_skills():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[{"skill_id": "s2", "name": "Recommended", "connection_strength": 3}])
    result = await svc.recommend_skills("u1")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_neo4j_find_learning_path():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[{"skill_names": ["Python", "Django"], "skill_ids": ["s1", "s2"], "steps": 1}])
    result = await svc.find_learning_path("u1", "s2")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_neo4j_find_similar_users():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[{"similar_user_id": "u2", "common_skills": 5, "avg_level": 3.0}])
    result = await svc.find_similar_users("u1")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_neo4j_get_graph_statistics():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(side_effect=[
        [{"total_nodes": 10}],
        [{"total_relationships": 25}],
        [{"labels": ["Skill", "Category"], "count": 5}],
    ])
    stats = await svc.get_graph_statistics()
    assert stats["total_nodes"] == 10
    assert stats["total_relationships"] == 25


@pytest.mark.asyncio
async def test_neo4j_get_graph_statistics_empty():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    stats = await svc.get_graph_statistics()
    assert stats["total_nodes"] == 0


@pytest.mark.asyncio
async def test_neo4j_sync_belongs_to_no_category():
    from shared.utils.neo4j_sync import Neo4jSyncService

    svc = Neo4jSyncService()
    svc._enabled = True
    svc._run = AsyncMock(return_value=[])
    await svc.sync_belongs_to({"skill_id": "s1"})
    # Should not call _run since category_id is missing
    svc._run.assert_not_called()


# ── Redis Cache Enabled Path Tests ──


@pytest.mark.asyncio
async def test_redis_initialize_with_config():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await cache.initialize()
            assert cache._enabled is True
    await cache.close()


@pytest.mark.asyncio
async def test_redis_initialize_import_error():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
        with patch.dict("sys.modules", {"redis.asyncio": None}):
            await cache.initialize()
            assert cache._enabled is False


@pytest.mark.asyncio
async def test_redis_initialize_connection_error():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
        with patch("redis.asyncio.from_url", side_effect=Exception("Connection failed")):
            await cache.initialize()
            assert cache._enabled is False


@pytest.mark.asyncio
async def test_redis_health_check_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.health_check()
    assert result is True


@pytest.mark.asyncio
async def test_redis_health_check_disabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = False

    result = await cache.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_redis_health_check_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Ping failed")
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.health_check()
    assert result is False
    assert cache._enabled is False


@pytest.mark.asyncio
async def test_redis_get_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"data": "test"}'
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.get("test:key")
    assert result == {"data": "test"}


@pytest.mark.asyncio
async def test_redis_get_enabled_no_value():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.get("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_redis_get_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = Exception("Redis error")
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.get("fallback:key")
    assert result is None


@pytest.mark.asyncio
async def test_redis_set_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    cache._redis = mock_redis
    cache._enabled = True

    await cache.set("test:key", {"data": "test"}, ttl=60)
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_redis_set_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.setex.side_effect = Exception("Set error")
    cache._redis = mock_redis
    cache._enabled = True

    await cache.set("test:key", "value")
    # Falls back to memory cache, no exception


@pytest.mark.asyncio
async def test_redis_delete_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    cache._redis = mock_redis
    cache._enabled = True

    await cache.delete("test:key")
    mock_redis.delete.assert_called_once_with("test:key")


@pytest.mark.asyncio
async def test_redis_delete_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.delete.side_effect = Exception("Delete error")
    cache._redis = mock_redis
    cache._enabled = True

    await cache.delete("test:key")
    # Falls back to memory cache, no exception


@pytest.mark.asyncio
async def test_redis_exists_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 1
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.exists("test:key")
    assert result is True


@pytest.mark.asyncio
async def test_redis_exists_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.exists.side_effect = Exception("Exists error")
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.exists("test:key")
    assert result is False


@pytest.mark.asyncio
async def test_redis_ttl_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.ttl.return_value = 42
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.ttl("test:key")
    assert result == 42


@pytest.mark.asyncio
async def test_redis_ttl_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.ttl.side_effect = Exception("TTL error")
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.ttl("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_redis_expire_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    cache._redis = mock_redis
    cache._enabled = True

    await cache.expire("test:key", 60)
    mock_redis.expire.assert_called_once_with("test:key", 60)


@pytest.mark.asyncio
async def test_redis_expire_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.expire.side_effect = Exception("Expire error")
    cache._redis = mock_redis
    cache._enabled = True

    await cache.expire("test:key", 60)
    # Exception caught silently


@pytest.mark.asyncio
async def test_redis_invalidate_prefix_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    # scan returns (0, []) on first call to exit loop
    mock_redis.scan.return_value = (0, [])
    cache._redis = mock_redis
    cache._enabled = True

    await cache.invalidate_prefix("taxonomy")
    mock_redis.scan.assert_called_once()


@pytest.mark.asyncio
async def test_redis_invalidate_prefix_with_keys():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.scan.return_value = (0, ["skills:taxonomy:abc", "skills:taxonomy:def"])
    cache._redis = mock_redis
    cache._enabled = True

    await cache.invalidate_prefix("taxonomy")
    mock_redis.delete.assert_called_once_with("skills:taxonomy:abc", "skills:taxonomy:def")


@pytest.mark.asyncio
async def test_redis_invalidate_prefix_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.scan.side_effect = Exception("Scan error")
    cache._redis = mock_redis
    cache._enabled = True

    await cache.invalidate_prefix("taxonomy")
    # Exception caught silently, memory cache cleared


@pytest.mark.asyncio
async def test_redis_invalidate_all():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.scan.return_value = (0, [])
    cache._redis = mock_redis
    cache._enabled = True
    # Set something in memory cache so clearing is meaningful
    from shared.utils.cache import cache as memory_cache
    await memory_cache.set("test", 1)

    await cache.invalidate_all()
    mock_redis.scan.assert_called_once()


@pytest.mark.asyncio
async def test_redis_get_or_set_with_prefix():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = False  # Use memory fallback

    result = await cache.get_or_set("mykey", lambda: {"data": "computed"}, prefix="test_prefix")
    assert result == {"data": "computed"}


@pytest.mark.asyncio
async def test_redis_get_or_set_cached():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = False
    key = cache._make_key("test_prefix", "mykey")
    await cache.set(key, {"data": "cached"})

    result = await cache.get_or_set("mykey", lambda: {"data": "fresh"}, prefix="test_prefix")
    assert result == {"data": "cached"}


@pytest.mark.asyncio
async def test_redis_get_or_set_async_fn():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = False

    async def async_compute():
        return {"data": "async_computed"}

    result = await cache.get_or_set("akey", async_compute)
    assert result == {"data": "async_computed"}


@pytest.mark.asyncio
async def test_redis_bulk_get_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.mget.return_value = ['{"val": 1}', '{"val": 2}', None]
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.bulk_get(["k1", "k2", "k3"])
    assert result == {"k1": {"val": 1}, "k2": {"val": 2}}


@pytest.mark.asyncio
async def test_redis_bulk_get_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.mget.side_effect = Exception("MGET error")
    cache._redis = mock_redis
    cache._enabled = True

    result = await cache.bulk_get(["k1"])
    # Falls back to memory cache
    assert result == {}


@pytest.mark.asyncio
async def test_redis_bulk_set_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = MagicMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.__aenter__.return_value = mock_pipeline
    mock_redis.pipeline.return_value = mock_pipeline
    cache._redis = mock_redis
    cache._enabled = True

    await cache.bulk_set({"k1": "v1", "k2": "v2"}, ttl=60)
    assert mock_pipeline.setex.call_count >= 2
    mock_pipeline.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_redis_bulk_set_enabled_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = MagicMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.__aenter__.return_value = mock_pipeline
    mock_pipeline.setex.side_effect = Exception("Pipeline error")
    mock_redis.pipeline.return_value = mock_pipeline
    cache._redis = mock_redis
    cache._enabled = True

    await cache.bulk_set({"k1": "v1"})
    # Falls back to memory cache


@pytest.mark.asyncio
async def test_redis_get_stats_enabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.info.return_value = {"keyspace_hits": 100, "keyspace_misses": 20}
    cache._redis = mock_redis
    cache._enabled = True

    stats = await cache.get_stats()
    assert stats["enabled"] is True
    assert stats["backend"] == "redis"
    assert stats["hits"] == 100
    assert stats["hit_rate"] == 83.3


@pytest.mark.asyncio
async def test_redis_get_stats_disabled():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = False

    stats = await cache.get_stats()
    assert stats["enabled"] is False
    assert stats["backend"] == "memory"


@pytest.mark.asyncio
async def test_redis_get_stats_exception():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    mock_redis = AsyncMock()
    mock_redis.info.side_effect = Exception("Info error")
    cache._redis = mock_redis
    cache._enabled = True

    stats = await cache.get_stats()
    assert stats["enabled"] is True


@pytest.mark.asyncio
async def test_redis_make_key():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    key = cache._make_key("test", "arg1", "arg2")
    assert key.startswith("skills:test:")


@pytest.mark.asyncio
async def test_redis_make_raw_key():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    key = cache._make_raw_key(["user", "u1"])
    assert key == "skills:user:u1"


@pytest.mark.asyncio
async def test_redis_start_notify_listener():
    from shared.utils.redis_cache import RedisCacheLayer

    cache = RedisCacheLayer()
    cache._enabled = True
    cache._start_notify_listener()
    assert cache._notify_running is True
    # Second call should do nothing
    cache._start_notify_listener()
    assert cache._notify_running is True


# ── Webhook Delivery Tests ──


@pytest.mark.asyncio
async def test_webhook_background_polling():
    from shared.utils.webhook_delivery import WebhookDeliveryService

    svc = WebhookDeliveryService()
    await svc.start_background_polling()
    assert svc._running is True
    assert svc._task is not None
    await svc.stop_background_polling()


@pytest.mark.asyncio
async def test_webhook_background_polling_twice():
    from shared.utils.webhook_delivery import WebhookDeliveryService

    svc = WebhookDeliveryService()
    svc._running = True
    svc._task = AsyncMock()
    await svc.start_background_polling()


@pytest.mark.asyncio
async def test_webhook_background_polling_with_data():
    import asyncio
    from shared.utils.webhook_delivery import WebhookDeliveryService

    svc = WebhookDeliveryService()
    svc.poll_once = AsyncMock(return_value=(2, 1))
    original_interval = svc.poll_interval
    svc.poll_interval = 0.01
    await svc.start_background_polling()
    await asyncio.sleep(0.05)
    await svc.stop_background_polling()
    svc.poll_interval = original_interval
    assert svc.poll_once.call_count >= 1


@pytest.mark.asyncio
async def test_webhook_delivery_close():
    from shared.utils.webhook_delivery import WebhookDeliveryService

    svc = WebhookDeliveryService()
    mock_client = AsyncMock()
    svc._http_client = mock_client
    await svc.close()
    mock_client.aclose.assert_awaited_once()
    assert svc._http_client is None
