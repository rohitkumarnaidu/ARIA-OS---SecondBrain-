"""Tests for AI supporting modules: context_assembly, sections, brave_search."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ═══════════════════════════════════════════════════════════════════════════════
# context_assembly.py — ContextAssembly class
# ═══════════════════════════════════════════════════════════════════════════════


class TestContextAssembly:
    """Test ContextAssembly: assemble, fetch, truncate, flatten."""

    @pytest.fixture
    def assembly(self):
        from ai.context_assembly import ContextAssembly

        return ContextAssembly(max_budget=2000, hard_cap=2500)

    def test_estimate_tokens(self, assembly):
        assert assembly.estimate_tokens("hello world") == 3
        assert assembly.estimate_tokens("a" * 100) == 26
        assert assembly.estimate_tokens("") == 1

    @pytest.mark.asyncio
    async def test_assemble_empty_sections(self, assembly):
        result = await assembly.assemble(user_id="user-1")
        assert result.sections == {}
        assert result.total_tokens == 0
        assert result.max_budget == 2000

    @pytest.mark.asyncio
    async def test_assemble_with_one_section(self, assembly):
        async def fetcher(uid):
            return [{"title": "Task 1", "status": "pending"}]

        def formatter(data):
            return "\n".join(f"- {t['title']}" for t in data)

        from ai.context_assembly import ContextSection

        section = ContextSection("tasks", 500, 1, fetcher, formatter, "No tasks")
        from ai.context_assembly import SECTIONS

        SECTIONS.insert(0, section)
        result = await assembly.assemble(user_id="user-1")
        assert "tasks" in result.sections
        assert "Task 1" in result.sections["tasks"]
        assert result.total_tokens > 0
        assert result.truncated == []
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_assemble_truncates_when_over_max_tokens(self, assembly):
        async def fetcher(uid):
            return [{"data": "x" * 500}]

        def formatter(data):
            return "x" * 2000 + "more content to be truncated"

        from ai.context_assembly import ContextSection

        section = ContextSection("large", 100, 1, fetcher, formatter, "fallback")
        from ai.context_assembly import SECTIONS

        SECTIONS.insert(0, section)
        result = await assembly.assemble(user_id="user-1")
        assert "large" in result.sections
        assert "[...truncated]" in result.sections["large"]
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_assemble_skips_when_over_hard_cap(self, assembly):
        """When total + new section tokens > hard_cap, section is truncated."""

        async def big_fetcher(uid):
            return [{"x": "y"}]

        def big_formatter(data):
            return "large block " * 1000

        async def small_fetcher(uid):
            return [{"a": "b"}]

        def small_formatter(data):
            return "small"

        from ai.context_assembly import ContextSection

        # Create assembly with tiny budget to force truncation
        small_assembly = __import__("ai.context_assembly", fromlist=["ContextAssembly"]).ContextAssembly(
            max_budget=5, hard_cap=10
        )
        from ai.context_assembly import SECTIONS

        SECTIONS.clear()
        SECTIONS.append(ContextSection("big", 500, 1, big_fetcher, big_formatter, "fallback"))
        SECTIONS.append(ContextSection("small", 500, 2, small_fetcher, small_formatter, "fallback"))

        result = await small_assembly.assemble(user_id="user-1")
        # "big" section consumes the budget, "small" should be in truncated
        assert "small" in result.truncated or "big" in result.truncated
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_fetch_section_returns_empty_on_error(self, assembly):
        async def failing_source(uid):
            raise ValueError("DB error")

        from ai.context_assembly import ContextSection

        failing_section = ContextSection("failing", 100, 1, failing_source, lambda d: "ok", "fallback")
        result = await assembly._fetch_section(failing_section, "user-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_section_returns_data(self, assembly):
        async def source(uid):
            return [{"id": 1}]

        from ai.context_assembly import ContextSection

        section = ContextSection("test", 100, 1, source, lambda d: "ok", "fallback")
        result = await assembly._fetch_section(section, "user-1")
        assert result == [{"id": 1}]

    def test_truncate_to_budget_shrinks_text(self, assembly):
        result = assembly._truncate_to_budget("Hello " * 100, budget=20)
        assert "[...truncated]" in result
        assert len(result) < len("Hello " * 100)

    def test_truncate_does_not_shrink_short_text(self, assembly):
        result = assembly._truncate_to_budget("Short text", budget=1000)
        assert result == "Short text"

    def test_flatten_with_truncated(self, assembly):
        from ai.context_assembly import AssembledContext

        ctx = AssembledContext(
            sections={"tasks": "- Task 1"},
            total_tokens=10,
            max_budget=2000,
            truncated=["goals", "habits"],
            assembled_at="2026-06-20T12:00:00",
        )
        result = assembly.flatten(ctx)
        assert "TASKS" in result
        assert "Task 1" in result
        assert "TRUNCATED" in result
        assert "goals" in result
        assert "habits" in result

    def test_flatten_without_truncated(self, assembly):
        from ai.context_assembly import AssembledContext

        ctx = AssembledContext(
            sections={"tasks": "- Task 1"},
            total_tokens=10,
            max_budget=2000,
            truncated=[],
            assembled_at="2026-06-20T12:00:00",
        )
        result = assembly.flatten(ctx)
        assert "TASKS" in result
        assert "TRUNCATED" not in result

    def test_flatten_multiple_sections(self, assembly):
        from ai.context_assembly import AssembledContext

        ctx = AssembledContext(
            sections={"tasks": "- Do work", "goals": "- Learn"},
            total_tokens=10,
            max_budget=2000,
            truncated=[],
            assembled_at="2026-06-20T12:00:00",
        )
        result = assembly.flatten(ctx)
        assert "TASKS" in result
        assert "GOALS" in result
        assert "Do work" in result
        assert "Learn" in result

    def test_assemble_context_dataclass(self):
        from ai.context_assembly import AssembledContext

        ctx = AssembledContext(sections={}, total_tokens=0, max_budget=1000, truncated=[], assembled_at="now")
        assert ctx.max_budget == 1000
        assert ctx.total_tokens == 0

    @pytest.mark.asyncio
    async def test_assemble_skips_sections_when_over_budget(self, assembly):
        async def fetcher(uid):
            return [{"content": "x"}]

        def formatter(data):
            return "big " * 2000  # ~1000 tokens

        from ai.context_assembly import ContextSection, SECTIONS

        SECTIONS.clear()

        # First section fills the budget
        SECTIONS.append(ContextSection("huge1", 10000, 1, fetcher, formatter, "fb"))
        SECTIONS.append(ContextSection("huge2", 10000, 2, fetcher, formatter, "fb"))

        tiny = __import__("ai.context_assembly", fromlist=["ContextAssembly"]).ContextAssembly(
            max_budget=500, hard_cap=600
        )
        result = await tiny.assemble(user_id="user-1")
        # huge1 goes over budget after first section
        assert len(result.truncated) > 0
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_assemble_truncates_at_budget_limit(self):
        def fetcher(uid):
            return [{"content": "x"}]

        def small_formatter(data):
            return "short " * 10  # ~25 tokens

        from ai.context_assembly import ContextSection, SECTIONS

        SECTIONS.clear()

        SECTIONS.append(ContextSection("small1", 10000, 1, fetcher, small_formatter, "fb"))
        SECTIONS.append(ContextSection("small2", 10000, 2, fetcher, small_formatter, "fb"))
        SECTIONS.append(ContextSection("small3", 10000, 3, fetcher, small_formatter, "fb"))

        tight = __import__("ai.context_assembly", fromlist=["ContextAssembly"]).ContextAssembly(
            max_budget=30, hard_cap=100
        )
        result = await tight.assemble(user_id="user-1")
        assert "small1" in result.sections
        assert "small2" in result.sections
        assert "small3" in result.truncated
        SECTIONS.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# sections.py — Section fetch functions and formatters
# ═══════════════════════════════════════════════════════════════════════════════


class TestSectionFetchers:
    """Test section data fetching functions."""

    @pytest.mark.asyncio
    async def test_fetch_tasks_returns_data(self):
        mock_client = MagicMock()
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"title": "Task 1", "status": "pending", "priority": "high", "due_date": "2026-06-20"}]
        )
        with patch("ai.sections.get_supabase_client", return_value=mock_client):
            from ai.sections import _fetch_tasks

            result = await _fetch_tasks("user-1")
            assert len(result) == 1
            assert result[0]["title"] == "Task 1"

    @pytest.mark.asyncio
    async def test_fetch_tasks_returns_empty_on_error(self):
        with patch("ai.sections.get_supabase_client", side_effect=Exception("DB down")):
            from ai.sections import _fetch_tasks

            result = await _fetch_tasks("user-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_goals_returns_data(self):
        mock_client = MagicMock()
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"title": "Goal 1", "status": "active", "progress": 50}]
        )
        with patch("ai.sections.get_supabase_client", return_value=mock_client):
            from ai.sections import _fetch_goals

            result = await _fetch_goals("user-1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_goals_empty_on_error(self):
        with patch("ai.sections.get_supabase_client", side_effect=Exception("error")):
            from ai.sections import _fetch_goals

            result = await _fetch_goals("user-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_courses_returns_data(self):
        mock_client = MagicMock()
        mock_client.from_.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[{"title": "CS 101", "status": "in_progress", "progress_percent": 30}])
        )
        with patch("ai.sections.get_supabase_client", return_value=mock_client):
            from ai.sections import _fetch_courses

            result = await _fetch_courses("user-1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_courses_empty_on_error(self):
        with patch("ai.sections.get_supabase_client", side_effect=Exception("error")):
            from ai.sections import _fetch_courses

            result = await _fetch_courses("user-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_habits_returns_data(self):
        mock_client = MagicMock()
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"name": "Exercise", "current_streak": 5, "is_active": True}]
        )
        with patch("ai.sections.get_supabase_client", return_value=mock_client):
            from ai.sections import _fetch_habits

            result = await _fetch_habits("user-1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_habits_empty_on_error(self):
        with patch("ai.sections.get_supabase_client", side_effect=Exception("error")):
            from ai.sections import _fetch_habits

            result = await _fetch_habits("user-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_sleep_returns_data(self):
        mock_client = MagicMock()
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"sleep_score": 85, "duration_hours": 7.5, "date": "2026-06-20"}]
        )
        with patch("ai.sections.get_supabase_client", return_value=mock_client):
            from ai.sections import _fetch_sleep

            result = await _fetch_sleep("user-1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_sleep_empty_on_error(self):
        with patch("ai.sections.get_supabase_client", side_effect=Exception("error")):
            from ai.sections import _fetch_sleep

            result = await _fetch_sleep("user-1")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_memory_returns_data(self):
        with patch("ai.sections.get_memory_summary", new=AsyncMock(return_value={"summary": "Focused on Python"})):
            from ai.sections import _fetch_memory

            result = await _fetch_memory("user-1")
            assert result == {"summary": "Focused on Python"}

    @pytest.mark.asyncio
    async def test_fetch_memory_empty_on_error(self):
        with patch("ai.sections.get_memory_summary", side_effect=Exception("error")):
            from ai.sections import _fetch_memory

            result = await _fetch_memory("user-1")
            assert result == {}


class TestSectionFormatters:
    """Test section formatter functions."""

    def test_fmt_tasks_with_data(self):
        from ai.sections import _fmt_tasks

        result = _fmt_tasks([{"title": "Work", "priority": "high"}, {"title": "Read", "priority": "low"}])
        assert "Work" in result
        assert "high" in result
        assert "Read" in result
        assert result.count("\n") == 1

    def test_fmt_tasks_empty(self):
        from ai.sections import _fmt_tasks

        assert _fmt_tasks([]) == "No pending tasks."
        assert _fmt_tasks(None) == "No pending tasks."

    def test_fmt_goals_with_data(self):
        from ai.sections import _fmt_goals

        result = _fmt_goals([{"title": "Learn", "progress": 75}])
        assert "Learn" in result
        assert "75%" in result

    def test_fmt_goals_empty(self):
        from ai.sections import _fmt_goals

        assert _fmt_goals([]) == "No active goals."
        assert _fmt_goals(None) == "No active goals."

    def test_fmt_courses_with_active(self):
        from ai.sections import _fmt_courses

        result = _fmt_courses(
            [
                {"title": "Python", "status": "in_progress", "progress_percent": 50},
                {"title": "Done", "status": "completed", "progress_percent": 100},
            ]
        )
        assert "Python" in result
        assert "50%" in result
        assert "Done" not in result

    def test_fmt_courses_no_active(self):
        from ai.sections import _fmt_courses

        result = _fmt_courses([{"title": "Done", "status": "completed"}])
        assert result == "No courses in progress."

    def test_fmt_courses_empty(self):
        from ai.sections import _fmt_courses

        assert _fmt_courses([]) == "No courses in progress."

    def test_fmt_habits_with_data(self):
        from ai.sections import _fmt_habits

        result = _fmt_habits([{"name": "Run", "current_streak": 10}])
        assert "Run" in result
        assert "10d" in result

    def test_fmt_habits_empty(self):
        from ai.sections import _fmt_habits

        assert _fmt_habits([]) == "No active habits."

    def test_fmt_sleep_with_data(self):
        from ai.sections import _fmt_sleep

        result = _fmt_sleep([{"sleep_score": 90, "duration_hours": 8}])
        assert "90" in result
        assert "8h" in result

    def test_fmt_sleep_empty(self):
        from ai.sections import _fmt_sleep

        assert _fmt_sleep([]) == "No sleep data yet."

    def test_fmt_memory_dict(self):
        from ai.sections import _fmt_memory

        result = _fmt_memory({"summary": "Focused on work"})
        assert "Focused on work" in result

    def test_fmt_memory_non_dict(self):
        from ai.sections import _fmt_memory

        result = _fmt_memory("raw string")
        assert result == "No memory data."

    def test_fmt_memory_empty_dict(self):
        from ai.sections import _fmt_memory

        result = _fmt_memory({})
        assert "No memory summary" in result


class TestRegisterDefaultSections:
    """Test register_default_sections populates correctly."""

    def test_registers_all_sections(self):
        from ai.sections import register_default_sections
        from ai.context_assembly import SECTIONS

        SECTIONS.clear()
        register_default_sections()
        names = [s.name for s in SECTIONS]
        assert "tasks" in names
        assert "goals" in names
        assert "courses" in names
        assert "habits" in names
        assert "sleep" in names
        assert "memory" in names
        assert len(SECTIONS) == 6
        SECTIONS.clear()

    def test_sections_sorted_by_priority(self):
        from ai.sections import register_default_sections
        from ai.context_assembly import SECTIONS

        SECTIONS.clear()
        register_default_sections()
        for i in range(len(SECTIONS) - 1):
            assert SECTIONS[i].priority <= SECTIONS[i + 1].priority
        SECTIONS.clear()

    def test_register_clears_existing(self):
        from ai.sections import register_default_sections
        from ai.context_assembly import SECTIONS

        SECTIONS.clear()
        from ai.context_assembly import ContextSection

        async def src(u):
            return []

        SECTIONS.append(ContextSection("extra", 100, 99, src, lambda d: "", ""))
        assert len(SECTIONS) == 1
        register_default_sections()
        assert "extra" not in [s.name for s in SECTIONS]
        assert len(SECTIONS) == 6
        SECTIONS.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# brave_search.py — Web search for opportunities
# ═══════════════════════════════════════════════════════════════════════════════


class TestBraveSearch:
    """Test brave_search function and opportunity fetching."""

    @pytest.mark.asyncio
    async def test_brave_search_returns_empty_when_no_key(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = None
            from ai.brave_search import brave_search

            result = await brave_search("test query")
            assert result == []

    def _make_brave_get_mock(self, status=200, json_data=None):
        """Create proper aiohttp mock for `async with session.get(...) as resp:`.

        aiohttp.ClientSession.get() returns a ClientResponse which is an async
        context manager. We patch ClientSession.get directly.
        """
        if json_data is None:
            json_data = {}
        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.json = AsyncMock(return_value=json_data)
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_resp)
        return mock_get

    @pytest.mark.asyncio
    async def test_brave_search_success(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_brave_get_mock(
                json_data={
                    "web": {
                        "results": [
                            {
                                "title": "MLH Fellowship 2026",
                                "url": "https://mlh.io",
                                "description": "Remote fellowship",
                                "age": "2 days ago",
                            },
                            {
                                "title": "GSoC 2026",
                                "url": "https://summerofcode.withgoogle.com",
                                "description": "Open source",
                                "age": "1 week ago",
                            },
                        ]
                    }
                }
            )
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import brave_search

                results = await brave_search("internship 2026")
                assert len(results) == 2
                assert results[0]["title"] == "MLH Fellowship 2026"
                assert results[1]["title"] == "GSoC 2026"

    @pytest.mark.asyncio
    async def test_brave_search_non_200_status(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_brave_get_mock(status=429)
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import brave_search

                results = await brave_search("test")
                assert results == []

    @pytest.mark.asyncio
    async def test_brave_search_network_error(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(side_effect=Exception("Network error"))
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import brave_search

                results = await brave_search("test")
                assert results == []

    @pytest.mark.asyncio
    async def test_brave_search_empty_results(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_brave_get_mock(json_data={"web": {"results": []}})
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import brave_search

                results = await brave_search("test")
                assert results == []

    @pytest.mark.asyncio
    async def test_brave_search_no_web_key_in_response(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_brave_get_mock(json_data={"web": {}})
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import brave_search

                results = await brave_search("test")
                assert results == []


class TestFetchOpportunitiesFromWeb:
    """Test fetch_opportunities_from_web orchestration."""

    def _make_opp_get_mock(self, results):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"web": {"results": results}})
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_resp)
        return mock_get

    @pytest.mark.asyncio
    async def test_fetch_opportunities_with_results(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_opp_get_mock(
                [
                    {
                        "title": "SWE Intern",
                        "url": "https://example.com/intern",
                        "description": "Software engineering internship",
                        "age": "3 days ago",
                    },
                ]
            )
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import fetch_opportunities_from_web

                results = await fetch_opportunities_from_web(["Python"], ["AI", "Web"])
                assert len(results) > 0
                assert results[0]["category"] in [
                    "internships",
                    "hackathons",
                    "open_source",
                    "startup_competitions",
                    "fellowships",
                    "freelance",
                ]
                assert results[0]["source"] == "brave_search"
                assert "skills_needed" in results[0]
                assert "match_score" in results[0]

    @pytest.mark.asyncio
    async def test_fetch_opportunities_deduplicates_urls(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_opp_get_mock(
                [
                    {
                        "title": "Duplicate",
                        "url": "https://example.com/dup",
                        "description": "Same URL",
                        "age": "1 day ago",
                    },
                ]
            )
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import fetch_opportunities_from_web

                results = await fetch_opportunities_from_web(["Python"], ["AI"])
                assert len(results) <= 20

    @pytest.mark.asyncio
    async def test_fetch_opportunities_caps_at_20(self):
        with patch("ai.brave_search.settings") as mock_settings:
            mock_settings.brave_api_key = "test-key"
            mock_get = self._make_opp_get_mock(
                [
                    {
                        "title": f"Result {i}",
                        "url": f"https://example.com/{i}",
                        "description": f"Desc {i}",
                        "age": "1 day ago",
                    }
                    for i in range(5)
                ]
            )
            with patch("aiohttp.ClientSession.get", return_value=mock_get):
                from ai.brave_search import fetch_opportunities_from_web

                results = await fetch_opportunities_from_web(["Python"], ["AI"])
                assert len(results) <= 20


class TestLearningAgentEdgeCases:

    @pytest.mark.asyncio
    async def test_detect_patterns_llm_unavailable(self):
        from ai.agents.learning_agent import detect_learning_patterns
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.learning_agent.track_user_progress", return_value={}):
            with patch("ai.agents.learning_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
                result = await detect_learning_patterns("user-1")
                assert isinstance(result, list)
                assert "Keep up" in result[0]

    @pytest.mark.asyncio
    async def test_suggest_focus_llm_unavailable(self):
        from ai.agents.learning_agent import suggest_learning_focus
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.learning_agent.detect_learning_patterns", return_value=["pattern1"]):
            with patch("ai.agents.learning_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
                result = await suggest_learning_focus("user-1")
                assert "patterns" in result
                assert "recommendations" in result
                assert "Stay consistent" in result["recommendations"][0]


# =============================================================================
# orchestrator.py — 5 main functions with LLM + DB + fallback paths
# =============================================================================


class TestOrchestrator:

    # ─── orchestrator.mock_helpers ─────────────────────────────────────────

    @staticmethod
    def _build_execute(data=None, err=None):
        return MagicMock(data=data or [], error=err)

    @staticmethod
    def _mock_supabase(mocker):
        class _AutoBuilders(dict):
            def __missing__(self, key):
                b = MagicMock()
                b.execute.return_value = TestOrchestrator._build_execute()
                for c in ("select", "eq", "order", "limit", "in_", "ilike", "gte", "lt", "range"):
                    getattr(b, c).return_value = b
                b.insert.return_value = MagicMock(execute=MagicMock(return_value=TestOrchestrator._build_execute([{}])))
                b.update.return_value = b

                def _delete_side():
                    db = MagicMock()
                    db.eq.return_value = db
                    db.execute.return_value = TestOrchestrator._build_execute([{}])
                    return db

                b.delete.side_effect = _delete_side
                self[key] = b
                return b

        builders = _AutoBuilders()
        client = MagicMock()
        client.from_.side_effect = lambda n: builders[n]
        client._builders = builders
        mocker.patch("ai.orchestrator.get_supabase_client", return_value=client)
        return client

    # ─── orchestrate_plan ──────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_orchestrate_plan_success(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Write",
                    "status": "pending",
                    "priority": "high",
                    "category": "work",
                    "due_date": "2026-07-01",
                }
            ]
        )
        client._builders["goals"].execute.return_value = MagicMock(
            data=[{"id": "g1", "title": "Learn AI", "status": "active", "target_date": "2026-12-01"}]
        )
        client._builders["courses"].execute.return_value = MagicMock(
            data=[{"id": "c1", "name": "ML 101", "status": "in_progress"}]
        )

        mock_prompt = MagicMock()
        mock_prompt.system_prompt = "You are a planner."
        with patch("ai.orchestrator.prompts.get_agent", return_value=mock_prompt):
            with patch(
                "ai.orchestrator.llm.generate_json",
                new=AsyncMock(
                    return_value={
                        "steps": [{"action": "study", "target": "ML", "reasoning": "Good", "confidence": 0.8}],
                        "summary": "Study ML",
                    }
                ),
            ):
                from ai.orchestrator import orchestrate_plan

                result = await orchestrate_plan("user-1", "help me study")
                assert result["summary"] == "Study ML"
                assert len(result["steps"]) == 1

    @pytest.mark.asyncio
    async def test_orchestrate_plan_no_prompt(self, mocker):
        self._mock_supabase(mocker)
        with patch("ai.orchestrator.prompts.get_agent", return_value=None):
            with patch(
                "ai.orchestrator.llm.generate_json",
                new=AsyncMock(
                    return_value={
                        "steps": [],
                        "summary": "Fallback plan",
                    }
                ),
            ):
                from ai.orchestrator import orchestrate_plan

                result = await orchestrate_plan("user-1", "plan")
                assert result["summary"] == "Fallback plan"

    @pytest.mark.asyncio
    async def test_orchestrate_plan_data_fetch_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.side_effect = Exception("DB down")
        with patch(
            "ai.orchestrator.llm.generate_json",
            new=AsyncMock(
                return_value={
                    "steps": [],
                    "summary": "ok",
                }
            ),
        ):
            from ai.orchestrator import orchestrate_plan

            result = await orchestrate_plan("user-1", "x")
            assert "steps" in result

    @pytest.mark.asyncio
    async def test_orchestrate_plan_llm_unavailable(self, mocker):
        self._mock_supabase(mocker)
        from ai.client import LLMProviderUnavailableError

        with patch("ai.orchestrator.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            from ai.orchestrator import orchestrate_plan

            result = await orchestrate_plan("user-1", "x")
            assert len(result["steps"]) > 0
            assert "Fallback" in result["steps"][0]["reasoning"]

    @pytest.mark.asyncio
    async def test_orchestrate_plan_steps_not_list(self, mocker):
        self._mock_supabase(mocker)
        with patch(
            "ai.orchestrator.llm.generate_json",
            new=AsyncMock(
                return_value={
                    "steps": "not a list",
                    "summary": "oops",
                }
            ),
        ):
            from ai.orchestrator import orchestrate_plan

            result = await orchestrate_plan("user-1", "x")
            assert result["steps"] == []

    # ─── search_memory ─────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_search_memory_success(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "note",
                    "key": "python",
                    "value": "Learning Python",
                    "importance": "high",
                    "tags": ["code"],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        client._builders["tasks"].execute.return_value = MagicMock(data=[])  # for get_user_preferences
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["goals"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])

        with patch("ai.orchestrator.llm.generate", new=AsyncMock(return_value="User is learning Python.")):
            from ai.orchestrator import search_memory

            result = await search_memory("user-1", "python")
            assert len(result["memories"]) == 1
            assert result["summary"] == "User is learning Python."

    @pytest.mark.asyncio
    async def test_search_memory_fetch_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.side_effect = Exception("DB error")
        with patch("ai.orchestrator.llm.generate", new=AsyncMock(return_value="")):
            from ai.orchestrator import search_memory

            result = await search_memory("user-1", "x")
            assert result["memories"] == []

    @pytest.mark.asyncio
    async def test_search_memory_prefs_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.return_value = MagicMock(data=[])
        with patch("ai.agents.memory_agent.get_user_preferences", new=AsyncMock(side_effect=Exception("prefs fail"))):
            with patch("ai.orchestrator.llm.generate", new=AsyncMock(return_value="")):
                from ai.orchestrator import search_memory

                result = await search_memory("user-1", "x")
                assert result["preferences"]["preferred_category"] == "personal"

    @pytest.mark.asyncio
    async def test_search_memory_llm_unavailable(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "note",
                    "key": "python",
                    "value": "Learning",
                    "importance": "high",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        client._builders["tasks"].execute.return_value = MagicMock(data=[])
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["goals"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        from ai.client import LLMProviderUnavailableError

        with patch("ai.orchestrator.llm.generate", side_effect=LLMProviderUnavailableError("down")):
            from ai.orchestrator import search_memory

            result = await search_memory("user-1", "python")
            assert result["summary"] == ""

    @pytest.mark.asyncio
    async def test_search_memory_no_prompt(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.return_value = MagicMock(data=[])
        client._builders["tasks"].execute.return_value = MagicMock(data=[])
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["goals"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.prompts.get_agent", return_value=None):
            with patch("ai.orchestrator.llm.generate", new=AsyncMock(return_value="inline")):
                from ai.orchestrator import search_memory

                result = await search_memory("user-1", "x")
                assert result["summary"] == "inline"

    @pytest.mark.asyncio
    async def test_search_memory_no_match(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "note",
                    "key": "other",
                    "value": "Other",
                    "importance": "low",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        client._builders["tasks"].execute.return_value = MagicMock(data=[])
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["goals"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.llm.generate", new=AsyncMock(return_value="")):
            from ai.orchestrator import search_memory

            result = await search_memory("user-1", "query-no-match")
            assert len(result["memories"]) == 1  # falls back to top 20

    # ─── detect_patterns ───────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_detect_patterns_success(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Work",
                    "status": "completed",
                    "priority": "high",
                    "category": "study",
                    "created_at": "2026-06-01T00:00:00",
                    "completed_at": "2026-06-02T00:00:00",
                },
                {
                    "id": "t2",
                    "title": "Task2",
                    "status": "pending",
                    "priority": "low",
                    "category": "personal",
                    "created_at": "2026-06-01T00:00:00",
                    "completed_at": None,
                },
            ]
        )
        client._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Read",
                    "is_active": True,
                    "current_streak": 10,
                    "best_streak": 20,
                    "consistency_percentage": 80,
                }
            ]
        )
        client._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[{"date": "2026-06-20", "sleep_score": 85, "duration_hours": 8}]
        )
        client._builders["time_entries"].execute.return_value = MagicMock(
            data=[
                {
                    "duration_minutes": 120,
                    "is_deep_work": True,
                    "category": "coding",
                    "start_time": "2026-06-20T09:00:00",
                }
            ]
        )
        with patch(
            "ai.orchestrator.llm.generate_json",
            new=AsyncMock(
                return_value={
                    "insights": [{"type": "good", "description": "Keep it up", "confidence": 0.8, "data": {}}]
                }
            ),
        ):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "how am I doing")
            assert len(result["patterns"]) == 5
            assert len(result["insights"]) == 1

    @pytest.mark.asyncio
    async def test_detect_patterns_data_fetch_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.side_effect = Exception("DB error")
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"insights": []})):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "x")
            assert result["patterns"][0]["confidence"] == 0.8

    @pytest.mark.asyncio
    async def test_detect_patterns_llm_unavailable(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "W",
                    "status": "completed",
                    "priority": "low",
                    "category": "work",
                    "created_at": "2026-01-01T00:00:00",
                    "completed_at": "2026-01-02T00:00:00",
                }
            ]
        )
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["sleep_logs"].execute.return_value = MagicMock(data=[])
        client._builders["time_entries"].execute.return_value = MagicMock(data=[])
        from ai.client import LLMProviderUnavailableError

        with patch("ai.orchestrator.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "x")
            # 1 completed out of 1 = 100% → no productivity_warning
            assert len(result["insights"]) == 0

    @pytest.mark.asyncio
    async def test_detect_patterns_no_prompt(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(data=[])
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["sleep_logs"].execute.return_value = MagicMock(data=[])
        client._builders["time_entries"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.prompts.get_agent", return_value=None):
            with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"insights": []})):
                from ai.orchestrator import detect_patterns

                result = await detect_patterns("user-1", "x")
                assert len(result["patterns"]) == 5

    @pytest.mark.asyncio
    async def test_detect_patterns_insight_as_string(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "W",
                    "status": "completed",
                    "priority": "low",
                    "category": "work",
                    "created_at": "2026-01-01T00:00:00",
                    "completed_at": "2026-01-02T00:00:00",
                }
            ]
        )
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["sleep_logs"].execute.return_value = MagicMock(data=[])
        client._builders["time_entries"].execute.return_value = MagicMock(data=[])
        with patch(
            "ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"insights": "Just a string insight"})
        ):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "x")
            assert len(result["insights"]) == 1
            assert result["insights"][0]["type"] == "llm_insight"

    @pytest.mark.asyncio
    async def test_detect_patterns_insight_wrong_type(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "W",
                    "status": "completed",
                    "priority": "low",
                    "category": "work",
                    "created_at": "2026-01-01T00:00:00",
                    "completed_at": "2026-01-02T00:00:00",
                }
            ]
        )
        client._builders["habits"].execute.return_value = MagicMock(data=[])
        client._builders["sleep_logs"].execute.return_value = MagicMock(data=[])
        client._builders["time_entries"].execute.return_value = MagicMock(data=[])
        with patch(
            "ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"insights": 42})  # not a list or string
        ):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "x")
            assert result["insights"] == []

    @pytest.mark.asyncio
    async def test_detect_patterns_triggers_low_insights(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "W",
                    "status": "pending",
                    "priority": "low",
                    "category": "personal",
                    "created_at": "2026-01-01T00:00:00",
                    "completed_at": None,
                }
            ]
        )
        client._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Read",
                    "is_active": True,
                    "current_streak": 1,
                    "best_streak": 5,
                    "consistency_percentage": 30,
                }
            ]
        )
        client._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[{"date": "2026-01-01", "sleep_score": 60, "duration_hours": 5}]
        )
        client._builders["time_entries"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"insights": []})):
            from ai.orchestrator import detect_patterns

            result = await detect_patterns("user-1", "x")
            insight_types = [i["type"] for i in result["insights"]]
            assert "productivity_warning" in insight_types
            assert "sleep_improvement" in insight_types

    # ─── match_opportunities ──────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_match_opportunities_success(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "o1",
                    "title": "ML Course",
                    "match_score": 0.9,
                    "status": "new",
                    "category": "course",
                    "created_at": "2026-06-01T00:00:00",
                }
            ]
        )
        client._builders["courses"].execute.return_value = MagicMock(
            data=[{"name": "AI", "skills": ["python", "ml"], "status": "completed"}]
        )
        client._builders["roadmap"].execute.return_value = MagicMock(
            data=[{"skill_name": "deep learning", "status": "in_progress"}]
        )
        with patch(
            "ai.orchestrator.llm.generate_json",
            new=AsyncMock(
                return_value={"matches": [{"id": "o1", "title": "ML Course", "score": 0.95, "reasoning": "Great fit"}]}
            ),
        ):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "find courses")
            assert len(result["matches"]) == 1
            assert "Matched" in result["summary"]

    @pytest.mark.asyncio
    async def test_match_opportunities_fetch_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.side_effect = Exception("DB error")
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"matches": []})):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "x")
            assert result["matches"] == []

    @pytest.mark.asyncio
    async def test_match_opportunities_skills_as_string(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(
            data=[{"name": "AI", "skills": "python,ml", "status": "completed"}]
        )
        client._builders["roadmap"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"matches": []})):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "x")
            assert "matches" in result

    @pytest.mark.asyncio
    async def test_match_opportunities_skills_fetch_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.side_effect = Exception("skills fail")
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"matches": []})):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "x")
            assert "matches" in result

    @pytest.mark.asyncio
    async def test_match_opportunities_llm_unavailable(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "o1",
                    "title": "Course",
                    "match_score": 0.8,
                    "status": "new",
                    "category": "tech",
                    "created_at": "2026-06-01T00:00:00",
                }
            ]
        )
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        client._builders["roadmap"].execute.return_value = MagicMock(data=[])
        from ai.client import LLMProviderUnavailableError

        with patch("ai.orchestrator.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "x")
            assert len(result["matches"]) == 1

    @pytest.mark.asyncio
    async def test_match_opportunities_no_prompt(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        client._builders["roadmap"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.prompts.get_agent", return_value=None):
            with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"matches": []})):
                from ai.orchestrator import match_opportunities

                result = await match_opportunities("user-1", "x")
                assert result["matches"] == []

    @pytest.mark.asyncio
    async def test_match_opportunities_not_a_list(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["opportunities"].execute.return_value = MagicMock(data=[])
        client._builders["courses"].execute.return_value = MagicMock(data=[])
        client._builders["roadmap"].execute.return_value = MagicMock(data=[])
        with patch("ai.orchestrator.llm.generate_json", new=AsyncMock(return_value={"matches": "not a list"})):
            from ai.orchestrator import match_opportunities

            result = await match_opportunities("user-1", "x")
            assert result["matches"] == []

    # ─── execute_action ────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_execute_action_create_task(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "new"}], error=None))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "Buy groceries")
        assert result["action"] == "create_task"
        assert "Created task" in result["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_create_task_db_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[], error=MagicMock(message="insert failed")))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "Buy")
        assert result["action"] == "noop"

    @pytest.mark.asyncio
    async def test_execute_action_update_task_all_fields(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action(
            "user-1",
            "update",
            {
                "action": "update_task",
                "task_id": "t1",
                "title": "New",
                "status": "completed",
                "priority": "high",
            },
        )
        assert result["action"] == "update_task"

    @pytest.mark.asyncio
    async def test_execute_action_update_task(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action(
            "user-1", "update task", {"action": "update_task", "task_id": "t1", "title": "New"}
        )
        assert result["action"] == "update_task"

    @pytest.mark.asyncio
    async def test_execute_action_update_task_no_id(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "new"}], error=None))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "update", {"action": "update_task"})
        assert result["action"] == "create_task"

    @pytest.mark.asyncio
    async def test_execute_action_complete_task(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "complete", {"action": "complete_task", "task_id": "t1"})
        assert result["action"] == "complete_task"

    @pytest.mark.asyncio
    async def test_execute_action_complete_task_search(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "complete homework", {"action": "complete_task"})
        assert result["action"] == "complete_task"

    @pytest.mark.asyncio
    async def test_execute_action_complete_task_not_found(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "complete nonexistent", {"action": "complete_task"})
        assert "not found" in result["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_create_habit_log(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["habits"].execute.return_value = MagicMock(data=[{"id": "h1"}], error=None)
        client._builders["habit_logs"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "hl1"}], error=None))
        )
        from ai.orchestrator import execute_action

        result = await execute_action(
            "user-1", "log habit exercise", {"action": "create_habit_log", "habit_name": "exercise"}
        )
        assert result["action"] == "create_habit_log"

    @pytest.mark.asyncio
    async def test_execute_action_create_habit_log_not_found(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["habits"].execute.return_value = MagicMock(data=[], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "log habit bad", {"action": "create_habit_log"})
        assert "not found" in result["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_delete_task(self, mocker):
        client = self._mock_supabase(mocker)
        del_qb = MagicMock()
        del_qb.eq.return_value = del_qb
        del_qb.execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        client._builders["tasks"].delete.side_effect = None
        client._builders["tasks"].delete.return_value = del_qb
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "delete", {"action": "delete_task", "task_id": "t1"})
        assert result["action"] == "delete_task"

    @pytest.mark.asyncio
    async def test_execute_action_update_task_db_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=MagicMock(message="update failed"))
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "update", {"action": "update_task", "task_id": "t1"})
        assert result["action"] == "noop"

    @pytest.mark.asyncio
    async def test_execute_action_complete_task_db_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=MagicMock(message="complete failed"))
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "complete", {"action": "complete_task", "task_id": "t1"})
        assert result["action"] == "noop"

    @pytest.mark.asyncio
    async def test_execute_action_habit_log_db_error(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["habits"].execute.return_value = MagicMock(data=[{"id": "h1"}], error=None)
        client._builders["habit_logs"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[], error=MagicMock(message="insert failed")))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "log habit run", {"action": "create_habit_log", "habit_name": "run"})
        assert result["action"] == "noop"

    @pytest.mark.asyncio
    async def test_execute_action_delete_task_db_error(self, mocker):
        client = self._mock_supabase(mocker)
        del_qb = MagicMock()
        del_qb.eq.return_value = del_qb
        del_qb.execute.return_value = MagicMock(data=[], error=MagicMock(message="delete failed"))
        client._builders["tasks"].delete.side_effect = None
        client._builders["tasks"].delete.return_value = del_qb
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "delete", {"action": "delete_task", "task_id": "t1"})
        assert result["action"] == "noop"

    @pytest.mark.asyncio
    async def test_execute_action_delete_task_not_found(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=None)
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "delete", {"action": "delete_task"})
        assert "not found" in result["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_action_from_context(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "n"}], error=None))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "some query", {"action": "create_task", "title": "Explicit"})
        assert "Explicit" in result["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_query_prefixes(self, mocker):
        client = self._mock_supabase(mocker)
        from ai.orchestrator import execute_action

        # update prefix
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        r = await execute_action("user-1", "update my task", {"task_id": "t1", "title": "New"})
        assert r["action"] == "update_task"

        # complete prefix → no task_id → search → found → complete
        client._builders["tasks"].execute.return_value = MagicMock(data=[{"id": "t1"}], error=None)
        client._builders["tasks"].update.return_value = client._builders["tasks"]
        r = await execute_action("user-1", "complete my task")
        assert r["action"] == "complete_task"

        # log habit prefix
        client._builders["habits"].execute.return_value = MagicMock(data=[{"id": "h1"}], error=None)
        client._builders["habit_logs"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "hl1"}], error=None))
        )
        r = await execute_action("user-1", "log habit reading")
        assert r["action"] == "create_habit_log"

        # delete prefix → no task_id → search → not found
        client._builders["tasks"].execute.return_value = MagicMock(data=[], error=None)
        r = await execute_action("user-1", "delete old_task")
        assert "not found" in r["summary"]

    @pytest.mark.asyncio
    async def test_execute_action_else_falls_to_create(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.return_value = MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[{"id": "n"}], error=None))
        )
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "do something", {"action": "unknown_action"})
        assert result["action"] == "create_task"

    @pytest.mark.asyncio
    async def test_execute_action_exception(self, mocker):
        client = self._mock_supabase(mocker)
        client._builders["tasks"].insert.side_effect = Exception("unexpected error")
        from ai.orchestrator import execute_action

        result = await execute_action("user-1", "buy", {})
        assert result["action"] == "noop"
