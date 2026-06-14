import pytest
from pathlib import Path
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
        assert any(word in prompt.body.lower()
                   for word in ["guardrail", "safety", "constraint", "limit", "boundary"])


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
