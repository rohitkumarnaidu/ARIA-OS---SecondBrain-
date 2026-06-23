"""Tests for agent prompts and agent module integration."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from ai.prompt_loader import PromptLoader


@pytest.fixture
def loader():
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    return PromptLoader(prompts_dir)


class TestAgentPrompts:
    def test_briefing_agent_prompt(self, loader):
        prompt = loader.get_agent("briefing_agent")
        assert prompt is not None
        assert "generating" in prompt.body.lower() or "briefing" in prompt.body.lower()
        assert prompt.frontmatter.get("temperature", 0) >= 0
        assert prompt.frontmatter.get("max_tokens", 0) > 0

    def test_memory_agent_prompt(self, loader):
        prompt = loader.get_agent("memory_agent")
        assert prompt is not None
        assert "memory" in prompt.body.lower() or "summar" in prompt.body.lower()
        assert prompt.frontmatter.get("status") == "active"

    def test_learning_agent_prompt(self, loader):
        prompt = loader.get_agent("learning_agent")
        assert prompt is not None
        assert "learning" in prompt.body.lower() or "pattern" in prompt.body.lower()

    def test_opportunity_radar_prompt(self, loader):
        prompt = loader.get_agent("opportunity_radar_agent")
        assert prompt is not None
        assert "opportunity" in prompt.body.lower() or "career" in prompt.body.lower()

    def test_task_agent_prompt(self, loader):
        prompt = loader.get_agent("task_agent")
        assert prompt is not None
        assert "task" in prompt.body.lower() or "breakdown" in prompt.body.lower()

    def test_sleep_agent_prompt(self, loader):
        prompt = loader.get_agent("sleep_agent")
        assert prompt is not None
        assert "sleep" in prompt.body.lower() or "wind-down" in prompt.body.lower()

    def test_nudge_agent_prompt(self, loader):
        prompt = loader.get_agent("nudge_agent")
        assert prompt is not None
        assert "nudge" in prompt.body.lower() or "habit" in prompt.body.lower()

    def test_weekly_review_agent_prompt(self, loader):
        prompt = loader.get_agent("weekly_review_agent")
        assert prompt is not None
        assert "weekly" in prompt.body.lower() or "review" in prompt.body.lower()

    def test_roadmap_agent_prompt(self, loader):
        prompt = loader.get_agent("roadmap_agent")
        assert prompt is not None
        assert "roadmap" in prompt.body.lower() or "milestone" in prompt.body.lower()

    def test_opportunity_matching_agent_prompt(self, loader):
        prompt = loader.get_agent("opportunity_matching_agent")
        assert prompt is not None
        assert "match" in prompt.body.lower() or "scor" in prompt.body.lower()

    def test_all_agent_prompts_have_tags(self, loader):
        for key in loader.list_prompts("agents"):
            entry = loader.get(key.split("/")[-1])
            assert entry is not None
            assert "tags" in entry.frontmatter, f"{key} missing tags"

    def test_all_system_prompts_have_description(self, loader):
        for key in loader.list_prompts("system"):
            entry = loader.get(key.split("/")[-1])
            assert entry is not None
            assert entry.frontmatter.get("description", ""), f"{key} missing description"


class TestSystemPrompts:
    def test_aria_system_prompt(self, loader):
        prompt = loader.get_system("aria_system")
        assert prompt is not None
        assert "ARIA" in prompt.body
        assert "persona" in prompt.body.lower() or "orchestrat" in prompt.body.lower()

    def test_guardrails_prompt(self, loader):
        prompt = loader.get_system("guardrails")
        assert prompt is not None
        assert any(word in prompt.body.lower() for word in ["guardrail", "safety", "constraint", "limit", "boundary"])


class TestFileSize:
    def test_prompt_files_are_not_empty(self, loader):
        for key, entry in loader._entries.items():
            content_length = len(entry.body)
            assert content_length > 0, f"{key} has empty body"
            assert content_length > 50, f"{key} body is suspiciously short ({content_length} chars)"

    def test_agent_prompts_are_substantial(self, loader):
        for key in loader.list_prompts("agents"):
            entry = loader.get(key.split("/")[-1])
            assert entry is not None
            assert len(entry.body) > 1000, f"{key} is too short ({len(entry.body)} chars)"


# ─── Agent Module Integration Tests ───────────────────────────────────────────


class TestAgentModuleImports:
    """Verify all agent modules export their main function correctly."""

    def test_briefing_agent_has_function(self):
        from ai.agents.briefing_agent import generate_daily_briefing
        assert callable(generate_daily_briefing)

    def test_weekly_review_agent_has_function(self):
        from ai.agents.weekly_review_agent import generate_weekly_review
        assert callable(generate_weekly_review)

    def test_memory_agent_has_functions(self):
        from ai.agents.memory_agent import (
            store_interaction,
            get_recent_interactions,
            get_user_preferences,
            get_session_context,
            consolidate_memories,
            get_memory_summary,
            prune_expired_memories,
        )
        for fn in [store_interaction, get_recent_interactions, get_user_preferences,
                   get_session_context, consolidate_memories, get_memory_summary,
                   prune_expired_memories]:
            assert callable(fn)

    def test_learning_agent_has_functions(self):
        from ai.agents.learning_agent import track_user_progress, detect_learning_patterns, suggest_learning_focus
        for fn in [track_user_progress, detect_learning_patterns, suggest_learning_focus]:
            assert callable(fn)

    def test_sleep_agent_has_functions(self):
        from ai.agents.sleep_agent import analyze_sleep, suggest_bedtime
        for fn in [analyze_sleep, suggest_bedtime]:
            assert callable(fn)

    def test_nudge_agent_has_functions(self):
        from ai.agents.nudge_agent import generate_nudge, check_course_nudges, check_habit_streaks, run_all_nudges
        for fn in [generate_nudge, check_course_nudges, check_habit_streaks, run_all_nudges]:
            assert callable(fn)

    def test_task_agent_has_functions(self):
        from ai.agents.task_agent import breakdown_task, check_missed_tasks, suggest_task_prioritization, auto_reschedule_overdue
        for fn in [breakdown_task, check_missed_tasks, suggest_task_prioritization, auto_reschedule_overdue]:
            assert callable(fn)

    def test_opportunity_agent_has_functions(self):
        from ai.agents.opportunity_agent import run_opportunity_radar, scan_default_opportunities, calculate_match_score
        for fn in [run_opportunity_radar, scan_default_opportunities, calculate_match_score]:
            assert callable(fn)

    def test_opportunity_matching_agent_has_function(self):
        from ai.agents.opportunity_matching_agent import match_opportunities
        assert callable(match_opportunities)

    def test_roadmap_agent_has_function(self):
        from ai.agents.roadmap_agent import optimize_roadmap
        assert callable(optimize_roadmap)


class TestAgentModuleExports:
    """Verify __init__ exports all modules."""

    def test_all_modules_in_export(self):
        from ai.agents import __all__
        expected = [
            "task_agent",
            "memory_agent",
            "learning_agent",
            "opportunity_agent",
            "briefing_agent",
            "weekly_review_agent",
            "sleep_agent",
            "nudge_agent",
            "roadmap_agent",
            "opportunity_matching_agent",
        ]
        for mod in expected:
            assert mod in __all__, f"{mod} missing from __all__"


class TestAgentPromptLoaded:
    """Verify each agent module's prompt is loadable and has correct structure."""

    AGENTS = [
        ("briefing_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("weekly_review_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("memory_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("learning_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("sleep_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("nudge_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("task_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("opportunity_radar_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("opportunity_matching_agent", ["version", "status", "model", "max_tokens", "temperature"]),
        ("roadmap_agent", ["version", "status", "model", "max_tokens", "temperature"]),
    ]

    def test_all_agents_have_required_frontmatter(self, loader):
        for name, required_fields in self.AGENTS:
            entry = loader.get_agent(name)
            assert entry is not None, f"{name} prompt not found"
            for field in required_fields:
                assert field in entry.frontmatter, f"{name} missing field: {field}"

    def test_all_agent_prompts_valid(self, loader):
        for name, _ in self.AGENTS:
            entry = loader.get_agent(name)
            assert entry is not None
            errors = entry.validate()
            assert not errors, f"{name} validation errors: {errors}"

    def test_all_agents_have_tags(self, loader):
        for name, _ in self.AGENTS:
            entry = loader.get_agent(name)
            assert entry is not None
            assert "tags" in entry.frontmatter, f"{name} missing tags"

    def test_agent_category_is_correct(self, loader):
        for name, _ in self.AGENTS:
            entry = loader.get(name, category="agents")
            assert entry is not None, f"{name} not found in agents category"


class TestAgentFunctionSignatures:
    """Verify agent functions accept user_id parameter."""

    def test_briefing_agent_signature(self):
        from ai.agents.briefing_agent import generate_daily_briefing
        import inspect
        sig = inspect.signature(generate_daily_briefing)
        assert "user_id" in sig.parameters

    def test_weekly_review_agent_signature(self):
        from ai.agents.weekly_review_agent import generate_weekly_review
        import inspect
        sig = inspect.signature(generate_weekly_review)
        assert "user_id" in sig.parameters

    def test_roadmap_agent_signature(self):
        from ai.agents.roadmap_agent import optimize_roadmap
        import inspect
        sig = inspect.signature(optimize_roadmap)
        assert "user_id" in sig.parameters

    def test_opportunity_matching_agent_signature(self):
        from ai.agents.opportunity_matching_agent import match_opportunities
        import inspect
        sig = inspect.signature(match_opportunities)
        assert "user_id" in sig.parameters

    def test_sleep_analyze_signature(self):
        from ai.agents.sleep_agent import analyze_sleep
        import inspect
        sig = inspect.signature(analyze_sleep)
        assert "user_id" in sig.parameters
        assert "date" in sig.parameters


class TestAgentDefaultOpportunities:
    """Test the scan_default_opportunities utility."""

    def test_scan_default_opportunities_returns_list(self):
        from ai.agents.opportunity_agent import scan_default_opportunities
        result = scan_default_opportunities(["Python", "React"])
        assert len(result) == 3
        assert all("title" in o for o in result)
        assert all("category" in o for o in result)
        assert all("match_score" in o for o in result)
        assert result[0]["match_score"] == 80
        assert result[1]["match_score"] == 75
        assert result[2]["match_score"] == 85

    def test_calculate_match_score(self):
        from ai.agents.opportunity_agent import calculate_match_score
        result = calculate_match_score({"match_score": 88}, ["Python"], ["AI"])
        assert result == 88

    def test_calculate_match_score_default(self):
        from ai.agents.opportunity_agent import calculate_match_score
        result = calculate_match_score({}, ["Python"], ["AI"])
        assert result == 50

    def test_nudge_types_are_defined(self):
        from ai.agents.nudge_agent import NUDGE_TYPES
        expected = ["course_behind", "habit_miss_2day", "habit_miss_5day", "multiple_courses_behind", "streak_at_risk"]
        assert NUDGE_TYPES == expected


class TestAgentPromptEdgeCases:
    """Test prompt edge cases: missing prompts, alternate prompts, etc."""

    def test_missing_agent_prompt_returns_none(self, loader):
        entry = loader.get_agent("nonexistent_agent_xyz")
        assert entry is None

    def test_prompts_dir_has_no_readme_as_prompt(self, loader):
        readme_keys = [k for k in loader._entries if "README" in k]
        assert len(readme_keys) == 0
