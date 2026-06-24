"""Tests for /api/v1/predictions/ endpoints."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.api
class TestPredictionRoutes:
    """Test prediction endpoints for tasks, habits, sleep, and smart slots."""

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_task_completion_success(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.execute.return_value.data = [
                {
                    "id": "t1", "title": "Finish lab report", "status": "completed",
                    "priority": "high", "due_date": "2026-06-20T00:00:00Z",
                    "created_at": "2026-06-01T00:00:00Z", "updated_at": "2026-06-10T00:00:00Z",
                    "completed_at": "2026-06-10T00:00:00Z",
                },
                {
                    "id": "t2", "title": "Study for exam", "status": "pending",
                    "priority": "high", "due_date": "2026-06-25T00:00:00Z",
                    "created_at": "2026-06-05T00:00:00Z", "updated_at": "2026-06-05T00:00:00Z",
                },
                {
                    "id": "t3", "title": "Read chapter 5", "status": "pending",
                    "priority": "low", "due_date": "2026-07-01T00:00:00Z",
                    "created_at": "2026-06-01T00:00:00Z", "updated_at": "2026-06-01T00:00:00Z",
                },
            ]
        from app.api.predictions import predict_task_completion

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_task_completion(current_user=current_user)
        assert result.total_pending == 2
        assert result.high_completion >= 0
        assert len(result.predictions) == 2
        assert all(isinstance(p.probability, float) for p in result.predictions)

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_task_completion_empty(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.execute.return_value.data = []
        from app.api.predictions import predict_task_completion

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_task_completion(current_user=current_user)
        assert result.total_pending == 0
        assert result.high_completion == 0
        assert result.at_risk_count == 0
        assert result.predictions == []

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_task_completion_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.execute.side_effect = Exception("DB error")
        from app.api.predictions import predict_task_completion
        from fastapi import HTTPException

        current_user = MagicMock(user=MagicMock(id="test-user"))
        with pytest.raises(HTTPException) as exc:
            await predict_task_completion(current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_habits_success(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = [
                {
                    "id": "h1", "name": "Morning run", "frequency": "daily",
                    "is_active": True, "current_streak": 25, "best_streak": 30,
                    "consistency_percent": 85,
                },
                {
                    "id": "h2", "name": "Read 30 min", "frequency": "daily",
                    "is_active": True, "current_streak": 7, "best_streak": 14,
                    "consistency_percent": 50,
                },
                {
                    "id": "h3", "name": "Meditate", "frequency": "daily",
                    "is_active": True, "current_streak": 1, "best_streak": 5,
                    "consistency_percent": 20,
                },
            ]
        from app.api.predictions import predict_habits

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_habits(current_user=current_user)
        assert result.total_active == 3
        assert result.at_risk_count == 1
        assert len(result.predictions) == 3
        assert result.predictions[0].risk_level == "Low"
        assert result.predictions[2].risk_level == "High"

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_habits_inactive(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = [
                {
                    "id": "h1", "name": "Old habit", "frequency": "daily",
                    "is_active": False, "current_streak": 0, "best_streak": 5,
                    "consistency_percentage": 10,
                },
            ]
        from app.api.predictions import predict_habits

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_habits(current_user=current_user)
        assert result.total_active == 0
        assert result.at_risk_count == 0

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_habits_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.side_effect = Exception("DB error")
        from app.api.predictions import predict_habits
        from fastapi import HTTPException

        current_user = MagicMock(user=MagicMock(id="test-user"))
        with pytest.raises(HTTPException) as exc:
            await predict_habits(current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_sleep_success(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        logs = []
        for i in range(7):
            logs.append({
                "id": f"s{i}", "date": f"2026-06-{20+i:02d}",
                "bedtime": "22:30", "wake_time": "06:30",
                "duration_hours": 8.0, "sleep_score": 78 + i,
                "sleep_debt": 0.5, "quality_rating": 4,
            })
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.limit.return_value.execute.return_value.data = logs
        from app.api.predictions import predict_sleep

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_sleep(current_user=current_user)
        assert result.average_score > 0
        assert result.average_duration > 0
        assert result.trend == "stable"

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_sleep_empty(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.limit.return_value.execute.return_value.data = []
        from app.api.predictions import predict_sleep

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_sleep(current_user=current_user)
        assert result.average_score == 0
        assert result.average_duration == 0
        assert result.trend == "insufficient_data"
        assert result.bedtime_prediction is None

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_sleep_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .order.return_value.limit.return_value.execute.side_effect = Exception("DB error")
        from app.api.predictions import predict_sleep
        from fastapi import HTTPException

        current_user = MagicMock(user=MagicMock(id="test-user"))
        with pytest.raises(HTTPException) as exc:
            await predict_sleep(current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_smart_slots_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.side_effect = Exception("DB error")
        from app.api.predictions import predict_smart_slots
        from fastapi import HTTPException

        current_user = MagicMock(user=MagicMock(id="test-user"))
        with pytest.raises(HTTPException) as exc:
            await predict_smart_slots(current_user=current_user)
        assert exc.value.status_code == 500

    @patch("app.api.predictions.get_supabase_client")
    @pytest.mark.asyncio
    async def test_predict_smart_slots(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value \
            .execute.return_value.data = [
                {"start_time": "2026-06-22T09:00:00Z", "duration_minutes": 120,
                 "id": "e1"},
                {"start_time": "2026-06-22T10:00:00Z", "duration_minutes": 60,
                 "id": "e2"},
                {"start_time": "2026-06-23T14:00:00Z", "duration_minutes": 90,
                 "id": "e3"},
                {"status": "completed", "id": "t1"},
                {"status": "pending", "id": "t2"},
            ]
        from app.api.predictions import predict_smart_slots

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await predict_smart_slots(current_user=current_user)
        assert len(result.slots) > 0
        assert result.best_hour >= 0
        assert result.best_day >= 0
        first = result.slots[0]
        assert isinstance(first.productivity_score, float)
        assert isinstance(first.completion_rate, float)
