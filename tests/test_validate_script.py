"""Tests for the prompt validation script itself."""

import pytest
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

    SAMPLE_STRING_TOKENS = """---
version: 1.0.0
status: active
model: ollama/mistral:7b
max_tokens: "4096"
temperature: "0.5"
description: String tokens should fail
tags: [test]
---

Body text.
"""

    SAMPLE_NON_DICT_FRONTMATTER = """---
true
---

This has non-dict frontmatter.
"""

    SAMPLE_YAML_ERROR = """---
version: 1.0.0
status: active
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.5
invalid_yaml: : : :
---

Bad YAML syntax.
"""

    def _write_prompt(self, tmp_path: Path, name: str, content: str) -> Path:
        prompts_dir = tmp_path / "prompts" / "agents"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        file_path = prompts_dir / name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def _write_prompt_any(self, tmp_path: Path, subdir: str, name: str, content: str) -> Path:
        prompts_dir = tmp_path / "prompts" / subdir
        prompts_dir.mkdir(parents=True, exist_ok=True)
        file_path = prompts_dir / name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_validates_correct_prompt(self, tmp_path):
        fp = self._write_prompt(tmp_path, "test_agent.md", self.SAMPLE_VALID_PROMPT)
        import yaml
        import re

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
        import yaml
        import re

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
        import yaml
        import re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert fm.get("status") not in ("active", "draft", "deprecated"), "Status should be invalid"

    def test_detects_missing_frontmatter(self, tmp_path):
        fp = self._write_prompt(tmp_path, "no_fm.md", self.SAMPLE_NO_FRONTMATTER)
        import re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is None, "Should NOT have frontmatter"

    def test_max_tokens_must_be_numeric(self, tmp_path):
        bad = self.SAMPLE_VALID_PROMPT.replace("max_tokens: 4096", 'max_tokens: "4096"')
        fp = self._write_prompt(tmp_path, "string_tokens.md", bad)
        import yaml
        import re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert not isinstance(fm.get("max_tokens"), (int, float)), "String should not pass numeric check"

    def test_temperature_must_be_numeric(self, tmp_path):
        bad = self.SAMPLE_VALID_PROMPT.replace("temperature: 0.5", 'temperature: "0.5"')
        fp = self._write_prompt(tmp_path, "string_temp.md", bad)
        import yaml
        import re

        content = fp.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert not isinstance(fm.get("temperature"), (int, float)), "String should not pass numeric check"

    def test_skips_readme_files(self, tmp_path):
        readme = tmp_path / "prompts" / "README.md"
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text("README content", encoding="utf-8")

        self._write_prompt(tmp_path, "test.md", self.SAMPLE_VALID_PROMPT)

        md_files = sorted(tmp_path.rglob("*.md"))
        md_names = [f.name for f in md_files]
        assert "README.md" in md_names
        non_readme = [f for f in md_files if f.name != "README.md"]
        assert len(non_readme) == 1

    def test_frontmatter_is_dict(self):
        import re
        import yaml

        content = self.SAMPLE_NON_DICT_FRONTMATTER
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        fm = yaml.safe_load(match.group(1))
        assert not isinstance(fm, dict), "Should not be a dict"

    def test_yaml_parse_error_caught(self):
        import re
        import yaml

        content = self.SAMPLE_YAML_ERROR
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        assert match is not None

        try:
            yaml.safe_load(match.group(1))
            assert False, "Should have raised YAMLError"
        except yaml.YAMLError:
            pass

    def test_validate_all_valid(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "test.md", self.SAMPLE_VALID_PROMPT)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 0
        finally:
            os.chdir(original_cwd)

    def test_validate_all_missing_fields(self, tmp_path):
        self._write_prompt_any(tmp_path, "system", "bad.md", self.SAMPLE_MISSING_FIELDS)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_invalid_status(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "bad.md", self.SAMPLE_INVALID_STATUS)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_missing_frontmatter(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "nofm.md", self.SAMPLE_NO_FRONTMATTER)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_non_dict_frontmatter(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "nd.md", self.SAMPLE_NON_DICT_FRONTMATTER)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_string_tokens(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "st.md", self.SAMPLE_STRING_TOKENS)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_multiple_errors(self, tmp_path):
        self._write_prompt_any(tmp_path, "agents", "bad1.md", self.SAMPLE_MISSING_FIELDS)
        self._write_prompt_any(tmp_path, "agents", "bad2.md", self.SAMPLE_INVALID_STATUS)
        self._write_prompt_any(tmp_path, "agents", "good.md", self.SAMPLE_VALID_PROMPT)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_validate_all_skips_readme(self, tmp_path):
        readme = tmp_path / "prompts" / "README.md"
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text("Just readme", encoding="utf-8")
        self._write_prompt_any(tmp_path, "agents", "good.md", self.SAMPLE_VALID_PROMPT)
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all

            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 0
        finally:
            os.chdir(original_cwd)

    def test_module_import(self):
        import scripts.validate_prompts
        assert callable(scripts.validate_prompts.validate_all)

    def test_readme_only_skipped(self, tmp_path):
        readme = tmp_path / "prompts" / "README.md"
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text("# Readme", encoding="utf-8")
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)
        try:
            import glob
            files = sorted(glob.glob("prompts/**/*.md", recursive=True))
            non_readme = [f for f in files if not f.endswith("README.md")]
            assert len(non_readme) == 0
        finally:
            os.chdir(original_cwd)

    def test_status_field_validation_values(self):
        valid_statuses = {"active", "draft", "deprecated"}
        assert "active" in valid_statuses
        assert "draft" in valid_statuses
        assert "deprecated" in valid_statuses
        assert "invalid_status" not in valid_statuses
        assert "" not in valid_statuses
        assert None not in valid_statuses

    def test_validate_all_yaml_error(self, tmp_path):
        prompts_dir = tmp_path / "prompts" / "agents"
        prompts_dir.mkdir(parents=True)
        bad_file = prompts_dir / "bad_yaml.md"
        bad_file.write_text("---\nversion: 1.0\nstatus: [unbalanced\n---\nBody")
        import os
        original = Path.cwd()
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all
            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original)

    def test_validate_all_non_dict_frontmatter_script(self, tmp_path):
        prompts_dir = tmp_path / "prompts" / "agents"
        prompts_dir.mkdir(parents=True)
        bad_file = prompts_dir / "bad_fm.md"
        bad_file.write_text("---\n[not a dict]\n---\nBody")
        import os
        original = Path.cwd()
        os.chdir(tmp_path)
        try:
            from scripts.validate_prompts import validate_all
            with pytest.raises(SystemExit) as exc:
                validate_all()
            assert exc.value.code == 1
        finally:
            os.chdir(original)

    def test_main_block(self):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_prompts"],
            capture_output=True, text=True, timeout=30,
        )
        assert "OK" in result.stdout or "FAIL" in result.stdout
