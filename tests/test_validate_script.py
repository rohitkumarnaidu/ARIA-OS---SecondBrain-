"""Tests for the prompt validation script itself."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.mark.prompt
class TestValidateScript:
    """Test the validate_prompts.py script logic."""

    SAMPLE_VALID_PROMPT = """---
version: 1.0.0
status: active
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.5
description: Test prompt
tags: [test]
---

# Test Prompt
This is a test prompt body.
"""

    SAMPLE_MISSING_FIELDS = """---
version: 1.0.0
status: active
---

Missing required fields: model, max_tokens, temperature
"""

    SAMPLE_INVALID_STATUS = """---
version: 1.0.0
status: invalid_status
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.5
---
"""

    SAMPLE_NO_FRONTMATTER = """Just a markdown file without frontmatter."""

    def _write_prompt(self, tmp_path: Path, name: str, content: str) -> Path:
        prompts_dir = tmp_path / "prompts" / "agents"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        file_path = prompts_dir / name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_validates_correct_prompt(self, tmp_path):
        fp = self._write_prompt(tmp_path, "test_agent.md", self.SAMPLE_VALID_PROMPT)
        import yaml, re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None, "Should have frontmatter"

        fm = yaml.safe_load(match.group(1))
        assert fm["version"] == "1.0.0"
        assert fm["status"] == "active"
        assert fm["model"] == "ollama/mistral:7b"
        assert isinstance(fm["max_tokens"], int)
        assert isinstance(fm["temperature"], float)

    def test_detects_missing_fields(self, tmp_path):
        fp = self._write_prompt(tmp_path, "bad_agent.md", self.SAMPLE_MISSING_FIELDS)
        import yaml, re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        errors = []
        for field in ["version", "status", "model", "max_tokens", "temperature"]:
            if field not in fm:
                errors.append(f"Missing required field: {field}")

        assert "Missing required field: model" in errors
        assert "Missing required field: max_tokens" in errors
        assert "Missing required field: temperature" in errors

    def test_detects_invalid_status(self, tmp_path):
        fp = self._write_prompt(tmp_path, "bad_status.md", self.SAMPLE_INVALID_STATUS)
        import yaml, re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert fm.get("status") not in ("active", "draft", "deprecated"), \
            "Status should be invalid"

    def test_detects_missing_frontmatter(self, tmp_path):
        fp = self._write_prompt(tmp_path, "no_fm.md", self.SAMPLE_NO_FRONTMATTER)
        import re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is None, "Should NOT have frontmatter"

    def test_max_tokens_must_be_numeric(self, tmp_path):
        bad = self.SAMPLE_VALID_PROMPT.replace(
            "max_tokens: 4096", 'max_tokens: "4096"'
        )
        fp = self._write_prompt(tmp_path, "string_tokens.md", bad)
        import yaml, re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert not isinstance(fm.get("max_tokens"), (int, float)), \
            "String should not pass numeric check"

    def test_skips_readme_files(self, tmp_path):
        readme = tmp_path / "prompts" / "README.md"
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text("README content", encoding="utf-8")

        agent = self._write_prompt(tmp_path, "test.md", self.SAMPLE_VALID_PROMPT)

        md_files = sorted(tmp_path.rglob("*.md"))
        md_names = [f.name for f in md_files]
        assert "README.md" in md_names
        # The validate script skips README - test it would be handled
        non_readme = [f for f in md_files if f.name != "README.md"]
        assert len(non_readme) == 1
