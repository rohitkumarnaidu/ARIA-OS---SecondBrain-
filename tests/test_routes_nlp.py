"""Tests for /api/v1/nlp/ endpoints (route functions only)."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_user():
    return MagicMock(user=MagicMock(id="test-user"))


@pytest.mark.api
class TestNLPRoutes:
    """Test NL route endpoints — helper functions are tested elsewhere."""

    @pytest.mark.asyncio
    async def test_parse_create_task_slash(self):
        """POST /parse should handle /new task slash command."""
        current_user = _mock_user()

        from app.api.nlp import parse_natural_language
        from database.schemas.nlp import NLPParseRequest

        result = await parse_natural_language(
            NLPParseRequest(text="/new task Finish ML project by tomorrow"),
            current_user=current_user,
        )
        assert result.type == "create_task"
        assert result.confidence >= 0.8
        assert result.task["title"] == "Finish ML project by tomorrow"

    @pytest.mark.asyncio
    async def test_parse_navigate_slash(self):
        """POST /parse should handle /go slash command."""
        current_user = _mock_user()

        from app.api.nlp import parse_natural_language
        from database.schemas.nlp import NLPParseRequest

        result = await parse_natural_language(
            NLPParseRequest(text="/go tasks"),
            current_user=current_user,
        )
        assert result.type == "navigate"
        assert result.confidence >= 0.9
        assert result.navigation == "/dashboard/tasks"

    @pytest.mark.asyncio
    async def test_parse_natural_language_create(self):
        """POST /parse should handle natural language task creation."""
        current_user = _mock_user()

        from app.api.nlp import parse_natural_language
        from database.schemas.nlp import NLPParseRequest

        result = await parse_natural_language(
            NLPParseRequest(text="create a task to review PR by Friday"),
            current_user=current_user,
        )
        assert result.type == "create_task"
        assert result.confidence >= 0.8

    @pytest.mark.asyncio
    async def test_parse_unknown_input(self):
        """POST /parse should return unknown type for unrecognized input."""
        current_user = _mock_user()

        from app.api.nlp import parse_natural_language
        from database.schemas.nlp import NLPParseRequest

        result = await parse_natural_language(
            NLPParseRequest(text="xyzzy plugh"),
            current_user=current_user,
        )
        assert result.type == "unknown"
        assert result.confidence < 0.5

    @patch("app.api.nlp.get_supabase_client")
    @pytest.mark.asyncio
    async def test_execute_create_task(self, mock_supabase):
        """POST /execute should create a task record."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()

        from app.api.nlp import execute_command

        result = await execute_command(
            {"type": "create_task", "task": {"title": "Test task", "priority": "high"}},
            current_user=current_user,
        )
        assert result["success"] is True
        assert "Test task" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_navigate(self):
        """POST /execute should handle navigation commands."""
        current_user = _mock_user()

        from app.api.nlp import execute_command

        result = await execute_command(
            {"type": "navigate", "navigation": "/dashboard/tasks"},
            current_user=current_user,
        )
        assert result["success"] is True
        assert result["redirect_url"] == "/dashboard/tasks"

    @pytest.mark.asyncio
    async def test_execute_unknown_type(self):
        """POST /execute should return failure for unknown command type."""
        current_user = _mock_user()

        from app.api.nlp import execute_command

        result = await execute_command(
            {"type": "unknown", "task": {}},
            current_user=current_user,
        )
        assert result["success"] is False
        assert "Unknown" in result["message"]

    @patch("app.api.nlp.get_supabase_client")
    @pytest.mark.asyncio
    async def test_execute_create_task_db_error(self, mock_supabase):
        """POST /execute should raise 500 on DB error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB down")

        from app.api.nlp import execute_command
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await execute_command(
                {"type": "create_task", "task": {"title": "Fail task"}},
                current_user=current_user,
            )
        assert exc.value.status_code == 500
