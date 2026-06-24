"""Tests for /api/v1/prompts/ endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


@pytest.mark.api
class TestPromptRoutes:
    """Test prompt listing, detail, rendering, and history endpoints."""

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_list_prompts_success(self, mock_prompts):
        mock_prompts.list_prompts.return_value = ["briefing_agent", "memory_agent"]
        mock_entry_b = MagicMock()
        mock_entry_b.name = "briefing_agent"
        mock_entry_b.category = "agents"
        mock_entry_b.file_path = MagicMock()
        mock_entry_b.frontmatter = {"version": "2.0.0"}
        mock_entry_b.body = "You are a briefing agent.\n\nGenerate report."
        mock_entry_m = MagicMock()
        mock_entry_m.name = "memory_agent"
        mock_entry_m.category = "agents"
        mock_entry_m.file_path = MagicMock()
        mock_entry_m.frontmatter = {"version": "1.5.0"}
        mock_entry_m.body = "You are a memory agent.\n\nConsolidate."
        mock_prompts.get.side_effect = lambda n: {
            "briefing_agent": mock_entry_b, "memory_agent": mock_entry_m,
        }.get(n)
        from app.api.prompts import list_prompts

        current_user = MagicMock()
        result = await list_prompts(current_user=current_user)
        assert result.total == 2
        assert len(result.prompts) == 2
        assert result.prompts[0].name == "briefing_agent"
        assert result.prompts[1].name == "memory_agent"

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_list_prompts_empty(self, mock_prompts):
        mock_prompts.list_prompts.return_value = []
        from app.api.prompts import list_prompts

        current_user = MagicMock()
        result = await list_prompts(current_user=current_user)
        assert result.total == 0

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_list_prompts_error(self, mock_prompts):
        mock_prompts.list_prompts.side_effect = Exception("Loader error")
        from app.api.prompts import list_prompts
        from fastapi import HTTPException

        current_user = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await list_prompts(current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_list_prompts_skips_none_entries(self, mock_prompts):
        mock_prompts.list_prompts.return_value = ["briefing_agent", "nonexistent"]
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = MagicMock()
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent.\n\nGenerate report."
        mock_prompts.get.side_effect = lambda n: mock_entry if n == "briefing_agent" else None
        from app.api.prompts import list_prompts

        current_user = MagicMock()
        result = await list_prompts(current_user=current_user)
        assert result.total == 1
        assert result.prompts[0].name == "briefing_agent"

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_success(self, mock_prompts):
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = MagicMock()
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent.\n\nGenerate report."
        mock_prompts.get.return_value = mock_entry
        from app.api.prompts import get_prompt

        current_user = MagicMock()
        result = await get_prompt(name="briefing_agent", current_user=current_user)
        assert result.name == "briefing_agent"
        assert result.body_length > 0

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_not_found(self, mock_prompts):
        mock_prompts.get.return_value = None
        from app.api.prompts import get_prompt
        from fastapi import HTTPException

        current_user = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await get_prompt(name="nonexistent", current_user=current_user)
        assert exc.value.status_code == 404

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_render_prompt_success(self, mock_prompts):
        mock_entry = MagicMock()
        mock_entry.name = "context_assembly"
        mock_entry.category = "templates"
        mock_entry.file_path = MagicMock()
        mock_entry.frontmatter = {"version": "1.0.0"}
        mock_entry.body = "Hello {name}, today is {day}."
        mock_entry.render.return_value = "Hello Alice, today is Monday."
        mock_prompts.get.return_value = mock_entry
        from app.api.prompts import render_prompt
        from database.schemas.prompt_schema import PromptRenderRequest

        current_user = MagicMock()
        req = PromptRenderRequest(variables={"name": "Alice", "day": "Monday"})
        result = await render_prompt(
            name="context_assembly", req=req, current_user=current_user,
        )
        assert result.name == "context_assembly"
        assert "Alice" in result.rendered

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_render_prompt_not_found(self, mock_prompts):
        mock_prompts.get.return_value = None
        from app.api.prompts import render_prompt
        from database.schemas.prompt_schema import PromptRenderRequest
        from fastapi import HTTPException

        current_user = MagicMock()
        req = PromptRenderRequest(variables={"name": "Alice"})
        with pytest.raises(HTTPException) as exc:
            await render_prompt(
                name="nonexistent", req=req, current_user=current_user,
            )
        assert exc.value.status_code == 404

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_render_prompt_key_error(self, mock_prompts):
        mock_entry = MagicMock()
        mock_entry.render.side_effect = KeyError("missing_var")
        mock_prompts.get.return_value = mock_entry
        from app.api.prompts import render_prompt
        from database.schemas.prompt_schema import PromptRenderRequest
        from fastapi import HTTPException

        current_user = MagicMock()
        req = PromptRenderRequest(variables={"bad": "data"})
        with pytest.raises(HTTPException) as exc:
            await render_prompt(name="test", req=req, current_user=current_user)
        assert exc.value.status_code == 422

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_render_prompt_generic_error(self, mock_prompts):
        mock_entry = MagicMock()
        mock_entry.render.side_effect = RuntimeError("boom")
        mock_prompts.get.return_value = mock_entry
        from app.api.prompts import render_prompt
        from database.schemas.prompt_schema import PromptRenderRequest
        from fastapi import HTTPException

        current_user = MagicMock()
        req = PromptRenderRequest(variables={"x": "y"})
        with pytest.raises(HTTPException) as exc:
            await render_prompt(name="test", req=req, current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.prompts.subprocess.run")
    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history(self, mock_prompts, mock_subprocess_run):
        project_root = Path(__file__).resolve().parent.parent
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = project_root / "prompts" / "agents" / "briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent."
        mock_prompts.get.return_value = mock_entry
        mock_subprocess_run.return_value.stdout = (
            "COMMIT\nabc123def456\n2026-01-01T12:00:00+00:00\n"
            "Developer\nUpdated briefing prompt\n"
            "5\t2\tprompts/agents/briefing_agent.md\n"
        )
        mock_subprocess_run.return_value.stderr = ""
        from app.api.prompts import get_prompt_history

        current_user = MagicMock()
        result = await get_prompt_history(name="briefing_agent", current_user=current_user)
        assert result.name == "briefing_agent"
        assert len(result.commits) == 1
        assert result.commits[0].hash == "abc123de"
        assert result.commits[0].author == "Developer"
        assert result.commits[0].additions == 5
        assert result.commits[0].deletions == 2

    @patch("app.api.prompts.subprocess.run")
    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history_empty_git_log(self, mock_prompts, mock_subprocess_run):
        project_root = Path(__file__).resolve().parent.parent
        mock_entry = MagicMock()
        mock_entry.name = "new_prompt"
        mock_entry.category = "agents"
        mock_entry.file_path = project_root / "prompts" / "agents" / "new_prompt.md"
        mock_entry.frontmatter = {"version": "1.0.0"}
        mock_entry.body = "New prompt."
        mock_prompts.get.return_value = mock_entry
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = ""
        from app.api.prompts import get_prompt_history

        current_user = MagicMock()
        result = await get_prompt_history(name="new_prompt", current_user=current_user)
        assert result.name == "new_prompt"
        assert len(result.commits) == 1
        assert result.commits[0].hash == "initial"

    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history_not_found(self, mock_prompts):
        mock_prompts.get.return_value = None
        from app.api.prompts import get_prompt_history
        from fastapi import HTTPException

        current_user = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await get_prompt_history(name="nonexistent", current_user=current_user)
        assert exc.value.status_code == 404

    @patch("app.api.prompts.subprocess.run")
    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history_git_timeout(self, mock_prompts, mock_subprocess_run):
        import subprocess
        project_root = Path(__file__).resolve().parent.parent
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = project_root / "prompts" / "agents" / "briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent."
        mock_prompts.get.return_value = mock_entry
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(
            cmd=["git", "log"], timeout=10,
        )
        from app.api.prompts import get_prompt_history
        from fastapi import HTTPException

        current_user = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await get_prompt_history(name="briefing_agent", current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.prompts.subprocess.run")
    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history_skips_malformed_commit_block(self, mock_prompts, mock_subprocess_run):
        project_root = Path(__file__).resolve().parent.parent
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = project_root / "prompts" / "agents" / "briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent."
        mock_prompts.get.return_value = mock_entry
        # A commit block with fewer than 4 header lines → line 88 continue
        mock_subprocess_run.return_value.stdout = "COMMIT\nabc123"
        mock_subprocess_run.return_value.stderr = ""
        from app.api.prompts import get_prompt_history

        current_user = MagicMock()
        result = await get_prompt_history(name="briefing_agent", current_user=current_user)
        assert len(result.commits) == 1
        assert result.commits[0].hash == "initial"

    @patch("app.api.prompts.subprocess.run")
    @patch("app.api.prompts.prompts")
    @pytest.mark.asyncio
    async def test_get_prompt_history_stat_parse_valueerror(self, mock_prompts, mock_subprocess_run):
        project_root = Path(__file__).resolve().parent.parent
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = project_root / "prompts" / "agents" / "briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.0.0"}
        mock_entry.body = "You are a briefing agent."
        mock_prompts.get.return_value = mock_entry
        # Stat line with non-numeric parts → ValueError on int(parts[0])
        mock_subprocess_run.return_value.stdout = (
            "COMMIT\nabc123def456\n2026-01-01T12:00:00+00:00\n"
            "Developer\nUpdated briefing prompt\n"
            "abc\tdef\tbriefing_agent.md\n0\t0\tother.md\n"
        )
        mock_subprocess_run.return_value.stderr = ""
        from app.api.prompts import get_prompt_history

        current_user = MagicMock()
        result = await get_prompt_history(name="briefing_agent", current_user=current_user)
        assert len(result.commits) == 1
        assert result.commits[0].additions == 0
        assert result.commits[0].deletions == 0
