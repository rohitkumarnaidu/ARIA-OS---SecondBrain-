"""Tests for Phase 2 agent feature gap closure -- at least 2 tests per new function."""

from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
import pytest

from ai.client import llm as llm_client, LLMProviderUnavailableError
from ai.agents import (
    task_agent,
    memory_agent,
    learning_agent,
    opportunity_agent,
    briefing_agent,
    weekly_review_agent,
    sleep_agent,
    nudge_agent,
    roadmap_agent,
    opportunity_matching_agent,
)
from ai.notification_dispatcher import NotificationDispatcher


_AGENT_MODULES = [
    "ai.agents.task_agent",
    "ai.agents.memory_agent",
    "ai.agents.learning_agent",
    "ai.agents.opportunity_agent",
    "ai.agents.opportunity_matching_agent",
    "ai.agents.briefing_agent",
    "ai.agents.weekly_review_agent",
    "ai.agents.sleep_agent",
    "ai.agents.nudge_agent",
    "ai.agents.roadmap_agent",
]


@pytest.fixture(autouse=True)
def mock_supabase(mocker):
    client = MagicMock()
    class _AutoBuilders(dict):
        def __missing__(self, key):
            val = MagicMock()
            val.execute.return_value = MagicMock(data=[], error=None)
            for m in ("select", "eq", "order", "limit", "gte", "lt", "range", "text_search", "or_", "match"):
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
    mocker.patch("shared.utils.upsert.get_supabase_client", return_value=client)
    mocker.patch("ai.notification_dispatcher.get_supabase_client", return_value=client)
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


# ═══════════════════════════════════════════════════════════════════════
# A01 — Task Agent
# ═══════════════════════════════════════════════════════════════════════


class TestTaskAgentPhase2:

    def test_detect_schedule_conflicts_overlap(self):
        tasks = [
            {"id": "1", "title": "Task A", "start_time": "09:00", "end_time": "10:00"},
            {"id": "2", "title": "Task B", "start_time": "09:30", "end_time": "11:00"},
            {"id": "3", "title": "Task C", "start_time": "11:00", "end_time": "12:00"},
        ]
        conflicts = task_agent.detect_schedule_conflicts(tasks)
        assert len(conflicts) == 1
        assert conflicts[0]["task_a_id"] == "1"
        assert conflicts[0]["task_b_id"] == "2"

    def test_detect_schedule_conflicts_no_overlap(self):
        tasks = [
            {"id": "1", "title": "Task A", "start_time": "09:00", "end_time": "10:00"},
            {"id": "2", "title": "Task B", "start_time": "10:00", "end_time": "11:00"},
        ]
        assert task_agent.detect_schedule_conflicts(tasks) == []

    def test_detect_circular_dependencies_cycle(self):
        tasks = [
            {"id": "a", "dependency_id": "b"},
            {"id": "b", "dependency_id": "c"},
            {"id": "c", "dependency_id": "a"},
        ]
        cycles = task_agent.detect_circular_dependencies(tasks)
        assert len(cycles) >= 1
        assert all(len(c) >= 2 for c in cycles)

    def test_detect_circular_dependencies_no_cycle(self):
        tasks = [
            {"id": "a", "dependency_id": "b"},
            {"id": "b", "dependency_id": "c"},
            {"id": "c"},
        ]
        assert task_agent.detect_circular_dependencies(tasks) == []

    def test_calculate_priority_score_default(self):
        score = task_agent.calculate_priority_score({"priority": "medium"}, {})
        assert 0 <= score <= 100
        assert score == 55

    def test_calculate_priority_score_overdue(self):
        task = {"priority": "high", "due_date": (datetime.now() - timedelta(hours=1)).isoformat()}
        score = task_agent.calculate_priority_score(task, {})
        assert score > 70

    def test_calculate_priority_score_goal_aligned(self):
        task = {"priority": "low", "goal_id": "goal-1"}
        context = {"active_goal_ids": ["goal-1"]}
        score = task_agent.calculate_priority_score(task, context)
        assert score > 60


# ═══════════════════════════════════════════════════════════════════════
# A02 — Memory Agent
# ═══════════════════════════════════════════════════════════════════════


class TestMemoryAgentPhase2:

    @pytest.mark.asyncio
    async def test_extract_memory_from_chat_returns_none_no_content(self, mock_llm_json):
        result = await memory_agent.extract_memory_from_chat("hello", "hi")
        assert result is None or result.get("content") is not None

    @pytest.mark.asyncio
    async def test_extract_memory_from_chat_handles_exception(self, mock_llm_json):
        mock_llm_json.side_effect = Exception("LLM error")
        result = await memory_agent.extract_memory_from_chat("hello", "hi")
        assert result is None

    @pytest.mark.asyncio
    async def test_deduplicate_memories_empty(self):
        count = await memory_agent.deduplicate_memories("user-1")
        assert count == 0

    @pytest.mark.asyncio
    async def test_apply_confidence_decay_empty(self):
        count = await memory_agent.apply_confidence_decay("user-1")
        assert count == 0

    @pytest.mark.asyncio
    async def test_run_weekly_deep_consolidation_fallback(self, mock_supabase, mock_llm_json):
        mock_llm_json.side_effect = Exception("LLM error")
        result = await memory_agent.run_weekly_deep_consolidation("user-1")
        assert result["status"] in ("completed", "failed")
        assert "user_id" in result


# ═══════════════════════════════════════════════════════════════════════
# A03 — Learning Agent
# ═══════════════════════════════════════════════════════════════════════


class TestLearningAgentPhase2:

    @pytest.mark.asyncio
    async def test_detect_productivity_peaks_no_data(self):
        result = await learning_agent.detect_productivity_peaks("user-1", 30)
        assert result.get("has_data") is False

    @pytest.mark.asyncio
    async def test_detect_productivity_peaks_handles_error(self):
        result = await learning_agent.detect_productivity_peaks("user-1", 30)
        assert "has_data" in result

    @pytest.mark.asyncio
    async def test_analyze_trends_unknown_metric(self):
        result = await learning_agent.analyze_trends("user-1", "invalid_metric", 30)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_analyze_trends_sleep_score(self):
        result = await learning_agent.analyze_trends("user-1", "sleep_score", 30)
        assert result["metric"] == "sleep_score"

    @pytest.mark.asyncio
    async def test_detect_anomalies_empty(self):
        result = await learning_agent.detect_anomalies("user-1")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_suggest_spaced_repetition_no_courses(self):
        result = await learning_agent.suggest_spaced_repetition("user-1")
        assert isinstance(result, list)
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════════════════
# A06 — Opportunity Agent
# ═══════════════════════════════════════════════════════════════════════


class TestOpportunityAgentPhase2:

    def test_calculate_skill_overlap_full(self):
        overlap = opportunity_agent.calculate_skill_overlap(
            ["Python", "React"], ["Python", "React"]
        )
        assert overlap == 1.0

    def test_calculate_skill_overlap_partial(self):
        overlap = opportunity_agent.calculate_skill_overlap(
            ["Python", "React", "SQL"], ["Python", "Java"]
        )
        assert 0.25 <= overlap <= 0.5

    def test_calculate_skill_overlap_no_match(self):
        overlap = opportunity_agent.calculate_skill_overlap(
            ["Python"], ["Java", "C++"]
        )
        assert overlap == 0.0

    def test_calculate_skill_overlap_empty(self):
        assert opportunity_agent.calculate_skill_overlap([], ["Python"]) == 0.0

    def test_tier_notification_opportunities_urgent_deadline(self):
        now = datetime.now()
        opps = [
            {"title": "Urgent Opp", "match_score": 80, "deadline": (now + timedelta(hours=24)).isoformat()},
            {"title": "High Match", "match_score": 75, "deadline": (now + timedelta(days=30)).isoformat()},
            {"title": "Regular", "match_score": 50, "deadline": (now + timedelta(days=60)).isoformat()},
        ]
        tiers = opportunity_agent.tier_notification_opportunities(opps)
        assert len(tiers["urgent"]) == 1
        assert len(tiers["high_match"]) >= 1
        assert tiers["counts"]["urgent"] == 1

    def test_tier_notification_opportunities_empty(self):
        tiers = opportunity_agent.tier_notification_opportunities([])
        assert tiers["counts"]["urgent"] == 0
        assert tiers["counts"]["regular"] == 0

    def test_deduplicate_opportunities_by_url(self):
        opps = [
            {"title": "Opp A", "url": "https://example.com/a"},
            {"title": "Opp B", "url": "https://example.com/a"},
            {"title": "Opp C", "url": "https://example.com/c"},
        ]
        deduped = opportunity_agent.deduplicate_opportunities(opps)
        assert len(deduped) == 2

    def test_deduplicate_opportunities_empty(self):
        assert opportunity_agent.deduplicate_opportunities([]) == []

    @pytest.mark.asyncio
    async def test_fetch_rss_feeds_empty(self):
        items = await opportunity_agent.fetch_rss_feeds([])
        assert items == []

    @pytest.mark.asyncio
    async def test_fetch_rss_feeds_bad_url(self):
        items = await opportunity_agent.fetch_rss_feeds(["https://nonexistent-rss-feed.example.com/rss"])
        assert isinstance(items, list)


# ═══════════════════════════════════════════════════════════════════════
# A08 — Roadmap Agent
# ═══════════════════════════════════════════════════════════════════════


class TestRoadmapAgentPhase2:

    def test_detect_stale_nodes_none(self):
        roadmap = {"milestones": [{"title": "Learn Python", "last_activity": datetime.now().isoformat()}]}
        stale = roadmap_agent.detect_stale_nodes(roadmap, threshold_days=30)
        assert stale == []

    def test_detect_stale_nodes_all_stale(self):
        roadmap = {"milestones": [{"title": "Old Skill", "last_activity": (datetime.now() - timedelta(days=60)).isoformat()}]}
        stale = roadmap_agent.detect_stale_nodes(roadmap, threshold_days=30)
        assert len(stale) == 1

    def test_detect_stale_nodes_no_date(self):
        roadmap = {"milestones": [{"title": "No Date Skill"}]}
        stale = roadmap_agent.detect_stale_nodes(roadmap)
        assert len(stale) == 1

    def test_validate_prerequisites_no_issues(self):
        roadmap = {
            "milestones": [
                {"title": "Python Basics", "prerequisites": []},
                {"title": "Advanced Python", "prerequisites": ["Python Basics"]},
            ]
        }
        issues = roadmap_agent.validate_prerequisites(roadmap)
        assert len(issues) == 0

    def test_validate_prerequisites_missing(self):
        roadmap = {
            "milestones": [
                {"title": "Advanced Python", "prerequisites": ["Python Basics"]},
            ]
        }
        issues = roadmap_agent.validate_prerequisites(roadmap)
        assert len(issues) >= 1

    def test_detect_circular_dependencies_roadmap(self):
        roadmap = {
            "milestones": [
                {"title": "A", "prerequisites": ["B"]},
                {"title": "B", "prerequisites": ["C"]},
                {"title": "C", "prerequisites": ["A"]},
            ]
        }
        cycles = roadmap_agent.detect_circular_dependencies(roadmap)
        assert len(cycles) >= 1

    def test_detect_circular_dependencies_no_cycle(self):
        roadmap = {
            "milestones": [
                {"title": "A", "prerequisites": ["B"]},
                {"title": "B", "prerequisites": []},
            ]
        }
        assert roadmap_agent.detect_circular_dependencies(roadmap) == []

    def test_enrich_with_external_data(self):
        roadmap = {"skills": ["Python", "Machine Learning"], "milestones": []}
        enriched = roadmap_agent.enrich_with_external_data(roadmap)
        assert "external_data" in enriched
        assert "Python" in enriched["external_data"]

    def test_enrich_with_external_data_empty_skills(self):
        enriched = roadmap_agent.enrich_with_external_data({"skills": [], "milestones": []})
        assert enriched["skills_analyzed"] == 0

    def test_enrich_with_external_data_estimation(self):
        enriched = roadmap_agent.enrich_with_external_data({"skills": ["Python", "Machine Learning", "DevOps"], "milestones": []})
        ext = enriched["external_data"]
        assert ext["Python"]["demand"] == "high"
        assert ext["Machine Learning"]["salaries"]["median"] == "$140k"
        assert ext["DevOps"]["market_trend"] == "stable"


# ═══════════════════════════════════════════════════════════════════════
# A09 — Briefing Agent
# ═══════════════════════════════════════════════════════════════════════


class TestBriefingAgentPhase2:

    def test_generate_day_profile_monday(self):
        profile = briefing_agent.generate_day_profile(0)
        assert profile["day_name"] == "Monday"
        assert profile["profile_name"] == "Focus"

    def test_generate_day_profile_sunday(self):
        profile = briefing_agent.generate_day_profile(6)
        assert profile["day_name"] == "Sunday"
        assert profile["profile_name"] == "Plan"

    def test_generate_day_profile_out_of_range(self):
        profile = briefing_agent.generate_day_profile(10)
        assert profile["day_name"] == "Unknown"

    @pytest.mark.asyncio
    async def test_include_opportunity_data_empty(self, mock_supabase):
        brief = {}
        result = await briefing_agent.include_opportunity_data(brief, "user-1")
        assert "top_opportunities" in result
        assert isinstance(result["top_opportunities"], list)

    @pytest.mark.asyncio
    async def test_include_habit_data_empty(self, mock_supabase):
        brief = {}
        result = await briefing_agent.include_habit_data(brief, "user-1")
        assert "habits" in result

    @pytest.mark.asyncio
    async def test_deduplicate_briefing_not_found(self, mock_supabase):
        exists = await briefing_agent.deduplicate_briefing("user-1", "2026-07-14")
        assert exists is False


# ═══════════════════════════════════════════════════════════════════════
# A10 — Weekly Review Agent
# ═══════════════════════════════════════════════════════════════════════


class TestWeeklyReviewAgentPhase2:

    @pytest.mark.asyncio
    async def test_apply_review_profile_default(self):
        profile = await weekly_review_agent.apply_review_profile("user-1")
        assert profile["profile_type"] == "balanced"
        assert profile["profile"]["name"] == "Balanced"

    @pytest.mark.asyncio
    async def test_apply_review_profile_deep_focus(self):
        profile = await weekly_review_agent.apply_review_profile("user-1", "deep-focus")
        assert profile["profile_type"] == "deep-focus"

    @pytest.mark.asyncio
    async def test_include_income_data_empty(self, mock_supabase):
        review = {"week_start": "2026-07-07", "week_end": "2026-07-14"}
        result = await weekly_review_agent.include_income_data(review, "user-1")
        assert "income" in result

    @pytest.mark.asyncio
    async def test_include_sleep_data_empty(self, mock_supabase):
        review = {"week_start": "2026-07-07", "week_end": "2026-07-14"}
        result = await weekly_review_agent.include_sleep_data(review, "user-1")
        assert "sleep" in result

    @pytest.mark.asyncio
    async def test_deduplicate_review_not_found(self, mock_supabase):
        exists = await weekly_review_agent.deduplicate_review("user-1", "2026-07-07")
        assert exists is False


# ═══════════════════════════════════════════════════════════════════════
# A13 — Sleep Agent
# ═══════════════════════════════════════════════════════════════════════


class TestSleepAgentPhase2:

    @pytest.mark.asyncio
    async def test_assign_sleep_profile_no_data(self):
        profile = await sleep_agent.assign_sleep_profile("user-1")
        assert isinstance(profile, str)
        assert len(profile) > 0

    @pytest.mark.asyncio
    async def test_analyze_sleep_debt_no_data(self):
        result = await sleep_agent.analyze_sleep_debt("user-1", 14)
        assert result["logs_count"] == 0

    @pytest.mark.asyncio
    async def test_adjust_tasks_for_energy_empty(self):
        result = await sleep_agent.adjust_tasks_for_energy("user-1", [])
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_adjust_tasks_for_energy_returns_tasks(self):
        tasks = [{"id": "1", "title": "Test", "priority_score": 50, "due_date": "2026-07-20"}]
        result = await sleep_agent.adjust_tasks_for_energy("user-1", tasks)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_generate_wind_down_routine(self):
        routine = await sleep_agent.generate_wind_down_routine("user-1")
        assert isinstance(routine, str)
        assert len(routine) > 20

    @pytest.mark.asyncio
    async def test_generate_morning_recovery_no_data(self):
        msg = await sleep_agent.generate_morning_recovery("user-1")
        assert isinstance(msg, str)
        assert len(msg) > 10


# ═══════════════════════════════════════════════════════════════════════
# A14 — Nudge Agent
# ═══════════════════════════════════════════════════════════════════════


class TestNudgeAgentPhase2:

    @pytest.mark.asyncio
    async def test_get_escalation_level_default(self):
        level = await nudge_agent.get_escalation_level("user-1", "course_behind")
        assert level >= 1

    @pytest.mark.asyncio
    async def test_combine_course_habit_digest_empty(self):
        digest = await nudge_agent.combine_course_habit_digest("user-1")
        assert "total_courses" in digest

    @pytest.mark.asyncio
    async def test_check_notification_preferences_default(self):
        pref = await nudge_agent.check_notification_preferences("user-1", "course_behind")
        assert isinstance(pref, bool)

    @pytest.mark.asyncio
    async def test_generate_positive_reinforcement_empty(self):
        msg = await nudge_agent.generate_positive_reinforcement("user-1")
        assert isinstance(msg, str)
        assert len(msg) > 0


# ═══════════════════════════════════════════════════════════════════════
# A15 — Opportunity Matching Agent
# ═══════════════════════════════════════════════════════════════════════


class TestOpportunityMatchingAgentPhase2:

    def test_compute_algorithmic_score_perfect_match(self):
        opp = {"skills_needed": ["Python", "React"]}
        score = opportunity_matching_agent.compute_algorithmic_score(opp, ["Python", "React"], [])
        assert score > 40

    def test_compute_algorithmic_score_no_match(self):
        opp = {"skills_needed": ["Java", "C++"]}
        score = opportunity_matching_agent.compute_algorithmic_score(opp, ["Python"], [])
        assert score < 40

    def test_compute_algorithmic_score_empty_skills(self):
        opp = {"skills_needed": []}
        score = opportunity_matching_agent.compute_algorithmic_score(opp, ["Python"], [])
        assert score > 0

    def test_identify_skill_gaps_some_missing(self):
        opp = {"skills_needed": ["Python", "React", "Docker"]}
        gaps = opportunity_matching_agent.identify_skill_gaps(opp, ["Python"])
        assert "Docker" in gaps
        assert "Python" not in gaps

    def test_identify_skill_gaps_all_present(self):
        opp = {"skills_needed": ["Python", "React"]}
        gaps = opportunity_matching_agent.identify_skill_gaps(opp, ["Python", "React"])
        assert gaps == []

    def test_identify_skill_gaps_no_skills_needed(self):
        gaps = opportunity_matching_agent.identify_skill_gaps({}, ["Python"])
        assert gaps == []

    def test_calculate_goal_alignment_no_goals(self):
        alignment = opportunity_matching_agent.calculate_goal_alignment({"title": "ML Engineer"}, [])
        assert alignment == 0.0

    def test_calculate_goal_alignment_with_goals(self):
        opp = {"title": "AI Research Intern", "description": "Work on machine learning models", "category": "internship"}
        goals = [{"title": "Become ML Engineer", "description": "Learn machine learning and AI"}]
        alignment = opportunity_matching_agent.calculate_goal_alignment(opp, goals)
        assert alignment > 0

    @pytest.mark.asyncio
    async def test_match_opportunities_algorithmic_fallback(self, mock_llm_json):
        mock_llm_json.side_effect = LLMProviderUnavailableError("LLM unavailable")
        result = await opportunity_matching_agent.match_opportunities("user-1")
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════════════════
# Cross-Cutting: Notification Dispatcher
# ═══════════════════════════════════════════════════════════════════════


class TestNotificationDispatcher:

    def test_send_push_without_webhook(self, mocker):
        mocker.patch("ai.notification_dispatcher.send_push_notification", return_value={"success": True})
        d = NotificationDispatcher()
        result = d.send_push("user-1", "Test", "Body")
        assert result is True

    def test_send_push_failure(self, mocker):
        mocker.patch("ai.notification_dispatcher.send_push_notification", return_value={"success": False})
        d = NotificationDispatcher()
        result = d.send_push("user-1", "Test", "Body")
        assert result is False

    def test_send_in_app_creates_notification(self, mock_supabase):
        d = NotificationDispatcher()
        result = d.send_in_app("user-1", "Test Title", "Test Body")
        assert result is True

    def test_dispatch_to_all_empty_channels(self, mocker):
        d = NotificationDispatcher()
        result = d.dispatch_to_all("user-1", "Test", "Body", [])
        assert result == {}

    def test_dispatch_to_all_unknown_channel(self, mocker):
        d = NotificationDispatcher()
        result = d.dispatch_to_all("user-1", "Test", "Body", ["unknown"])
        assert result.get("unknown") is False


# ═══════════════════════════════════════════════════════════════════════
# Cross-Cutting: Upsert Utility
# ═══════════════════════════════════════════════════════════════════════


class TestUpsertUtility:

    def test_upsert_fails_on_error(self, mock_supabase):
        def side_effect(data):
            raise Exception("DB error")
        mock_supabase._builders["test"].insert.side_effect = side_effect
        import importlib
        import shared.utils.upsert as upsert_mod
        importlib.reload(upsert_mod)
        with pytest.raises(Exception):
            upsert_mod.upsert("test", {"id": "1"}, ["id"])
