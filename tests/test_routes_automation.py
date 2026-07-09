"""Tests for /api/v1/automation/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.api
class TestAutomationRoutes:
    """Test automation trigger endpoints."""

    def _make_request(self):
        req = MagicMock()
        req.client.host = "127.0.0.1"
        return req

    def _make_user(self):
        return MagicMock(user=MagicMock(id="test-user"))

    @patch("app.api.automation.generate_daily_briefing")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_briefing_success(self, mock_limiter, mock_auth, mock_briefing):
        """POST /trigger/briefing should generate briefing."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_briefing.return_value = {"title": "Morning Briefing", "summary": "Your day ahead"}

        from app.api.automation import trigger_briefing

        result = await trigger_briefing(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["title"] == "Morning Briefing"

    @patch("app.api.automation.generate_daily_briefing")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_briefing_rate_limited(self, mock_limiter, mock_auth, mock_briefing):
        """POST /trigger/briefing should 429 when rate limited."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = False

        from app.api.automation import trigger_briefing
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await trigger_briefing(self._make_request(), current_user=mock_user)
        assert exc.value.status_code == 429

    @patch("app.api.automation.generate_daily_briefing")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_briefing_error(self, mock_limiter, mock_auth, mock_briefing):
        """POST /trigger/briefing should 500 on agent failure."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_briefing.side_effect = Exception("Agent crashed")

        from app.api.automation import trigger_briefing
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await trigger_briefing(self._make_request(), current_user=mock_user)
        assert exc.value.status_code == 500

    @patch("app.api.automation.run_opportunity_radar")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_radar_success(self, mock_limiter, mock_auth, mock_radar):
        """POST /trigger/radar should return opportunity count."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_radar.return_value = [{"id": "1"}, {"id": "2"}]

        from app.api.automation import trigger_radar

        result = await trigger_radar(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["count"] == 2

    @patch("app.api.automation.generate_weekly_review")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_weekly_review_success(self, mock_limiter, mock_auth, mock_review):
        """POST /trigger/weekly-review should generate review."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_review.return_value = {"week_summary": "Great week"}

        from app.api.automation import trigger_weekly_review

        result = await trigger_weekly_review(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["week_summary"] == "Great week"

    @patch("app.api.automation.analyze_sleep")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_sleep_analysis_success(self, mock_limiter, mock_auth, mock_sleep):
        """POST /trigger/sleep-analysis should analyze sleep."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_sleep.return_value = {"score": 7.5, "recommendation": "Sleep earlier"}

        from app.api.automation import trigger_sleep_analysis

        result = await trigger_sleep_analysis(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["score"] == 7.5

    @patch("app.api.automation.suggest_bedtime")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_sleep_bedtime_success(self, mock_limiter, mock_auth, mock_bedtime):
        """POST /trigger/sleep-bedtime should suggest bedtime."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_bedtime.return_value = {"bedtime": "23:00", "wind_down": "22:30"}

        from app.api.automation import trigger_sleep_bedtime

        result = await trigger_sleep_bedtime(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["bedtime"] == "23:00"

    @patch("app.api.automation.run_all_nudges")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_nudges_success(self, mock_limiter, mock_auth, mock_nudges):
        """POST /trigger/nudges should run nudges."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_nudges.return_value = [{"type": "course", "message": "Study math"}]

        from app.api.automation import trigger_nudges

        result = await trigger_nudges(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert len(result["data"]) == 1

    @patch("app.api.automation.orchestrate_plan")
    @patch("app.api.automation.get_current_user")
    @pytest.mark.asyncio
    async def test_create_plan_success(self, mock_auth, mock_plan):
        """POST /plan should create plan."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_plan.return_value = {"plan_id": "plan-1", "steps": [], "summary": "Plan summary"}

        from app.api.automation import create_plan
        from database.schemas.orchestrator import PlanRequest

        req = PlanRequest(query="Plan my day", context={})
        result = await create_plan(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["plan_id"] == "plan-1"

    @patch("app.api.automation.orchestrate_plan")
    @patch("app.api.automation.get_current_user")
    @pytest.mark.asyncio
    async def test_create_plan_fallback(self, mock_auth, mock_plan):
        """POST /plan should return fallback plan on error."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_plan.side_effect = Exception("Planner failed")

        from app.api.automation import create_plan
        from database.schemas.orchestrator import PlanRequest

        req = PlanRequest(query="Plan my day", context={})
        result = await create_plan(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["plan_id"] == "fallback"

    @patch("app.api.automation.orchestrate_execute")
    @patch("app.api.automation.get_current_user")
    @pytest.mark.asyncio
    async def test_create_execution_success(self, mock_auth, mock_exec):
        """POST /execute should execute action."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_exec.return_value = {"action": "search", "result": {}, "summary": "Searched tasks"}

        from app.api.automation import create_execution
        from database.schemas.orchestrator import PlanRequest

        req = PlanRequest(query="Find my tasks", context={})
        result = await create_execution(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["action"] == "search"

    @patch("app.api.automation.orchestrate_execute")
    @patch("app.api.automation.get_current_user")
    @pytest.mark.asyncio
    async def test_create_execution_fallback(self, mock_auth, mock_exec):
        """POST /execute should return noop fallback on error."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_exec.side_effect = Exception("Executor failed")

        from app.api.automation import create_execution
        from database.schemas.orchestrator import PlanRequest

        req = PlanRequest(query="Find my tasks", context={})
        result = await create_execution(req, current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["action"] == "noop"

    @patch("app.api.automation.run_data_retention_cleanup")
    @patch("app.api.automation.get_current_user")
    @patch("app.api.automation.endpoint_limiter")
    @pytest.mark.asyncio
    async def test_trigger_data_cleanup_success(self, mock_limiter, mock_auth, mock_cleanup):
        """POST /trigger/cleanup should run retention cleanup."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_limiter.check.return_value = True
        mock_cleanup.return_value = {"audit_deleted": 10, "chat_deleted": 5}

        from app.api.automation import trigger_data_cleanup

        result = await trigger_data_cleanup(self._make_request(), current_user=mock_user)
        assert result["status"] == "success"
        assert result["data"]["audit_deleted"] == 10
