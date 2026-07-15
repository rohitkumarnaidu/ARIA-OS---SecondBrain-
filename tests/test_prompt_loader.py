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
            assert entry.frontmatter.get("status") in (
                "active",
                "draft",
                "deprecated",
            ), f"{key} has invalid status: {entry.frontmatter.get('status')}"

    def test_all_prompts_have_model(self, loader):
        for key, entry in loader._entries.items():
            assert "model" in entry.frontmatter, f"{key} missing model"

    def test_all_prompts_have_max_tokens(self, loader):
        for key, entry in loader._entries.items():
            assert isinstance(entry.frontmatter.get("max_tokens"), (int, float)), f"{key} missing or invalid max_tokens"

    def test_all_prompts_have_temperature(self, loader):
        for key, entry in loader._entries.items():
            assert isinstance(
                entry.frontmatter.get("temperature"), (int, float)
            ), f"{key} missing or invalid temperature"

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

    def test_get_required_returns_entry(self, loader):
        entry = loader.get_required("aria_system", category="system")
        assert entry is not None
        assert entry.name == "aria_system"

    def test_get_required_raises_for_missing(self, loader):
        from ai.prompt_loader import PromptLoaderError

        with pytest.raises(PromptLoaderError):
            loader.get_required("nonexistent_prompt")

    def test_count_prompts(self, loader):
        counts = loader.count_prompts()
        assert "system" in counts
        assert "agents" in counts
        assert "templates" in counts
        assert counts["system"] >= 1
        assert counts["agents"] >= 6
        assert counts["templates"] >= 1

    def test_list_categories(self, loader):
        cats = loader.list_categories()
        assert len(cats) >= 3
        assert "system" in cats
        assert "agents" in cats
        assert "templates" in cats

    def test_reload(self, loader):
        before = loader.count_prompts()
        loader.reload()
        after = loader.count_prompts()
        assert before == after

    def test_get_system_entry_properties(self, loader):
        entry = loader.get_system("aria_system")
        assert entry is not None
        assert entry.category == "system"
        assert entry.system_prompt == entry.body

    def test_get_agent_entry_properties(self, loader):
        entry = loader.get_agent("briefing_agent")
        assert entry is not None
        assert entry.category == "agents"
        assert entry.agent_prompt == entry.body

    def test_gate_loaded_once(self):
        """Ensure PromptLoader singleton is already populated (gate import)."""
        from ai.prompt_loader import prompts

        assert prompts.count_prompts()["system"] >= 1


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

    def test_validate_missing_required_field(self):
        entry = PromptEntry({}, "body", Path("test.md"))
        errors = entry.validate()
        assert "Missing required field: version" in errors
        assert "Missing required field: status" in errors
        assert "Missing required field: model" in errors
        assert "Missing required field: max_tokens" in errors
        assert "Missing required field: temperature" in errors

    def test_validate_invalid_status(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "invalid", "model": "m", "max_tokens": 100, "temperature": 0.5},
            "body",
            Path("test.md"),
        )
        errors = entry.validate()
        assert any("Invalid status" in e for e in errors)

    def test_validate_max_tokens_not_number(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active", "model": "m", "max_tokens": "not-a-number", "temperature": 0.5},
            "body",
            Path("test.md"),
        )
        errors = entry.validate()
        assert any("max_tokens must be a number" in e for e in errors)

    def test_validate_temperature_not_number(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active", "model": "m", "max_tokens": 100, "temperature": "hot"},
            "body",
            Path("test.md"),
        )
        errors = entry.validate()
        assert any("temperature must be a number" in e for e in errors)

    def test_render_keyerror_returns_body_unchanged(self):
        entry = PromptEntry(
            {"version": "1.0", "status": "active"},
            "Hello {name}, your balance is {balance}",
            Path("test.md"),
        )
        result = entry.render(name="Alice")
        assert result == "Hello {name}, your balance is {balance}"

    def test_parse_no_frontmatter(self):
        from ai.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=Path("."))
        content = "# Just a body\nNo frontmatter here."
        frontmatter, body = loader._parse_frontmatter(content)
        assert frontmatter == {}
        assert "No frontmatter" in body

    def test_validate_frontmatter_not_found(self, loader):
        errors = loader.validate_frontmatter("nonexistent_prompt")
        assert errors == ["Prompt not found"]

    def test_validate_all_with_errors(self, tmp_path):
        bad = tmp_path / "bad.md"
        bad.write_text("---\nversion: 1.0\n---\nBody")
        from ai.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=tmp_path)
        all_errors = loader.validate_all()
        assert len(all_errors) > 0
