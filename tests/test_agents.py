"""Comprehensive tests for all 10 AI agent modules — fallback, happy, error, empty paths."""

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
import pytest

from ai.client import llm as llm_client
from ai.prompt_loader import prompts as prompt_loader
from ai.context_assembly import ContextAssembly, ContextSection, SECTIONS
from ai.sections import register_default_sections
from ai.agents import (
    briefing_agent,
    memory_agent,
    learning_agent,
    opportunity_agent,
    opportunity_matching_agent,
    task_agent,
    weekly_review_agent,
    sleep_agent,
    nudge_agent,
    roadmap_agent,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _fresh_builder(data=None, ret_insert=None):
    """Build a fresh chainable supabase query builder.

    All chain methods (select, eq, order, …) return self.
    .execute() returns a MagicMock with .data = data (or []) and .error = None.
    .insert().execute() returns ret_insert (default: [{"id": "mock-id"}]).
    .update() returns self for update().eq().execute() chaining.
    """
    b = MagicMock()
    insert_val = ret_insert if ret_insert is not None else [{"id": "mock-id"}]
    b.execute.return_value = MagicMock(data=data or [], error=None)
    for m in ("select", "eq", "order", "limit", "gte", "lt", "range", "text_search"):
        getattr(b, m).return_value = b
    b.insert.return_value = MagicMock(execute=MagicMock(return_value=MagicMock(data=insert_val, error=None)))
    b.update.return_value = b
    return b


_AGENT_MODULES = [
    "ai.agents.briefing_agent",
    "ai.agents.memory_agent",
    "ai.agents.learning_agent",
    "ai.agents.opportunity_agent",
    "ai.agents.opportunity_matching_agent",
    "ai.agents.task_agent",
    "ai.agents.weekly_review_agent",
    "ai.agents.sleep_agent",
    "ai.agents.nudge_agent",
    "ai.agents.roadmap_agent",
    "ai.agents.skill_agent",
    "ai.sections",
]


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def mock_supabase(mocker):
    """Patch get_supabase_client inside every agent module's namespace.

    Each agent does 'from config.core.supabase import get_supabase_client',
    creating a local reference — patching config.core.supabase is not enough;
    we must patch each module individually.

    The returned client exposes a ``_builders`` dict that tests can modify
    to control per-table query results:

        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "1", "title": "…"}]
        )
    """
    client = MagicMock()

    # Real dict with auto-creation — accessing _builders["tasks"]
    # automatically creates a fresh builder for that table.
    class _AutoBuilders(dict):
        def __missing__(self, key):
            val = MagicMock()
            val.execute.return_value = MagicMock(data=[], error=None)
            for m in ("select", "eq", "order", "limit", "gte", "lt", "range", "text_search", "or_"):
                getattr(val, m).return_value = val
            val.update.return_value = val

            def _insert_side_effect(data):
                result = {"id": "mock-id", **(data or {})}
                return MagicMock(execute=MagicMock(return_value=MagicMock(data=[result], error=None)))

            val.insert.side_effect = _insert_side_effect
            self[key] = val
            return val

    builders = _AutoBuilders()

    def from_side(table):
        return builders[table]

    client.from_.side_effect = from_side
    client._builders = builders

    for mod in _AGENT_MODULES:
        mocker.patch(f"{mod}.get_supabase_client", return_value=client)
    return client


@pytest.fixture
def mock_llm_json(mocker):
    m = AsyncMock(return_value={})
    mocker.patch.object(llm_client, "generate_json", m)
    return m


@pytest.fixture
def mock_llm_generate(mocker):
    m = AsyncMock(return_value="mock text response")
    mocker.patch.object(llm_client, "generate", m)
    return m


@pytest.fixture
def mock_get_agent(mocker):
    entry = MagicMock()
    entry.system_prompt = "You are a helpful AI assistant."
    entry.body = entry.system_prompt
    entry.agent_prompt = entry.system_prompt
    entry.render.return_value = entry.system_prompt
    mocker.patch.object(prompt_loader, "get_agent", return_value=entry)
    return entry


@pytest.fixture
def mock_get_agent_none(mocker):
    mocker.patch.object(prompt_loader, "get_agent", return_value=None)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. briefing_agent — generate_daily_briefing
# ═══════════════════════════════════════════════════════════════════════════════


class TestBriefingAgent:
    """Daily briefing generator — 4 paths."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Finish report",
                    "status": "pending",
                    "priority": "high",
                    "due_date": "2026-06-20",
                    "estimated_minutes": 45,
                },
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Get A grade", "status": "active", "progress": 60},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(data=[])
        mock_llm_json.return_value = {
            "aria_pick": {"title": "Finish report", "reason": "Deadline approaching"},
            "productivity_tip": "Use Pomodoro technique",
            "focus_area": "Clear high-priority tasks",
        }

        result = await briefing_agent.generate_daily_briefing("user-1")

        assert result["top_3_tasks"][0]["title"] == "Finish report"
        assert result["aria_pick"]["title"] == "Finish report"
        assert result["productivity_tip"] == "Use Pomodoro technique"
        assert result["focus_area"] == "Clear high-priority tasks"
        assert "generated_at" in result
        assert result["sleep_score"] == 70
        assert result["active_goals"][0]["title"] == "Get A grade"

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Urgent task",
                    "status": "pending",
                    "priority": "urgent",
                    "due_date": "2026-06-17",
                    "estimated_minutes": 30,
                },
                {
                    "id": "t2",
                    "title": "Low priority",
                    "status": "pending",
                    "priority": "low",
                    "due_date": "2026-06-25",
                    "estimated_minutes": 10,
                },
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Goal 1", "status": "active", "progress": 40},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "CS 101", "status": "in_progress"},
            ]
        )
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": datetime.now().date().isoformat(), "quality": 85, "duration_hours": 7.5},
            ]
        )
        mock_llm_json.return_value = {
            "aria_pick": {"title": "Urgent task", "reason": "Top priority"},
            "productivity_tip": "Start early",
            "focus_area": "Urgent items first",
        }

        result = await briefing_agent.generate_daily_briefing("user-1")

        assert result["sleep_score"] == 85
        assert result["top_3_tasks"][0]["title"] == "Urgent task"
        assert isinstance(result["productivity_score"], int)
        assert result["aria_pick"]["title"] == "Urgent task"
        assert len(result["active_goals"]) == 1

    @pytest.mark.asyncio
    async def test_error_when_llm_raises(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.side_effect = RuntimeError("LLM unavailable")
        with pytest.raises(RuntimeError):
            await briefing_agent.generate_daily_briefing("user-1")

    @pytest.mark.asyncio
    async def test_empty_data_returns_defaults(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {}
        result = await briefing_agent.generate_daily_briefing("user-1")
        assert result["top_3_tasks"] == []
        assert result["sleep_score"] == 70
        assert result["active_goals"] == []
        assert result["aria_pick"]["title"] == "Start your day"
        assert result["productivity_tip"] == "Break big tasks into smaller chunks"
        assert result["focus_area"] == "Clear your pending tasks first"

    @pytest.mark.asyncio
    async def test_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await briefing_agent.generate_daily_briefing("user-1")
        assert result["productivity_tip"] == "Break big tasks into smaller chunks"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. memory_agent — store, query, preferences, summary
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryAgent:
    """Memory consolidation agent — 4 public functions tested."""

    @pytest.mark.asyncio
    async def test_store_interaction(self, mock_supabase):
        result = await memory_agent.store_interaction("user-1", "query", "What is my schedule?", {"source": "chat"})
        assert result["id"] == "mock-id"
        inserted = mock_supabase._builders["memory"].insert.call_args[0][0]
        assert inserted["user_id"] == "user-1"
        assert inserted["type"] == "query"

    @pytest.mark.asyncio
    async def test_store_interaction_empty_result(self, mock_supabase):
        mock_supabase._builders["memory"].insert.side_effect = lambda d: MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[], error=None))
        )
        result = await memory_agent.store_interaction("user-1", "note", "Just a note")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_recent_interactions(self, mock_supabase):
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {"id": "m1", "content": "Hello", "timestamp": "2026-06-17T10:00:00"},
            ]
        )
        result = await memory_agent.get_recent_interactions("user-1", limit=5)
        assert len(result) == 1
        assert result[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_get_recent_interactions_empty(self, mock_supabase):
        result = await memory_agent.get_recent_interactions("user-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_preferences_from_tasks(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"category": "study", "priority": "high"},
                {"category": "study", "priority": "high"},
                {"category": "personal", "priority": "medium"},
            ]
        )
        result = await memory_agent.get_user_preferences("user-1")
        assert result["preferred_category"] == "study"
        assert result["preferred_priority"] == "high"
        assert result["total_tasks"] == 3

    @pytest.mark.asyncio
    async def test_get_user_preferences_empty(self, mock_supabase):
        result = await memory_agent.get_user_preferences("user-1")
        assert result["preferred_category"] == "personal"
        assert result["preferred_priority"] == "medium"
        assert result["total_tasks"] == 0

    @pytest.mark.asyncio
    async def test_get_memory_summary_fallback(self, mock_supabase, mock_get_agent_none, mock_llm_generate):
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {"id": "m1", "type": "query", "value": "Working on project", "created_at": "2026-06-17T10:00:00"},
            ]
        )
        result = await memory_agent.get_memory_summary("user-1")
        assert result["recent_interactions"] == 1
        assert result["preferences"]["preferred_category"] == "personal"
        assert result["memory_type"] == "short_term"

    @pytest.mark.asyncio
    async def test_get_memory_summary_happy_path(self, mock_supabase, mock_get_agent, mock_llm_generate):
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {"id": "m1", "type": "query", "value": "Learning Python", "created_at": "2026-06-17T10:00:00"},
            ]
        )
        mock_llm_generate.return_value = "User is focused on Python learning."
        result = await memory_agent.get_memory_summary("user-1")
        assert result["summary"] == "User is focused on Python learning."
        assert result["recent_interactions"] == 1

    @pytest.mark.asyncio
    async def test_get_memory_summary_no_interactions(self, mock_supabase, mock_get_agent):
        result = await memory_agent.get_memory_summary("user-1")
        assert result["summary"] == "No recent interactions to summarize."
        assert result["recent_interactions"] == 0
        assert result["memory_type"] == "short_term"

    @pytest.mark.asyncio
    async def test_get_memory_summary_long_term(self, mock_supabase, mock_get_agent, mock_llm_generate):
        interactions = [
            {"id": str(i), "type": "query", "value": f"Interaction {i}", "created_at": "2026-06-17T10:00:00"}
            for i in range(55)
        ]
        mock_supabase._builders["memory"].execute.return_value = MagicMock(data=interactions)
        result = await memory_agent.get_memory_summary("user-1")
        assert result["memory_type"] == "long_term"

    @pytest.mark.asyncio
    async def test_get_memory_summary_llm_error(self, mock_supabase, mock_get_agent, mock_llm_generate):
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {"id": "m1", "type": "query", "value": "Hi", "created_at": "2026-06-17T10:00:00"},
            ]
        )
        mock_llm_generate.side_effect = RuntimeError("LLM error")
        result = await memory_agent.get_memory_summary("user-1")
        assert result["summary"] == "Unable to generate memory summary at this time."

    # --- store_interaction error path ---

    @pytest.mark.asyncio
    async def test_store_interaction_db_error(self, mock_supabase):
        mock_supabase._builders["memory"].insert.side_effect = Exception("DB down")
        result = await memory_agent.store_interaction("user-1", "query", "test")
        assert result is None

    # --- get_recent_interactions error path ---

    @pytest.mark.asyncio
    async def test_get_recent_interactions_error(self, mock_supabase):
        mock_supabase._builders["memory"].execute.side_effect = Exception("query failed")
        result = await memory_agent.get_recent_interactions("user-1")
        assert result == []

    # --- get_user_preferences — habits, courses, goals, error ---

    @pytest.mark.asyncio
    async def test_get_user_preferences_with_habits_and_courses(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[{"frequency": "daily", "streak": 10}, {"frequency": "weekly", "streak": 5}]
        )
        mock_supabase._builders["goals"].neq.return_value = mock_supabase._builders["goals"]
        mock_supabase._builders["goals"].execute.return_value = MagicMock(data=[{"id": "g1", "status": "active"}])
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[{"status": "in_progress", "progress": 75}, {"status": "in_progress", "progress": 50}]
        )
        result = await memory_agent.get_user_preferences("user-1")
        assert result["total_habits"] == 2
        assert result["habit_streak_avg"] == 7
        assert result["active_goal_count"] == 1
        assert result["total_courses"] == 2
        assert result["course_progress_avg"] == 62.5

    @pytest.mark.asyncio
    async def test_get_user_preferences_db_error(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.side_effect = Exception("DB error")
        result = await memory_agent.get_user_preferences("user-1")
        assert result["preferred_category"] == "personal"

    @pytest.mark.asyncio
    async def test_get_user_preferences_high_workload(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"category": "study", "priority": "high"}] * 3 + [{"category": "personal", "priority": "low"}] * 1
        )
        mock_supabase._builders["habits"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["goals"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["courses"].execute.return_value = MagicMock(data=[])
        result = await memory_agent.get_user_preferences("user-1")
        assert result["work_hours_pattern"] == "high_workload"

    # --- get_session_context — conversation grouping, error ---

    @pytest.mark.asyncio
    async def test_get_session_context_with_conversations(self, mock_supabase):
        mock_supabase._builders["chat_messages"].execute.return_value = MagicMock(
            data=[
                {"conversation_id": "conv1", "role": "user", "content": "What is my schedule?", "created_at": "a"},
                {"conversation_id": "conv1", "role": "assistant", "content": "You have 3 tasks", "created_at": "b"},
                {"conversation_id": "conv2", "role": "user", "content": "Remind me", "created_at": "c"},
                {"conversation_id": "conv3", "role": "user", "content": "", "created_at": "d"},
                {"conversation_id": "conv3", "role": "assistant", "content": "OK", "created_at": "e"},
            ]
        )
        result = await memory_agent.get_session_context("user-1")
        assert result["active_conversations"] == 2  # conv1 (>1) + conv3 (>1)
        assert result["total_recent_messages"] == 5
        assert result["last_interaction"] == "a"

    @pytest.mark.asyncio
    async def test_get_session_context_empty(self, mock_supabase):
        mock_supabase._builders["chat_messages"].execute.return_value = MagicMock(data=[])
        result = await memory_agent.get_session_context("user-1")
        assert result["total_recent_messages"] == 0
        assert result["last_interaction"] is None

    @pytest.mark.asyncio
    async def test_get_session_context_db_error(self, mock_supabase):
        mock_supabase._builders["chat_messages"].execute.side_effect = Exception("DB error")
        result = await memory_agent.get_session_context("user-1")
        assert result["active_conversations"] == 0

    # --- consolidate_memories — LLM path, fallback, error ---

    def _setup_prefs_empty(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["habits"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["goals"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["courses"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["chat_messages"].execute.return_value = MagicMock(data=[])

    @pytest.mark.asyncio
    async def test_consolidate_memories_full_llm(self, mock_supabase, mock_get_agent, mock_llm_json):
        self._setup_prefs_empty(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "test",
                    "importance": "medium",
                    "tags": ["t"],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_llm_json.return_value = {
            "memories_to_create": [
                {
                    "memory_type": "insight",
                    "content": "Key insight",
                    "domain": "work",
                    "confidence": 0.9,
                    "source": "chat",
                    "ttl_days": 30,
                }
            ],
            "memories_to_update": [],
            "memories_to_discard": [],
            "analysis": {"summary": "Done", "key_observation": "Productive", "actionable": True},
            "pattern_detected": "consistent_work",
            "contradictions": [],
            "confidence_level": "high",
            "processing_notes": "OK",
        }
        result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "llm_driven"
        assert result["memories_created"] == 1
        assert result["patterns_detected"] == 1

    def _setup_prefs_empty_with_neq(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["habits"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["goals"].neq.return_value = mock_supabase._builders["goals"]
        mock_supabase._builders["goals"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["courses"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["chat_messages"].execute.return_value = MagicMock(data=[])

    @pytest.mark.asyncio
    async def test_consolidate_memories_update_discard(self, mock_supabase, mock_get_agent, mock_llm_json):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": {"content": "old"},
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_supabase._builders["memory"].delete.return_value = mock_supabase._builders["memory"]
        mock_llm_json.return_value = {
            "memories_to_create": [],
            "memories_to_update": [{"memory_id": "m1", "updates": {"confidence": 0.85, "content": "Updated"}}],
            "memories_to_discard": [{"memory_id": "m2"}],
            "analysis": {"summary": "Done", "key_observation": None, "actionable": False},
            "pattern_detected": None,
            "contradictions": [{"type": "time"}],
            "confidence_level": "medium",
        }
        result = await memory_agent.consolidate_memories("user-1")
        assert result["memories_updated"] == 1
        assert result["memories_discarded"] == 1

    @pytest.mark.asyncio
    async def test_consolidate_memories_update_low_confidence(self, mock_supabase, mock_get_agent, mock_llm_json):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": {"content": "old"},
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_supabase._builders["memory"].delete.return_value = mock_supabase._builders["memory"]
        mock_llm_json.return_value = {
            "memories_to_create": [],
            "memories_to_update": [
                {"memory_id": "m1", "updates": {"confidence": 0.25, "content": "low confidence update"}}
            ],
            "memories_to_discard": [],
            "analysis": {"summary": "Done", "key_observation": None, "actionable": False},
            "pattern_detected": None,
            "contradictions": [],
            "confidence_level": "low",
        }
        result = await memory_agent.consolidate_memories("user-1")
        assert result["memories_updated"] == 1

    @pytest.mark.asyncio
    async def test_consolidate_memories_update_error(self, mock_supabase, mock_get_agent, mock_llm_json):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": {"content": "old"},
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_llm_json.return_value = {
            "memories_to_create": [],
            "memories_to_update": [{"memory_id": "m1", "updates": {"confidence": 0.9, "content": "update"}}],
            "memories_to_discard": [],
            "analysis": {"summary": "Done", "key_observation": None, "actionable": False},
            "pattern_detected": None,
            "contradictions": [],
            "confidence_level": "high",
        }
        # Make the update execute raise
        mock_supabase._builders["memory"].update.side_effect = lambda d: MagicMock(
            eq=lambda k, v: MagicMock(
                eq=lambda k2, v2: MagicMock(execute=MagicMock(side_effect=Exception("update failed")))
            )
        )
        result = await memory_agent.consolidate_memories("user-1")
        assert result["memories_updated"] == 0

    @pytest.mark.asyncio
    async def test_consolidate_memories_discard_error(self, mock_supabase, mock_get_agent, mock_llm_json):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "test",
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        del_mock = MagicMock()
        del_mock.eq.side_effect = lambda k, v: MagicMock(
            eq=lambda k2, v2: MagicMock(execute=MagicMock(side_effect=Exception("discard failed")))
        )
        mock_supabase._builders["memory"].delete.return_value = del_mock
        mock_llm_json.return_value = {
            "memories_to_create": [],
            "memories_to_update": [],
            "memories_to_discard": [{"memory_id": "m2"}],
            "analysis": {"summary": "Done", "key_observation": None, "actionable": False},
            "pattern_detected": None,
            "contradictions": [],
            "confidence_level": "high",
        }
        result = await memory_agent.consolidate_memories("user-1")
        assert result["memories_discarded"] == 0

    @pytest.mark.asyncio
    async def test_consolidate_memories_llm_unavailable(self, mock_supabase, mock_get_agent):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "test",
                    "importance": "medium",
                    "tags": ["t"],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_supabase._builders["memory"].delete.return_value = mock_supabase._builders["memory"]
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.memory_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("API down")):
            result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "rule_based"

    @pytest.mark.asyncio
    async def test_consolidate_memories_fallback_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "test",
                    "importance": "medium",
                    "tags": ["t"],
                    "created_at": "2026-01-01T00:00:00",
                }
            ]
        )
        mock_llm_json.return_value = {
            "memories_to_create": [],
            "memories_to_update": [],
            "memories_to_discard": [],
            "analysis": {"summary": "inline fallback", "actionable": False},
            "pattern_detected": None,
            "contradictions": [],
            "confidence_level": "low",
        }
        result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "llm_driven"

    @pytest.mark.asyncio
    async def test_consolidate_memories_outer_error(self, mock_supabase, mock_get_agent):
        with patch("ai.agents.memory_agent.get_recent_interactions", side_effect=Exception("outer fail")):
            result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "error"

    # --- _rule_based_consolidation tested via LLM-unavailable fallback ---

    @pytest.mark.asyncio
    async def test_consolidate_memories_stale_expired(self, mock_supabase, mock_get_agent):
        self._setup_prefs_empty_with_neq(mock_supabase)
        from datetime import datetime, timezone, timedelta

        past = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        future = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "v",
                    "importance": "medium",
                    "tags": ["t"],
                    "created_at": "2026-01-01T00:00:00",
                    "expires_at": past,
                },
                {
                    "id": "m2",
                    "type": "note",
                    "key": "k2",
                    "value": "v2",
                    "importance": "low",
                    "tags": [],
                    "created_at": "2026-01-02T00:00:00",
                    "expires_at": future,
                },
                {
                    "id": "m3",
                    "type": "query",
                    "key": "k3",
                    "value": "v3",
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-03T00:00:00",
                    "expires_at": past,
                },
                {
                    "id": "m4",
                    "type": "query",
                    "key": "k4",
                    "value": "v4",
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-04T00:00:00",
                    "expires_at": past,
                },
            ]
        )
        mock_supabase._builders["memory"].delete.return_value = mock_supabase._builders["memory"]
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.memory_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "rule_based"
        assert result["memories_discarded"] == 3
        # 3 stale deleted (m1, m3, m4), patterns_detected >= 1 (query has 3+ items)

    @pytest.mark.asyncio
    async def test_consolidate_memories_rule_based_error(self, mock_supabase, mock_get_agent):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "v",
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                    "expires_at": "2020-01-01T00:00:00+00:00",
                }
            ]
        )
        del_mock = MagicMock()
        del_mock.eq.side_effect = lambda k, v: MagicMock(
            eq=lambda k2, v2: MagicMock(execute=MagicMock(side_effect=Exception("rule-based delete failed")))
        )
        mock_supabase._builders["memory"].delete.return_value = del_mock
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.memory_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "rule_based"
        assert result["memories_discarded"] == 0

    @pytest.mark.asyncio
    async def test_consolidate_memories_stale_parse_error(self, mock_supabase, mock_get_agent):
        self._setup_prefs_empty_with_neq(mock_supabase)
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "m1",
                    "type": "query",
                    "key": "k",
                    "value": "v",
                    "importance": "medium",
                    "tags": [],
                    "created_at": "2026-01-01T00:00:00",
                    "expires_at": "not-a-date",
                },
            ]
        )
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.memory_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await memory_agent.consolidate_memories("user-1")
        assert result["consolidation_type"] == "rule_based"
        assert result["memories_discarded"] == 0

    # --- prune_expired_memories ---

    @pytest.mark.asyncio
    async def test_prune_expired_memories_success(self, mock_supabase):
        mock_supabase._builders["memory"].delete.return_value = mock_supabase._builders["memory"]
        mock_supabase._builders["memory"].execute.return_value = MagicMock(data=[{"id": "m1"}])
        result = await memory_agent.prune_expired_memories("user-1")
        assert result == 1

    @pytest.mark.asyncio
    async def test_prune_expired_memories_error(self, mock_supabase):
        mock_supabase._builders["memory"].delete.side_effect = Exception("delete failed")
        result = await memory_agent.prune_expired_memories("user-1")
        assert result == 0

    # --- get_memory_summary — LLMProviderUnavailableError ---

    @pytest.mark.asyncio
    async def test_get_memory_summary_llm_unavailable(self, mock_supabase, mock_get_agent):
        mock_supabase._builders["memory"].execute.return_value = MagicMock(
            data=[
                {"id": "m1", "type": "query", "value": "Hi", "importance": "high", "created_at": "2026-06-17T10:00:00"}
            ]
        )
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["habits"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["goals"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["courses"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["chat_messages"].execute.return_value = MagicMock(data=[])
        from ai.client import LLMProviderUnavailableError

        with patch("ai.agents.memory_agent.llm.generate", side_effect=LLMProviderUnavailableError("down")):
            result = await memory_agent.get_memory_summary("user-1")
        assert "recent interactions" in result["summary"]

    @pytest.mark.asyncio
    async def test_get_memory_summary_outer_error(self, mock_supabase, mock_get_agent):
        with patch("ai.agents.memory_agent.get_user_preferences", side_effect=Exception("boom")):
            result = await memory_agent.get_memory_summary("user-1")
        assert result["summary"] == "Unable to generate memory summary at this time."


# ═══════════════════════════════════════════════════════════════════════════════
# 3. learning_agent — track_progress, detect_patterns, suggest_focus
# ═══════════════════════════════════════════════════════════════════════════════


class TestLearningAgent:
    """Learning pattern detection — 3 public functions."""

    @pytest.mark.asyncio
    async def test_track_progress(self, mock_supabase):
        recent = (datetime.now() - timedelta(days=1)).isoformat()
        old = (datetime.now() - timedelta(days=30)).isoformat()
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "status": "completed", "created_at": recent, "completed_at": recent},
                {"id": "t2", "status": "pending", "created_at": recent},
                {"id": "t3", "status": "completed", "created_at": old, "completed_at": old},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "status": "in_progress"},
                {"id": "c2", "status": "completed"},
            ]
        )
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {"id": "h1", "is_active": True},
                {"id": "h2", "is_active": False},
            ]
        )
        result = await learning_agent.track_user_progress("user-1")
        assert result["tasks_created"] == 2
        assert result["tasks_completed"] == 1
        assert result["completion_rate"] == 50.0
        assert result["courses_enrolled"] == 1
        assert result["courses_completed"] == 1
        assert result["active_habits"] == 1

    @pytest.mark.asyncio
    async def test_track_progress_empty(self, mock_supabase):
        result = await learning_agent.track_user_progress("user-1")
        assert result["tasks_created"] == 0
        assert result["tasks_completed"] == 0
        assert result["completion_rate"] == 0
        assert result["active_habits"] == 0

    @pytest.mark.asyncio
    async def test_detect_patterns_fallback(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_llm_json.return_value = ["Student is consistent"]
        result = await learning_agent.detect_learning_patterns("user-1")
        assert result == ["Student is consistent"]

    @pytest.mark.asyncio
    async def test_detect_patterns_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {"patterns": ["Good progress", "Needs consistency"]}
        result = await learning_agent.detect_learning_patterns("user-1")
        assert result == ["Good progress", "Needs consistency"]

    @pytest.mark.asyncio
    async def test_detect_patterns_returns_list_directly(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = ["Direct list pattern"]
        result = await learning_agent.detect_learning_patterns("user-1")
        assert result == ["Direct list pattern"]

    @pytest.mark.asyncio
    async def test_detect_patterns_returns_default(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {"unexpected": "data"}
        result = await learning_agent.detect_learning_patterns("user-1")
        assert result == ["Keep up the consistent work"]

    @pytest.mark.asyncio
    async def test_suggest_learning_focus(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {"recommendations": ["Study daily", "Take breaks"]}
        result = await learning_agent.suggest_learning_focus("user-1")
        assert "patterns" in result
        assert result["recommendations"] == ["Study daily", "Take breaks"]

    @pytest.mark.asyncio
    async def test_suggest_learning_focus_defaults(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {}
        result = await learning_agent.suggest_learning_focus("user-1")
        assert result["recommendations"] == ["Stay consistent with your study routine"]

    @pytest.mark.asyncio
    async def test_detect_patterns_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.side_effect = RuntimeError("LLM error")
        with pytest.raises(RuntimeError):
            await learning_agent.detect_learning_patterns("user-1")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. opportunity_agent — run_opportunity_radar
# ═══════════════════════════════════════════════════════════════════════════════


class TestOpportunityAgent:
    """Opportunity radar — fetches user skills, calls LLM, inserts results."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python", "React"], "interests": ["AI", "Web"]},
            ]
        )
        mock_llm_json.return_value = {}
        result = await opportunity_agent.run_opportunity_radar("user-1")
        assert len(result) == 3
        assert result[0]["title"] == "Google Summer of Code 2026"

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": ["ML"]},
            ]
        )
        mock_llm_json.return_value = [
            {
                "title": "AI Intern",
                "category": "internships",
                "url": "https://example.com",
                "deadline": "2026-08-01",
                "description": "ML internship",
                "skills_needed": ["Python"],
                "match_score": 90,
            },
        ]
        result = await opportunity_agent.run_opportunity_radar("user-1")
        assert len(result) == 1
        assert result[0]["title"] == "AI Intern"

    @pytest.mark.asyncio
    async def test_llm_returns_dict_with_opportunities_key(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": []},
            ]
        )
        mock_llm_json.return_value = {
            "opportunities": [
                {
                    "title": "GSoC",
                    "category": "open_source",
                    "url": "https://gsoc",
                    "deadline": "2026-07-01",
                    "description": "Open source",
                    "skills_needed": ["Python"],
                    "match_score": 85,
                },
            ],
        }
        result = await opportunity_agent.run_opportunity_radar("user-1")
        assert len(result) == 1
        assert result[0]["title"] == "GSoC"

    @pytest.mark.asyncio
    async def test_no_user_data_uses_default_scan(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[])
        mock_llm_json.return_value = {}
        result = await opportunity_agent.run_opportunity_radar("user-1")
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": []},
            ]
        )
        mock_llm_json.side_effect = RuntimeError("API down")
        with pytest.raises(RuntimeError):
            await opportunity_agent.run_opportunity_radar("user-1")

    @pytest.mark.asyncio
    async def test_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await opportunity_agent.run_opportunity_radar("user-1")
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# 5. opportunity_matching_agent — match_opportunities
# ═══════════════════════════════════════════════════════════════════════════════


class TestOpportunityMatchingAgent:
    """Opportunity scoring engine — ranks opportunities by match quality."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": ["Web"], "experience_level": "beginner"},
            ]
        )
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(
            data=[
                {"id": "o1", "title": "Intern", "match_score": 50},
            ]
        )
        mock_llm_json.return_value = {
            "recommendations": [
                {"opportunity_id": "o1", "match_score": 85, "reasoning": "Good fit", "action_tip": "Apply now"}
            ],
        }
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert len(result) == 1
        assert result[0]["opportunity_id"] == "o1"
        assert result[0]["match_score"] == 85

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": ["ML"], "experience_level": "intermediate"},
            ]
        )
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(
            data=[
                {"id": "o1", "title": "ML Intern", "match_score": 40},
            ]
        )
        mock_llm_json.return_value = {
            "recommendations": [
                {"opportunity_id": "o1", "match_score": 92, "reasoning": "ML match", "action_tip": "Update resume"},
            ],
        }
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert result[0]["match_score"] == 92

    @pytest.mark.asyncio
    async def test_empty_opportunities(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": [], "experience_level": "beginner"},
            ]
        )
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(data=[])
        mock_llm_json.return_value = {"recommendations": []}
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_no_user_data(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(data=[])
        mock_llm_json.return_value = {"recommendations": []}
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": [], "interests": [], "experience_level": "beginner"},
            ]
        )
        mock_llm_json.side_effect = RuntimeError("LLM failed")
        with pytest.raises(RuntimeError):
            await opportunity_matching_agent.match_opportunities("user-1")

    @pytest.mark.asyncio
    async def test_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════════
# 6. task_agent — breakdown, check_missed, prioritization, reschedule
# ═══════════════════════════════════════════════════════════════════════════════


class TestTaskAgent:
    """Task breakdown, missed-task detection, prioritization, reschedule."""

    # -- breakdown_task --------------------------------------------------------

    @pytest.mark.asyncio
    async def test_breakdown_fallback(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Write essay",
                    "description": "History paper",
                    "category": "study",
                    "priority": "high",
                },
            ]
        )
        mock_llm_json.return_value = [
            {"title": "Research topic", "category": "study"},
            {"title": "Write outline", "category": "study"},
        ]
        result = await task_agent.breakdown_task("user-1", "t1")
        assert len(result) == 2
        assert result[0]["title"] == "Research topic"
        assert result[0]["parent_task_id"] == "t1"
        assert result[0]["user_id"] == "user-1"

    @pytest.mark.asyncio
    async def test_breakdown_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "t1",
                    "title": "Build app",
                    "description": "React app",
                    "category": "coding",
                    "priority": "urgent",
                },
            ]
        )
        mock_llm_json.return_value = {
            "subtasks": [
                {"title": "Setup project", "category": "coding"},
                {"title": "Build UI", "category": "coding"},
            ],
        }
        result = await task_agent.breakdown_task("user-1", "t1")
        assert len(result) == 2
        assert result[0]["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_breakdown_ai_returns_empty(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "title": "Clean room", "description": "", "category": "personal", "priority": "low"},
            ]
        )
        mock_llm_json.return_value = {}
        result = await task_agent.breakdown_task("user-1", "t1")
        assert len(result) == 1
        assert "Start" in result[0]["title"]

    @pytest.mark.asyncio
    async def test_breakdown_task_not_found(self, mock_supabase, mock_get_agent):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(data=[])
        result = await task_agent.breakdown_task("user-1", "nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_breakdown_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "title": "Test", "description": "", "category": "personal"},
            ]
        )
        mock_llm_json.side_effect = RuntimeError("LLM broken")
        with pytest.raises(RuntimeError):
            await task_agent.breakdown_task("user-1", "t1")

    @pytest.mark.asyncio
    async def test_breakdown_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "title": "Test", "description": "", "category": "personal"},
            ]
        )
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await task_agent.breakdown_task("user-1", "t1")
        assert len(result) == 1

    # -- check_missed_tasks ---------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_missed_tasks(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "status": "pending", "due_date": "2020-01-01", "missed_count": 0},
                {"id": "t2", "status": "pending", "due_date": "2020-01-02", "missed_count": 2},
            ]
        )
        result = await task_agent.check_missed_tasks("user-1")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_check_missed_tasks_none(self, mock_supabase):
        result = await task_agent.check_missed_tasks("user-1")
        assert result == []

    # -- suggest_task_prioritization ------------------------------------------

    @pytest.mark.asyncio
    async def test_suggest_prioritization(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "priority": "high", "due_date": "2026-06-18", "status": "pending"},
                {"id": "t2", "priority": "urgent", "due_date": "2026-06-17", "status": "pending"},
                {"id": "t3", "priority": "low", "due_date": "2026-06-25", "status": "pending"},
            ]
        )
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"date": "2026-06-16", "quality": 80},
            ]
        )
        result = await task_agent.suggest_task_prioritization("user-1")
        assert len(result) == 3
        assert result[0]["id"] == "t2"

    @pytest.mark.asyncio
    async def test_suggest_prioritization_filters_urgent_when_sleep_poor(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "priority": "urgent", "due_date": "2026-06-17", "status": "pending"},
                {"id": "t2", "priority": "high", "due_date": "2026-06-18", "status": "pending"},
            ]
        )
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"date": "2026-06-16", "quality": 50},
            ]
        )
        result = await task_agent.suggest_task_prioritization("user-1")
        assert len(result) == 1
        assert result[0]["id"] == "t2"

    @pytest.mark.asyncio
    async def test_suggest_prioritization_no_sleep_data(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "priority": "urgent", "due_date": "2026-06-17", "status": "pending"},
            ]
        )
        result = await task_agent.suggest_task_prioritization("user-1")
        assert len(result) == 1

    # -- auto_reschedule_overdue ----------------------------------------------

    @pytest.mark.asyncio
    async def test_auto_reschedule(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "status": "pending", "due_date": "2020-01-01", "missed_count": 0},
            ]
        )
        count = await task_agent.auto_reschedule_overdue("user-1")
        assert count == 1

    @pytest.mark.asyncio
    async def test_auto_reschedule_none_missed(self, mock_supabase):
        count = await task_agent.auto_reschedule_overdue("user-1")
        assert count == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 7. weekly_review_agent — generate_weekly_review
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeeklyReviewAgent:
    """Weekly review generator — 4 paths."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        recent = (datetime.now() - timedelta(days=1)).isoformat()
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "status": "completed", "created_at": recent},
                {"id": "t2", "status": "pending", "created_at": recent},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "status": "in_progress"},
            ]
        )
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {"id": "h1", "is_active": True},
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Learn Python", "status": "active"},
            ]
        )
        mock_llm_json.return_value = {
            "week_summary": "Good week",
            "achievements": ["Completed tasks"],
            "challenges": ["Need focus"],
            "next_week_intention": "Stay consistent",
            "morale": "positive",
        }
        result = await weekly_review_agent.generate_weekly_review("user-1")
        assert result["tasks_completed"] == 1
        assert result["tasks_total"] == 2
        assert result["completion_rate"] == 50.0
        assert result["summary"] == "Good week"
        assert result["achievements"] == ["Completed tasks"]
        assert result["morale"] == "positive"

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        recent = (datetime.now() - timedelta(days=1)).isoformat()
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"id": "t1", "status": "completed", "created_at": recent},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "status": "completed"},
            ]
        )
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {"id": "h1", "is_active": True},
                {"id": "h2", "is_active": True},
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Goal A", "status": "active"},
            ]
        )
        mock_llm_json.return_value = {
            "week_summary": "Productive week!",
            "achievements": ["1 task done", "Habit streak"],
            "challenges": [],
            "next_week_intention": "Do more",
            "morale": "positive",
        }
        result = await weekly_review_agent.generate_weekly_review("user-1")
        assert result["completion_rate"] == 100.0
        assert result["active_habits"] == 2

    @pytest.mark.asyncio
    async def test_zero_tasks(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {}
        result = await weekly_review_agent.generate_weekly_review("user-1")
        assert result["completion_rate"] == 0
        assert result["summary"] == "Completed 0/0 tasks"
        assert result["achievements"] == []
        assert result["next_week_intention"] == "Keep consistent"

    @pytest.mark.asyncio
    async def test_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.side_effect = RuntimeError("LLM error")
        with pytest.raises(RuntimeError):
            await weekly_review_agent.generate_weekly_review("user-1")

    @pytest.mark.asyncio
    async def test_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await weekly_review_agent.generate_weekly_review("user-1")
        assert result["summary"].startswith("Completed")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. sleep_agent — analyze_sleep, suggest_bedtime
# ═══════════════════════════════════════════════════════════════════════════════


class TestSleepAgent:
    """Sleep analysis and wind-down suggestions."""

    @pytest.mark.asyncio
    async def test_analyze_fallback(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        today = datetime.now().date().isoformat()
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": today, "quality": 78, "duration_hours": 7.0, "sleep_debt_hours": 1.0},
            ]
        )
        mock_llm_json.return_value = {
            "sleep_analysis": "Good sleep, slight debt",
            "wind_down_routine": ["Dim lights"],
            "recommendations": ["Sleep earlier"],
        }
        result = await sleep_agent.analyze_sleep("user-1")
        assert result["has_data"] is True
        assert result["score"] == 78
        assert result["duration_hours"] == 7.0
        assert result["sleep_analysis"] == "Good sleep, slight debt"

    @pytest.mark.asyncio
    async def test_analyze_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        today = datetime.now().date().isoformat()
        (datetime.now() - timedelta(days=1)).date().isoformat()
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": today, "quality": 85, "duration_hours": 8.0, "sleep_debt_hours": 0.0},
            ]
        )
        # We need to set up two separate queries: one for the date lookup and one for the week
        # Since both go through the same builder, set week data as well
        result = await sleep_agent.analyze_sleep("user-1")
        assert result["has_data"] is True
        assert result["score"] == 85

    @pytest.mark.asyncio
    async def test_analyze_no_data(self, mock_supabase):
        result = await sleep_agent.analyze_sleep("user-1")
        assert result["has_data"] is False
        assert result["message"] == "No sleep data for this date."

    @pytest.mark.asyncio
    async def test_analyze_specific_date(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": "2026-06-15", "quality": 90, "duration_hours": 8.0, "sleep_debt_hours": 0.0},
            ]
        )
        mock_llm_json.return_value = {}
        result = await sleep_agent.analyze_sleep("user-1", date="2026-06-15")
        assert result["date"] == "2026-06-15"
        assert result["has_data"] is True

    @pytest.mark.asyncio
    async def test_analyze_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        today = datetime.now().date().isoformat()
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": today, "quality": 70, "duration_hours": 6.0, "sleep_debt_hours": 2.0},
            ]
        )
        mock_llm_json.side_effect = RuntimeError("LLM error")
        with pytest.raises(RuntimeError):
            await sleep_agent.analyze_sleep("user-1")

    @pytest.mark.asyncio
    async def test_analyze_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        today = datetime.now().date().isoformat()
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"id": "s1", "date": today, "quality": 70, "duration_hours": 6.0, "sleep_debt_hours": 2.0},
            ]
        )
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await sleep_agent.analyze_sleep("user-1")
        assert "sleep_analysis" in result

    # -- suggest_bedtime ------------------------------------------------------

    @pytest.mark.asyncio
    async def test_suggest_bedtime_poor_sleep(self, mock_supabase):
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"quality": 50},
                {"quality": 55},
                {"quality": 45},
            ]
        )
        result = await sleep_agent.suggest_bedtime("user-1")
        assert result["suggested_bedtime"] == "21:30"

    @pytest.mark.asyncio
    async def test_suggest_bedtime_moderate_sleep(self, mock_supabase):
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"quality": 65},
                {"quality": 70},
                {"quality": 68},
            ]
        )
        result = await sleep_agent.suggest_bedtime("user-1")
        assert result["suggested_bedtime"] == "22:00"

    @pytest.mark.asyncio
    async def test_suggest_bedtime_good_sleep(self, mock_supabase):
        mock_supabase._builders["sleep_logs"].execute.return_value = MagicMock(
            data=[
                {"quality": 85},
                {"quality": 90},
            ]
        )
        result = await sleep_agent.suggest_bedtime("user-1")
        assert result["suggested_bedtime"] == "22:30"

    @pytest.mark.asyncio
    async def test_suggest_bedtime_no_data(self, mock_supabase):
        result = await sleep_agent.suggest_bedtime("user-1")
        assert result["suggested_bedtime"] == "22:00"
        assert result["based_on_avg_quality"] == 70.0


# ═══════════════════════════════════════════════════════════════════════════════
# 9. nudge_agent — generate_nudge, check_course_nudges, check_habit_streaks, run_all
# ═══════════════════════════════════════════════════════════════════════════════


class TestNudgeAgent:
    """Course/habit nudges — 4 public functions."""

    # -- generate_nudge -------------------------------------------------------

    @pytest.mark.asyncio
    async def test_generate_nudge_fallback(self, mock_get_agent_none, mock_llm_json):
        mock_llm_json.return_value = {
            "nudge_text": "You've missed a few days!",
            "smallest_action": "Spend 10 min today",
            "escalation": False,
        }
        result = await nudge_agent.generate_nudge("user-1", "habit_miss_2day", {"name": "Exercise"})
        assert result["nudge_text"] == "You've missed a few days!"
        assert result["smallest_action"] == "Spend 10 min today"
        assert result["nudge_type"] == "habit_miss_2day"

    @pytest.mark.asyncio
    async def test_generate_nudge_happy_path(self, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {
            "nudge_text": "Keep your streak alive!",
            "smallest_action": "Do 5 pushups now",
            "escalation": True,
        }
        result = await nudge_agent.generate_nudge("user-1", "streak_at_risk", {"name": "Pushups", "current_streak": 10})
        assert result["escalation"] is True
        assert result["nudge_text"] == "Keep your streak alive!"

    @pytest.mark.asyncio
    async def test_generate_nudge_invalid_type(self, mock_get_agent):
        result = await nudge_agent.generate_nudge("user-1", "invalid_type", {})
        assert "error" in result
        assert "Unknown" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_nudge_llm_error_propagates(self, mock_get_agent, mock_llm_json):
        mock_llm_json.side_effect = RuntimeError("LLM error")
        with pytest.raises(RuntimeError):
            await nudge_agent.generate_nudge("user-1", "streak_at_risk", {})

    @pytest.mark.asyncio
    async def test_generate_nudge_llm_unavailable_fallback(self, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await nudge_agent.generate_nudge("user-1", "streak_at_risk", {})
        assert result["nudge_text"] == "Time to check in on your progress!"

    # -- check_course_nudges --------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_course_nudges_triggers(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "Python 101", "progress": 15, "status": "in_progress"},
                {"id": "c2", "title": "Advanced JS", "progress": 80, "status": "in_progress"},
                {"id": "c3", "title": "Completed Course", "progress": 100, "status": "completed"},
            ]
        )
        mock_llm_json.return_value = {
            "nudge_text": "Catch up on Python 101",
            "smallest_action": "Watch one lecture",
            "escalation": False,
        }
        results = await nudge_agent.check_course_nudges("user-1")
        assert len(results) == 1
        assert results[0]["nudge_type"] == "course_behind"

    @pytest.mark.asyncio
    async def test_check_course_nudges_none(self, mock_supabase):
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "Done", "progress": 100, "status": "completed"},
            ]
        )
        results = await nudge_agent.check_course_nudges("user-1")
        assert results == []

    # -- check_habit_streaks --------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_habit_streaks_streak_at_risk(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Meditate",
                    "is_active": True,
                    "current_streak": 10,
                    "best_streak": 15,
                    "missed_days": 0,
                },
            ]
        )
        mock_llm_json.return_value = {
            "nudge_text": "Don't break your streak!",
            "smallest_action": "Meditate 2 min",
            "escalation": False,
        }
        results = await nudge_agent.check_habit_streaks("user-1")
        assert len(results) == 1
        assert results[0]["nudge_type"] == "streak_at_risk"

    @pytest.mark.asyncio
    async def test_check_habit_streaks_missed_5day(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Read",
                    "is_active": True,
                    "current_streak": 3,
                    "best_streak": 10,
                    "missed_days": 5,
                },
            ]
        )
        mock_llm_json.return_value = {
            "nudge_text": "You've missed 5 days!",
            "smallest_action": "Read 1 page",
            "escalation": True,
        }
        results = await nudge_agent.check_habit_streaks("user-1")
        assert len(results) == 1
        assert results[0]["nudge_type"] == "habit_miss_5day"

    @pytest.mark.asyncio
    async def test_check_habit_streaks_missed_2day(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Write",
                    "is_active": True,
                    "current_streak": 1,
                    "best_streak": 7,
                    "missed_days": 2,
                },
            ]
        )
        mock_llm_json.return_value = {
            "nudge_text": "Missed 2 days!",
            "smallest_action": "Write for 5 min",
            "escalation": False,
        }
        results = await nudge_agent.check_habit_streaks("user-1")
        assert len(results) == 1
        assert results[0]["nudge_type"] == "habit_miss_2day"

    @pytest.mark.asyncio
    async def test_check_habit_streaks_inactive_skipped(self, mock_supabase):
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Old habit",
                    "is_active": False,
                    "current_streak": 0,
                    "best_streak": 0,
                    "missed_days": 10,
                },
            ]
        )
        results = await nudge_agent.check_habit_streaks("user-1")
        assert results == []

    @pytest.mark.asyncio
    async def test_check_habit_streaks_no_nudges_needed(self, mock_supabase):
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "New habit",
                    "is_active": True,
                    "current_streak": 1,
                    "best_streak": 1,
                    "missed_days": 0,
                },
            ]
        )
        results = await nudge_agent.check_habit_streaks("user-1")
        assert results == []

    # -- run_all_nudges -------------------------------------------------------

    @pytest.mark.asyncio
    async def test_run_all_nudges(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "Behind Course", "progress": 10, "status": "in_progress"},
            ]
        )
        mock_supabase._builders["habits"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "h1",
                    "name": "Exercise",
                    "is_active": True,
                    "current_streak": 8,
                    "best_streak": 10,
                    "missed_days": 0,
                },
            ]
        )
        mock_llm_json.return_value = {
            "nudge_text": "Nudge text",
            "smallest_action": "Action step",
            "escalation": False,
        }
        result = await nudge_agent.run_all_nudges("user-1")
        assert result["total_nudges"] == 2
        assert len(result["course_nudges"]) == 1
        assert len(result["habit_nudges"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# 10. roadmap_agent — optimize_roadmap
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoadmapAgent:
    """Skill development roadmap optimizer — 4 paths."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_prompt(self, mock_supabase, mock_get_agent_none, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {"id": "user-1", "skills": ["Python"], "interests": ["Web"], "career_goal": "Full-stack developer"},
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "React", "status": "in_progress"},
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Build portfolio", "status": "active"},
            ]
        )
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"count": 10},
            ]
        )
        mock_llm_json.return_value = {
            "milestones": [
                {
                    "title": "Learn React",
                    "deadline_estimate": "3 months",
                    "skills_gained": ["React"],
                    "priority": "high",
                }
            ],
            "recommended_path": ["React", "Node.js"],
            "estimated_completion": "6 months",
        }
        result = await roadmap_agent.optimize_roadmap("user-1")
        assert len(result["milestones"]) == 1
        assert result["milestones"][0]["title"] == "Learn React"
        assert result["recommended_path"] == ["React", "Node.js"]
        assert result["estimated_completion"] == "6 months"
        assert result["active_courses"] == 1
        assert result["active_goals"] == 1

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_supabase._builders["users"].execute.return_value = MagicMock(
            data=[
                {
                    "id": "user-1",
                    "skills": ["JS", "CSS"],
                    "interests": ["Frontend"],
                    "career_goal": "Frontend engineer",
                },
            ]
        )
        mock_supabase._builders["courses"].execute.return_value = MagicMock(
            data=[
                {"id": "c1", "title": "React"},
                {"id": "c2", "title": "Vue"},
            ]
        )
        mock_supabase._builders["goals"].execute.return_value = MagicMock(
            data=[
                {"id": "g1", "title": "Portfolio", "status": "active"},
            ]
        )
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[
                {"count": 25},
            ]
        )
        mock_llm_json.return_value = {
            "milestones": [
                {
                    "title": "Master React",
                    "deadline_estimate": "2 months",
                    "skills_gained": ["React", "Testing"],
                    "priority": "high",
                },
                {
                    "title": "Build 3 projects",
                    "deadline_estimate": "4 months",
                    "skills_gained": ["Next.js", "Tailwind"],
                    "priority": "medium",
                },
            ],
            "recommended_path": ["React basics", "Advanced React", "Projects"],
            "estimated_completion": "6 months",
        }
        result = await roadmap_agent.optimize_roadmap("user-1")
        assert len(result["milestones"]) == 2
        assert result["active_courses"] == 2

    @pytest.mark.asyncio
    async def test_no_user_record(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {
            "milestones": [],
            "recommended_path": [],
            "estimated_completion": "6 months",
        }
        result = await roadmap_agent.optimize_roadmap("user-1")
        assert result["milestones"] == []
        assert result["active_courses"] == 0
        assert result["active_goals"] == 0

    @pytest.mark.asyncio
    async def test_empty_data_uses_defaults(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.return_value = {}
        result = await roadmap_agent.optimize_roadmap("user-1")
        assert result["milestones"] == []
        assert result["recommended_path"] == []
        assert result["estimated_completion"] == "6 months"

    @pytest.mark.asyncio
    async def test_llm_error_propagates(self, mock_supabase, mock_get_agent, mock_llm_json):
        mock_llm_json.side_effect = RuntimeError("LLM failure")
        with pytest.raises(RuntimeError):
            await roadmap_agent.optimize_roadmap("user-1")

    @pytest.mark.asyncio
    async def test_llm_unavailable_fallback(self, mock_supabase, mock_get_agent, mock_llm_json):
        from ai.client import LLMProviderUnavailableError

        mock_llm_json.side_effect = LLMProviderUnavailableError("API down")
        result = await roadmap_agent.optimize_roadmap("user-1")
        assert result["milestones"] == []


class TestSkillAgent:
    """Tests for skill_agent.py — 9 sub-agents with fallback paths."""

    @pytest.mark.asyncio
    async def test_assess_user_skill_success(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"recommended_level": 3, "confidence_adjustment": 0.1, "gap_analysis": [], "next_milestones": []}
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"user_skill_id": "us1", "skill_id": "s1", "level": 2, "state": "active", "confidence_score": 0.6}])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "description": "Programming", "level_min": 1, "level_max": 5}])
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[{"source_type": "github", "title": "open source PR"}])
        from ai.agents.skill_agent import assess_user_skill
        result = await assess_user_skill("us1", "user-1")
        assert result["skill_name"] == "Python"

    @pytest.mark.asyncio
    async def test_assess_user_skill_not_found(self, mock_supabase):
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[])
        from ai.agents.skill_agent import assess_user_skill
        result = await assess_user_skill("fake", "user-1")
        assert result.get("fallback") is True

    @pytest.mark.asyncio
    async def test_assess_user_skill_fallback(self, mock_supabase, mock_llm_json, mock_get_agent_none):
        mock_llm_json.return_value = {"recommended_level": 2, "confidence_adjustment": 0.0, "gap_analysis": [], "next_milestones": []}
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"user_skill_id": "us1", "skill_id": "s1", "level": 2, "state": "active", "confidence_score": 0.6}])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "description": "Programming", "level_min": 1, "level_max": 5}])
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[{"source_type": "github", "title": "PR"}])
        from ai.agents.skill_agent import assess_user_skill
        result = await assess_user_skill("us1", "user-1")
        assert "current_level" in result

    @pytest.mark.asyncio
    async def test_assess_user_skill_llm_fallback(self, mock_supabase, mock_get_agent):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"user_skill_id": "us1", "skill_id": "s1", "level": 2, "state": "active", "confidence_score": 0.6}])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "description": "Programming", "level_min": 1, "level_max": 5}])
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[])
        from ai.agents.skill_agent import assess_user_skill, algorithmic_fallback_assessment
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await assess_user_skill("us1", "user-1")
        assert result.get("gap_analysis") is not None

    def test_algorithmic_fallback_assessment_confidence_boost(self):
        from ai.agents.skill_agent import algorithmic_fallback_assessment
        result = algorithmic_fallback_assessment({"level": 2, "confidence_score": 0.5}, [{"id": 1}, {"id": 2}, {"id": 3}])
        assert result["confidence_adjustment"] > 0

    @pytest.mark.asyncio
    async def test_recommend_skills_success(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"recommendations": [{"skill_id": "s2", "name": "ML", "reason": "demand", "priority": 1}], "focus_area": "AI", "estimated_time": "6 months"}
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[{"skills": ["Python"], "interests": ["ML"], "career_goal": "ML Engineer"}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "level": 3, "state": "active"}])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"skill_id": "s2", "name": "ML", "category_id": "c1", "skill_health": 0.8}, {"skill_id": "s3", "name": "Rust", "category_id": "c1", "skill_health": 0.7}])
        from ai.agents.skill_agent import recommend_skills
        result = await recommend_skills("user-1")
        assert result["candidate_count"] == 2

    @pytest.mark.asyncio
    async def test_recommend_skills_fallback(self, mock_supabase, mock_get_agent_none):
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[{"skills": [], "interests": [], "career_goal": ""}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "name": "Python", "category_id": "c1", "skill_health": 0.8}])
        from ai.agents.skill_agent import recommend_skills
        result = await recommend_skills("user-1")
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_recommend_skills_llm_fallback(self, mock_supabase, mock_get_agent):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[{"skills": [], "interests": [], "career_goal": ""}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[])
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "name": "Python", "category_id": "c1", "skill_health": 0.8}])
        from ai.agents.skill_agent import recommend_skills
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await recommend_skills("user-1")
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_refresh_skill_intelligence_success(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"health_score": 0.8, "trends": ["growing"], "recommendations": ["learn"]}
        mock_supabase._builders["skill_market_data"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "demand_score": 0.8, "growth_score": 0.7, "salary_median": 120000, "competition_score": 0.5, "future_relevance": 0.9, "data_freshness": "current", "skill_health": 0.8}])
        from ai.agents.skill_agent import refresh_skill_intelligence
        result = await refresh_skill_intelligence("s1")
        assert result["health_score"] == 0.8

    @pytest.mark.asyncio
    async def test_refresh_skill_intelligence_fallback(self, mock_supabase, mock_get_agent_none):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["skill_market_data"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "skill_health": 0.7, "data_freshness": "current"}])
        from ai.agents.skill_agent import refresh_skill_intelligence
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await refresh_skill_intelligence("s1")
        assert result["health_score"] == 0.7

    @pytest.mark.asyncio
    async def test_generate_skill_roadmap_fallback(self, mock_supabase, mock_llm_json, mock_get_agent_none):
        mock_llm_json.return_value = {"phases": [], "total_estimated_hours": 0, "difficulty": "beginner"}
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "description": "Programming", "level_max": 5}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"level": 1, "state": "active"}])
        from ai.agents.skill_agent import generate_skill_roadmap
        result = await generate_skill_roadmap("user-1", "s1")
        assert "phases" in result

    @pytest.mark.asyncio
    async def test_generate_skill_roadmap_llm_fallback(self, mock_supabase, mock_get_agent):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "description": "Programming", "level_max": 5}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"level": 1, "state": "active"}])
        from ai.agents.skill_agent import generate_skill_roadmap
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await generate_skill_roadmap("user-1", "s1")
        assert len(result["phases"]) > 0

    @pytest.mark.asyncio
    async def test_verify_evidence_success(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"verification_decision": "verified", "confidence_score": 0.9, "trust_score": 0.8, "quality_score": 0.7, "reasoning": "Good"}
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[{"evidence_id": "e1", "title": "GitHub PR", "source_type": "github", "url": "https://github.com/user/repo/pull/1", "description": "A PR", "state": "submitted", "signed_hash": "abc123", "quality_score": 0.6, "trust_score": 0.7}])
        from ai.agents.skill_agent import verify_evidence
        result = await verify_evidence("e1", "user-1")
        assert result["verification_decision"] == "verified"

    @pytest.mark.asyncio
    async def test_verify_evidence_not_found(self, mock_supabase):
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[])
        from ai.agents.skill_agent import verify_evidence
        result = await verify_evidence("fake", "user-1")
        assert result.get("fallback") is True

    @pytest.mark.asyncio
    async def test_verify_evidence_fallback(self, mock_supabase, mock_get_agent_none):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["user_skill_evidence"].execute.return_value = MagicMock(data=[{"evidence_id": "e1", "title": "Cert", "source_type": "certification", "url": "", "description": "Cert", "state": "submitted", "signed_hash": "", "quality_score": 0.5, "trust_score": 0.5}])
        from ai.agents.skill_agent import verify_evidence
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await verify_evidence("e1", "user-1")
        assert result["verification_decision"] == "verified_auto"

    @pytest.mark.asyncio
    async def test_analyze_career_readiness_success(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"readiness_score": 75, "strengths": ["Python"], "gaps": ["ML"], "recommended_career_paths": ["ML Engineer"], "action_items": ["Learn ML"]}
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[{"skills": ["Python"], "career_goal": "ML Engineer", "interests": ["AI"]}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "level": 3, "state": "active"}])
        from ai.agents.skill_agent import analyze_career_readiness
        result = await analyze_career_readiness("user-1")
        assert result["readiness_score"] == 75

    @pytest.mark.asyncio
    async def test_analyze_career_readiness_fallback(self, mock_supabase, mock_get_agent_none):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["users"].execute.return_value = MagicMock(data=[{"skills": [], "career_goal": "", "interests": []}])
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[])
        from ai.agents.skill_agent import analyze_career_readiness
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await analyze_career_readiness("user-1")
        assert "readiness_score" in result

    @pytest.mark.asyncio
    async def test_analyze_market_trends_with_skill_id(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"market_overview": {}, "top_demand_skills": [], "growth_opportunities": [], "salary_insights": [], "recommendations": []}
        mock_supabase._builders["skill_market_data"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "demand_score": 0.8, "growth_score": 0.6, "skill_health": 0.7}])
        from ai.agents.skill_agent import analyze_market_trends
        result = await analyze_market_trends(skill_id="s1")
        assert result["skill_count"] == 1

    @pytest.mark.asyncio
    async def test_analyze_market_trends_no_skill_id(self, mock_supabase, mock_llm_json, mock_get_agent):
        mock_llm_json.return_value = {"market_overview": {}, "top_demand_skills": [], "growth_opportunities": [], "salary_insights": [], "recommendations": []}
        mock_supabase._builders["skill_market_data"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "demand_score": 0.8, "growth_score": 0.6, "skill_health": 0.7}])
        from ai.agents.skill_agent import analyze_market_trends
        result = await analyze_market_trends()
        assert result["skill_count"] == 1

    @pytest.mark.asyncio
    async def test_analyze_market_trends_fallback(self, mock_supabase, mock_get_agent_none):
        from ai.client import LLMProviderUnavailableError
        mock_supabase._builders["skill_market_data"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "demand_score": 0.9, "growth_score": 0.7, "skill_health": 0.8}])
        from ai.agents.skill_agent import analyze_market_trends
        with patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("down")):
            result = await analyze_market_trends()
        assert len(result["top_demand_skills"]) == 1

    @pytest.mark.asyncio
    async def test_explore_skill_graph(self, mock_supabase):
        mock_supabase._builders["skills"].execute.return_value = MagicMock(data=[{"name": "Python", "category_id": "c1"}])
        mock_supabase._builders["skill_relationships"].execute.return_value = MagicMock(data=[
            {"from_skill_id": "s1", "to_skill_id": "s2", "relationship_type": "prerequisite", "weight": 0.8},
            {"from_skill_id": "s1", "to_skill_id": "s3", "relationship_type": "related_to", "weight": 0.5},
        ])
        from ai.agents.skill_agent import explore_skill_graph
        result = await explore_skill_graph("s1")
        assert result["skill_name"] == "Python"
        assert result["prerequisites"] == 1
        assert result["related_skills"] == 1

    @pytest.mark.asyncio
    async def test_match_skill_opportunities(self, mock_supabase):
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "level": 3}])
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(data=[{"id": "o1", "title": "ML Intern"}])
        mock_supabase._builders["skill_opportunities"].execute.return_value = MagicMock(data=[{"opportunity_id": "o1", "skill_id": "s1", "min_level": 2}])
        from ai.agents.skill_agent import match_skill_opportunities
        result = await match_skill_opportunities("user-1")
        assert len(result["matches"]) == 1
        assert result["matches"][0]["match_pct"] == 100.0

    @pytest.mark.asyncio
    async def test_match_skill_opportunities_no_match(self, mock_supabase):
        mock_supabase._builders["user_skills"].execute.return_value = MagicMock(data=[{"skill_id": "s1", "level": 1}])
        mock_supabase._builders["opportunities"].execute.return_value = MagicMock(data=[{"id": "o1", "title": "ML Intern"}])
        mock_supabase._builders["skill_opportunities"].execute.return_value = MagicMock(data=[{"opportunity_id": "o1", "skill_id": "s2", "min_level": 2}])
        from ai.agents.skill_agent import match_skill_opportunities
        result = await match_skill_opportunities("user-1")
        assert result["matches"][0]["match_pct"] == 0.0


class TestContextAssembly:
    def test_section_creation(self):
        async def fake_source(uid):
            return []

        section = ContextSection("test", 200, 1, fake_source, lambda d: "fallback", "fallback")
        assert section.name == "test"
        assert section.max_tokens == 200
        assert section.priority == 1

    @pytest.mark.asyncio
    async def test_assembly_creates_sections(self):
        assembly = ContextAssembly(max_budget=7800)
        result = await assembly.assemble(user_id="user-1")
        assert isinstance(result, object)
        assert hasattr(result, "sections")
        assert hasattr(result, "total_tokens")

    @pytest.mark.asyncio
    async def test_assembly_with_data(self):
        async def fetcher(uid):
            return [{"title": "Task 1", "status": "pending"}]

        def formatter(data):
            return "\n".join(f"- {t['title']}" for t in data)

        SECTIONS.insert(0, ContextSection("custom", 200, 0, fetcher, formatter, "none"))
        assembly = ContextAssembly(max_budget=7800)
        result = await assembly.assemble(user_id="user-1")
        flat = assembly.flatten(result)
        assert "Task 1" in flat
        assert "custom" in result.sections
        SECTIONS.clear()

    def test_register_default_sections_clears_and_populates(self):
        SECTIONS.clear()
        register_default_sections()
        names = [s.name for s in SECTIONS]
        assert "tasks" in names
        assert "goals" in names
        assert "courses" in names
        assert "habits" in names
        assert "sleep" in names
        assert "memory" in names
        assert SECTIONS == sorted(SECTIONS, key=lambda s: s.priority)

    def test_section_comparison(self):
        async def src(u):
            return []

        high = ContextSection("a", 100, 1, src, lambda d: "", "")
        low = ContextSection("b", 100, 2, src, lambda d: "", "")
        sections = [low, high]
        sections.sort(key=lambda s: s.priority)
        assert sections[0].name == "a"
        assert sections[1].name == "b"

    def test_section_priority_order(self):
        async def src(u):
            return []

        SECTIONS.clear()
        SECTIONS.append(ContextSection("second", 100, 2, src, lambda d: "", ""))
        SECTIONS.append(ContextSection("first", 100, 1, src, lambda d: "", ""))
        SECTIONS.sort(key=lambda s: s.priority)
        assert SECTIONS[0].name == "first"
        assert SECTIONS[1].name == "second"
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_section_fetch_tasks(self, mock_supabase):
        mock_supabase._builders["tasks"].execute.return_value = MagicMock(
            data=[{"id": "1", "title": "Test Task", "status": "pending", "priority": "high"}]
        )
        SECTIONS.clear()
        register_default_sections()
        assembly = ContextAssembly(max_budget=7800)
        result = await assembly.assemble(user_id="user-1")
        flat = assembly.flatten(result)
        assert "Test Task" in flat
        SECTIONS.clear()

    @pytest.mark.asyncio
    async def test_section_fetch_empty(self, mock_supabase):
        SECTIONS.clear()
        register_default_sections()
        assembly = ContextAssembly(max_budget=7800)
        result = await assembly.assemble(user_id="user-1")
        flat = assembly.flatten(result)
        assert "No pending tasks." in flat
        SECTIONS.clear()
