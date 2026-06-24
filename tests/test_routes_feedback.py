"""Tests for /api/v1/feedback/ endpoints."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.api
class TestFeedbackRoutes:
    """Test feedback submission and summary endpoints."""

    @patch("app.api.feedback.uuid4")
    @patch("app.api.feedback.get_supabase_client")
    @pytest.mark.asyncio
    async def test_submit_feedback_success(self, mock_supabase_cli, mock_uuid):
        mock_uuid.return_value = "fb-uuid"
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value.data = [
            {"id": "fb-uuid", "source": "tasks", "rating": 5}
        ]
        from app.api.feedback import submit_feedback
        from database.schemas.feedback import FeedbackCreate

        fb = FeedbackCreate(source="tasks", target_id="task-1", rating=5)
        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await submit_feedback(fb=fb, current_user=current_user)
        assert result["id"] == "fb-uuid"
        mock_client.from_.assert_called_once_with("feedback")

    @patch("app.api.feedback.uuid4")
    @patch("app.api.feedback.get_supabase_client")
    @pytest.mark.asyncio
    async def test_submit_feedback_insert_error(self, mock_supabase_cli, mock_uuid):
        mock_uuid.return_value = "fb-uuid"
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.side_effect = \
            Exception("DB error")
        from app.api.feedback import submit_feedback
        from database.schemas.feedback import FeedbackCreate
        from fastapi import HTTPException

        fb = FeedbackCreate(source="tasks", target_id="task-1", rating=3)
        current_user = MagicMock(user=MagicMock(id="test-user"))
        with pytest.raises(HTTPException) as exc:
            await submit_feedback(fb=fb, current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.feedback.get_supabase_client")
    @pytest.mark.asyncio
    async def test_feedback_summary_with_data(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = [
                {"id": "1", "rating": 5, "source": "tasks"},
                {"id": "2", "rating": 4, "source": "tasks"},
                {"id": "3", "rating": 1, "source": "habits"},
                {"id": "4", "rating": 3, "source": "goals"},
            ]
        from app.api.feedback import feedback_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await feedback_summary(current_user=current_user)
        assert result.total == 4
        assert result.positive == 2
        assert result.negative == 1
        assert result.positive_rate == 50.0
        assert result.by_source == {"tasks": 2, "habits": 1, "goals": 1}

    @patch("app.api.feedback.get_supabase_client")
    @pytest.mark.asyncio
    async def test_feedback_summary_empty(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = []
        from app.api.feedback import feedback_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await feedback_summary(current_user=current_user)
        assert result.total == 0
        assert result.positive == 0
        assert result.negative == 0
        assert result.positive_rate == 0.0

    @patch("app.api.feedback.get_supabase_client")
    @pytest.mark.asyncio
    async def test_feedback_summary_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.side_effect = Exception("DB error")
        from app.api.feedback import feedback_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await feedback_summary(current_user=current_user)
        assert result.total == 0
        assert result.positive == 0
        assert result.negative == 0
