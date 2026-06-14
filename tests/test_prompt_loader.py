import pytest
from pathlib import Path
from ai.prompt_loader import PromptLoader, PromptEntry


@pytest.fixture
def loader():
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    return PromptLoader(prompts_dir)


class TestPromptLoader:
    def test_loads_system_prompts(self, loader):
        entry = loader.get_system("aria_system")
        assert entry is not None
        assert entry.name == "aria_system"
        assert "ARIA" in entry.body

    def test_loads_agent_prompts(self, loader):
        entry = loader.get_agent("briefing_agent")
        assert entry is not None
        assert entry.name == "briefing_agent"
        assert "ARIA Daily Briefing" in entry.body

    def test_loads_templates(self, loader):
        entry = loader.get_template("context_assembly")
        assert entry is not None or loader.get_template("email_templates") is not None

    def test_all_prompts_have_frontmatter(self, loader):
        for key, entry in loader._entries.items():
            assert entry.frontmatter, f"{key} has no frontmatter"

    def test_all_prompts_have_version(self, loader):
        for key, entry in loader._entries.items():
            assert "version" in entry.frontmatter, f"{key} missing version"

    def test_all_prompts_have_valid_status(self, loader):
        for key, entry in loader._entries.items():
            assert entry.frontmatter.get("status") in ("active", "draft", "deprecated"), \
                f"{key} has invalid status: {entry.frontmatter.get('status')}"

    def test_all_prompts_have_model(self, loader):
        for key, entry in loader._entries.items():
            assert "model" in entry.frontmatter, f"{key} missing model"

    def test_all_prompts_have_max_tokens(self, loader):
        for key, entry in loader._entries.items():
            assert isinstance(entry.frontmatter.get("max_tokens"), (int, float)), \
                f"{key} missing or invalid max_tokens"

    def test_all_prompts_have_temperature(self, loader):
        for key, entry in loader._entries.items():
            assert isinstance(entry.frontmatter.get("temperature"), (int, float)), \
                f"{key} missing or invalid temperature"

    def test_get_returns_none_for_missing(self, loader):
        assert loader.get("nonexistent_prompt") is None

    def test_get_by_category(self, loader):
        entry = loader.get("briefing_agent", category="agents")
        assert entry is not None

    def test_list_prompts(self, loader):
        all_keys = loader.list_prompts()
        assert len(all_keys) > 0
        system_keys = loader.list_prompts("system")
        assert len(system_keys) >= 1
        agent_keys = loader.list_prompts("agents")
        assert len(agent_keys) >= 6

    def test_validate_all_returns_no_errors(self, loader):
        errors = loader.validate_all()
        if errors:
            for key, errs in errors.items():
                pytest.fail(f"{key}: {errs}")
        assert len(errors) == 0, f"Found {len(errors)} prompts with errors: {errors}"


class TestPromptEntry:
    def test_has_body(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active"},
            "Hello {name}",
            Path("test.md"),
        )
        assert entry.body == "Hello {name}"
        assert entry.name == "test"

    def test_render_with_kwargs(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active"},
            "Hello {name}, your score is {score}",
            Path("test.md"),
        )
        result = entry.render(name="Alice", score=95)
        assert result == "Hello Alice, your score is 95"

    def test_render_without_kwargs(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active"},
            "Plain text prompt",
            Path("test.md"),
        )
        assert entry.render() == "Plain text prompt"
