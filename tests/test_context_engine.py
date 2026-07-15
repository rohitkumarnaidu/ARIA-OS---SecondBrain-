import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestContextEngine:
    @pytest.fixture
    def mock_supabase(self):
        client = MagicMock()

        class _AutoBuilders(dict):
            def __missing__(self, key):
                val = MagicMock()
                val.execute.return_value = MagicMock(data=[], error=None)
                for m in ("select", "eq", "order", "limit", "gte", "lt", "range", "text_search"):
                    getattr(val, m).return_value = val
                self[key] = val
                return val

        builders = _AutoBuilders()

        def from_side(table):
            return builders[table]

        client.from_.side_effect = from_side
        client._builders = builders
        return client

    @pytest.fixture
    def engine(self, mock_supabase):
        from ai.context_engine import ContextEngine

        eng = ContextEngine(supabase_client=mock_supabase, cache_ttl=300)
        eng._cache.clear()
        return eng

    @pytest.mark.asyncio
    async def test_assemble_context_empty_needs(self, engine):
        result = await engine.assemble_context("user-1", [])
        assert result == ""

    @pytest.mark.asyncio
    async def test_assemble_context_unknown_need(self, engine):
        result = await engine.assemble_context("user-1", ["nonexistent_need"])
        assert result == ""

    @pytest.mark.asyncio
    async def test_assemble_context_with_data(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Finish report", "status": "pending"}]
        )
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert "Tasks Pending" in result
        assert "Finish report" in result

    @pytest.mark.asyncio
    async def test_assemble_context_multiple_needs(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Task A", "status": "pending"}]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[{"id": "g1", "title": "Goal A", "status": "active"}]
        )
        result = await engine.assemble_context("user-1", ["tasks_pending", "goals_active"])
        assert "Tasks Pending" in result
        assert "Goal A" in result

    @pytest.mark.asyncio
    async def test_cache_hit(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Cached task", "status": "pending"}]
        )
        result1 = await engine.assemble_context("user-1", ["tasks_pending"])
        assert "Cached task" in result1

        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t2", "title": "Different task", "status": "pending"}]
        )
        result2 = await engine.assemble_context("user-1", ["tasks_pending"])
        assert "Cached task" in result2
        assert "Different task" not in result2

    @pytest.mark.asyncio
    async def test_cache_invalidate_all(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "First", "status": "pending"}]
        )
        await engine.assemble_context("user-1", ["tasks_pending"])

        engine.invalidate_cache()
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t2", "title": "Second", "status": "pending"}]
        )
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert "Second" in result

    @pytest.mark.asyncio
    async def test_cache_invalidate_specific(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "First", "status": "pending"}]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[{"id": "g1", "title": "Goal", "status": "active"}]
        )
        await engine.assemble_context("user-1", ["tasks_pending", "goals_active"])

        engine.invalidate_cache("tasks_pending")
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t2", "title": "Refreshed", "status": "pending"}]
        )
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert "Refreshed" in result

    @pytest.mark.asyncio
    async def test_empty_data_handling(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert result == ""

    @pytest.mark.asyncio
    async def test_assemble_context_dict(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Dict task", "status": "pending"}]
        )
        result = await engine.assemble_context_dict("user-1", ["tasks_pending"])
        assert "tasks_pending" in result
        assert result["tasks_pending"][0]["title"] == "Dict task"

    @pytest.mark.asyncio
    async def test_assemble_context_dict_empty(self, engine):
        result = await engine.assemble_context_dict("user-1", ["nonexistent"])
        assert result == {}

    def test_estimate_tokens(self, engine):
        assert engine.estimate_tokens("hello world") == 3
        assert engine.estimate_tokens("a" * 100) == 26
        assert engine.estimate_tokens("") == 1

    def test_format_section(self, engine):
        data = [{"title": "Task A"}, {"title": "Task B"}]
        result = engine._format_section("tasks_pending", data)
        assert "=== Tasks Pending ===" in result
        assert "Task A" in result
        assert "Task B" in result

    def test_format_section_max_five_items(self, engine):
        data = [{"title": f"Task {i}"} for i in range(10)]
        result = engine._format_section("tasks_pending", data)
        lines = [l for l in result.split("\n") if l.startswith("  - ")]
        assert len(lines) == 5

    def test_format_section_fallback_labels(self, engine):
        data = [{"name": "My Habit"}, {"id": "some-id"}]
        result = engine._format_section("habits_today", data)
        assert "My Habit" in result
        assert "some-id" in result

    def test_format_section_empty_data(self, engine):
        data = [{"title": "Solo item"}]
        result = engine._format_section("goals_active", data)
        assert "=== Goals Active ===" in result
        assert "Solo item" in result

    def test_get_cache_stats_empty(self, engine):
        stats = engine.get_cache_stats()
        assert stats["size"] == 0
        assert stats["entries"] == {}

    @pytest.mark.asyncio
    async def test_get_cache_stats_with_entries(self, engine, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Stats check", "status": "pending"}]
        )
        await engine.assemble_context("user-1", ["tasks_pending"])
        stats = engine.get_cache_stats()
        assert stats["size"] == 1
        assert "tasks_pending" in stats["entries"]

    @pytest.mark.asyncio
    async def test_fetch_with_today_filter(self, engine, mock_supabase):

        today = datetime.now().strftime("%Y-%m-%d")
        mock_supabase._builders["habit_logs"].execute.return_value = MagicMock(
            data=[{"id": "h1", "name": "Morning jog", "date": today}]
        )
        result = await engine.assemble_context("user-1", ["habits_today"])
        assert "Morning jog" in result
        builder = mock_supabase._builders["habit_logs"]
        builder.eq.assert_any_call("date", today)

    @pytest.mark.asyncio
    async def test_fetch_with_order(self, engine, mock_supabase):
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[{"id": "s1", "name": "Sleep entry"}]
        )
        result = await engine.assemble_context("user-1", ["sleep_recent"])
        assert "Sleep entry" in result
        builder = mock_supabase._builders["sleep_logs"]
        builder.order.assert_called_once_with("date", desc=True)

    @pytest.mark.asyncio
    async def test_fetch_with_limit(self, engine, mock_supabase):
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(
            data=[{"id": "o1", "title": "Open opp"}]
        )
        result = await engine.assemble_context("user-1", ["opportunities_open"])
        assert "Open opp" in result
        builder = mock_supabase._builders["opportunities"]
        builder.limit.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_fetch_with_order_no_desc(self, engine, mock_supabase):
        from ai.context_engine import NEEDS_MAP

        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "t1", "title": "Ordered task"}]
        )
        with patch.dict(NEEDS_MAP, {"tasks_ordered": {"table": "tasks", "filter": {}, "order": "created_at", "limit": 5}}):
            engine._cache.clear()
            result = await engine.assemble_context("user-1", ["tasks_ordered"])
            assert "Ordered task" in result
            mock_supabase._builders["tasks"].order.assert_called_once_with("created_at", desc=False)

    @pytest.mark.asyncio
    async def test_fetch_supabase_exception_returns_empty(self, engine, mock_supabase):
        builder = mock_supabase._builders["tasks"]
        builder.execute.side_effect = Exception("DB connection timeout")
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert result == ""

    @pytest.mark.asyncio
    async def test_fetch_supabase_returns_none_instead_of_list(self, engine, mock_supabase):
        builder = mock_supabase._builders["tasks"]
        builder.execute.return_value = MagicMock(data=None)
        result = await engine.assemble_context("user-1", ["tasks_pending"])
        assert result == ""

    @pytest.mark.asyncio
    async def test_assemble_context_dict_with_unknown_need(self, engine):
        result = await engine.assemble_context_dict("user-1", ["nonexistent"])
        assert result == {}

    def test_needs_map_exists(self):
        from ai.context_engine import NEEDS_MAP

        assert "tasks_pending" in NEEDS_MAP
        assert "goals_active" in NEEDS_MAP
        assert "sleep_recent" in NEEDS_MAP
        assert len(NEEDS_MAP) >= 10
