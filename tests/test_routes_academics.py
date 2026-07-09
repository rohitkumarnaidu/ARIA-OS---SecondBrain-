"""Tests for /api/v1/academics/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.api
class TestAcademicsRoutes:
    """Test CRUD operations for academics."""

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_subjects_success(self, mock_supabase, mock_auth):
        """GET /subjects should return paginated list."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "name": "Math", "code": "MTH101", "semester": "1"}]
        )

        from app.api.academics import list_subjects

        result = await list_subjects(limit=50, offset=0, current_user=mock_user)
        assert len(result) == 1
        assert result[0]["name"] == "Math"

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_subjects_empty(self, mock_supabase, mock_auth):
        """GET /subjects should return empty list when no data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.academics import list_subjects

        result = await list_subjects(limit=50, offset=0, current_user=mock_user)
        assert result == []

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_subject_success(self, mock_supabase, mock_auth):
        """POST /subjects should create a subject."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "name": "Physics", "user_id": "test-user"}], error=None
        )

        from app.api.academics import create_subject
        from database.schemas.academic import SubjectCreate

        subject = SubjectCreate(name="Physics", code="PHY101", semester="1")
        result = await create_subject(subject, current_user=mock_user)
        assert result["name"] == "Physics"

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_subject_error(self, mock_supabase, mock_auth):
        """POST /subjects should raise on insert error."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            error=MagicMock(message="Insert failed")
        )

        from app.api.academics import create_subject
        from database.schemas.academic import SubjectCreate
        from fastapi import HTTPException

        subject = SubjectCreate(name="Physics", code="PHY101", semester="1")
        with pytest.raises(HTTPException) as exc:
            await create_subject(subject, current_user=mock_user)
        assert exc.value.status_code == 400

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_subject_success(self, mock_supabase, mock_auth):
        """DELETE /subjects/{id} should return None."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=None)
        )

        from app.api.academics import delete_subject

        result = await delete_subject("subj-1", current_user=mock_user)
        assert result is None

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_marks_success(self, mock_supabase, mock_auth):
        """GET /marks should return paginated list."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "subject_id": "subj-1", "exam_type": "Midterm", "marks_obtained": 85, "max_marks": 100}]
        )

        from app.api.academics import list_marks

        result = await list_marks(limit=50, offset=0, current_user=mock_user)
        assert len(result) == 1
        assert result[0]["marks_obtained"] == 85

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_mark_success(self, mock_supabase, mock_auth):
        """POST /marks should create a mark."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "subject_id": "subj-1", "marks_obtained": 90, "user_id": "test-user"}], error=None
        )

        from app.api.academics import create_mark
        from database.schemas.academic import MarkCreate

        mark = MarkCreate(
            subject_id="subj-1", exam_type="Midterm", marks_obtained=90.0, max_marks=100.0, date="2026-06-24"
        )
        result = await create_mark(mark, current_user=mock_user)
        assert result["marks_obtained"] == 90

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_mark_success(self, mock_supabase, mock_auth):
        """DELETE /marks/{id} should return None."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=None)
        )

        from app.api.academics import delete_mark

        result = await delete_mark("mark-1", current_user=mock_user)
        assert result is None

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_learning_stats_with_data(self, mock_supabase, mock_auth):
        """GET /learning-progress/stats should return computed stats."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "1",
                    "completion_rate": 80,
                    "courses_active": 3,
                    "habits_streak": 5,
                    "focus_minutes": 120,
                    "sleep_score": 7.5,
                },
                {
                    "id": "2",
                    "completion_rate": 70,
                    "courses_active": 3,
                    "habits_streak": 4,
                    "focus_minutes": 90,
                    "sleep_score": 6.5,
                },
            ]
        )

        from app.api.academics import learning_stats

        result = await learning_stats(current_user=mock_user)
        assert result["completion_rate"] == 80
        assert result["avg_completion_rate"] == 75.0
        assert result["trend"] in ("improving", "declining", "stable")

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_learning_stats_empty(self, mock_supabase, mock_auth):
        """GET /learning-progress/stats should return defaults when no data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.academics import learning_stats

        result = await learning_stats(current_user=mock_user)
        assert result["completion_rate"] == 0
        assert result["trend"] == "stable"
        assert result["snapshots"] == []

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_learning_timeline_success(self, mock_supabase, mock_auth):
        """GET /learning-progress/timeline should return snapshots."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "date": "2026-06-01", "completion_rate": 75}]
        )

        from app.api.academics import learning_timeline

        result = await learning_timeline(days=30, current_user=mock_user)
        assert len(result) == 1
        assert result[0]["completion_rate"] == 75

    @patch("app.api.academics.get_current_user")
    @patch("app.api.academics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_learning_timeline_exception(self, mock_supabase, mock_auth):
        """GET /learning-progress/timeline should return empty list on exception."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.gte.return_value.order.return_value.execute.side_effect = Exception(
            "DB down"
        )

        from app.api.academics import learning_timeline

        result = await learning_timeline(days=30, current_user=mock_user)
        assert result == []
