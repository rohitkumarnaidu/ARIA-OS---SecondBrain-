"""Tests for /api/v1/analytics/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.api
class TestAnalyticsRoutes:
    """Test analytics endpoints."""

    @patch("app.api.analytics.get_current_user")
    @patch("app.api.analytics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_daily_summary_success(self, mock_supabase, mock_auth):
        """GET /daily should return aggregated daily data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            if table == "tasks":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"count": 5}])
                )
            elif table == "habit_logs":
                m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"count": 3}]
                )
            elif table == "sleep_logs":
                m.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = (
                    MagicMock(data=[{"sleep_score": 7.5, "duration_hours": 8}])
                )
            elif table == "time_entries":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"duration_minutes": 120, "is_deep_work": True}])
                )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.analytics import get_daily_summary

        result = await get_daily_summary(date="2026-06-24", current_user=mock_user)
        assert result["date"] == "2026-06-24"
        assert result["sleep_score"] == 7.5
        assert result["focus_minutes"] == 120

    @patch("app.api.analytics.get_current_user")
    @patch("app.api.analytics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_daily_summary_no_sleep(self, mock_supabase, mock_auth):
        """GET /daily should return None sleep when no data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            if table == "sleep_logs":
                m.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = (
                    MagicMock(data=[])
                )
            else:
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[])
                )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.analytics import get_daily_summary

        result = await get_daily_summary(date="2026-06-24", current_user=mock_user)
        assert result["sleep_score"] is None

    @patch("app.api.analytics.get_current_user")
    @patch("app.api.analytics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_weekly_trends_success(self, mock_supabase, mock_auth):
        """GET /weekly should return weekly metrics."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            if table == "tasks":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"status": "completed"}, {"status": "pending"}])
                )
            elif table == "habit_logs":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"completed": True}, {"completed": False}])
                )
            elif table == "sleep_logs":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"sleep_score": 8.0}, {"sleep_score": 6.0}])
                )
            elif table == "time_entries":
                m.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    MagicMock(data=[{"duration_minutes": 60, "is_deep_work": True}])
                )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.analytics import get_weekly_trends

        result = await get_weekly_trends(week_start="2026-06-22", current_user=mock_user)
        assert result["task_completion_rate"] == 50.0
        assert result["habit_consistency"] == 50.0
        assert result["avg_sleep_score"] == 7.0
        assert result["total_focus_hours"] == 1.0

    @patch("app.api.analytics.get_current_user")
    @patch("app.api.analytics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_weekly_trends_empty(self, mock_supabase, mock_auth):
        """GET /weekly should return zeros when no data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            m.from_.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = MagicMock(
                data=[]
            )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.analytics import get_weekly_trends

        result = await get_weekly_trends(week_start="2026-06-22", current_user=mock_user)
        assert result["task_completion_rate"] == 0
        assert result["habit_consistency"] == 0
        assert result["avg_sleep_score"] == 0

    @patch("app.api.analytics.get_current_user")
    @patch("app.api.analytics.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_aggregated_stats_success(self, mock_supabase, mock_auth):
        """GET /stats should return aggregated statistics."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            if table == "tasks":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"status": "completed", "priority": "high"}, {"status": "pending", "priority": "medium"}]
                )
            elif table == "habits":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"is_active": True, "current_streak": 5, "best_streak": 10, "consistency_percentage": 80}]
                )
            elif table == "sleep_logs":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"duration_hours": 8, "sleep_score": 7.5, "sleep_debt": 1.0}]
                )
            elif table == "time_entries":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"duration_minutes": 120, "is_deep_work": True}]
                )
            elif table == "projects":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"status": "completed"}, {"status": "in_progress"}]
                )
            elif table == "ideas":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"status": "raw"}, {"status": "building"}]
                )
            elif table == "income_entries":
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"amount": 500, "effective_hourly_rate": 50.0}]
                )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.analytics import get_aggregated_stats

        result = await get_aggregated_stats(start_date="2026-06-01", end_date="2026-06-30", current_user=mock_user)
        assert result["tasks"]["completed"] == 1
        assert result["tasks"]["total"] == 2
        assert result["habits"]["total"] == 1
        assert result["sleep"]["avg_score"] == 7.5
        assert result["time"]["deep_work_minutes"] == 120
        assert result["income"]["total"] == 500

    @patch("app.api.analytics.detect_patterns")
    @patch("app.api.analytics.get_current_user")
    @pytest.mark.asyncio
    async def test_detect_patterns_success(self, mock_auth, mock_detect):
        """POST /patterns should return pattern data."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_detect.return_value = {
            "patterns": [{"name": "procrastination"}],
            "summary": "You tend to delay hard tasks",
        }

        from app.api.analytics import detect_patterns_endpoint
        from database.schemas.orchestrator import PatternRequest

        req = PatternRequest(query="Do I procrastinate?")
        result = await detect_patterns_endpoint(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["patterns"][0]["name"] == "procrastination"

    @patch("app.api.analytics.detect_patterns")
    @patch("app.api.analytics.get_current_user")
    @pytest.mark.asyncio
    async def test_detect_patterns_fallback(self, mock_auth, mock_detect):
        """POST /patterns should return fallback on exception."""
        mock_user = MagicMock(user=MagicMock(id="test-user"))
        mock_auth.return_value = mock_user
        mock_detect.side_effect = Exception("AI unavailable")

        from app.api.analytics import detect_patterns_endpoint
        from database.schemas.orchestrator import PatternRequest

        req = PatternRequest(query="Do I procrastinate?")
        result = await detect_patterns_endpoint(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["patterns"] == []
