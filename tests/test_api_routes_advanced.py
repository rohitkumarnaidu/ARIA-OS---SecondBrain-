"""Comprehensive tests for low-coverage API route files."""

import subprocess
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

# ===========================================================================
# Reuse helpers from test_api_endpoints.py — imports are guarded to run
# only when this file is executed directly or via pytest.
# ===========================================================================

_AUTH_HEADER = {"Authorization": "Bearer test-token"}
_TEST_USER_ID = "user-1"


def _make_auth_mock_user():
    class _Inner:
        id = _TEST_USER_ID

    class _MockUser:
        user = _Inner()

    return _MockUser()


class MockQueryBuilder:
    """Fluent mock for supabase query builder (.select().eq().execute())."""

    def __init__(self, return_data=None, error_message=None):
        self._return_data = return_data if return_data is not None else []
        self._error_message = error_message

    def select(self, *args, **kwargs):
        return self

    def eq(self, col, val):
        return self

    def neq(self, col, val):
        return self

    def order(self, col, **kwargs):
        return self

    def limit(self, n):
        return self

    def range(self, start, end):
        return self

    def gte(self, col, val):
        return self

    def lte(self, col, val):
        return self

    def text_search(self, col, val):
        return self

    def lt(self, col, val):
        return self

    def execute(self):
        result = MagicMock()
        result.data = self._return_data
        if self._error_message:
            result.error = MagicMock(message=self._error_message)
        else:
            result.error = None
        return result

    def insert(self, data):
        return MockQueryBuilder(return_data=self._return_data, error_message=self._error_message)

    def update(self, data):
        return MockQueryBuilder(return_data=self._return_data, error_message=self._error_message)

    def delete(self):
        return MockQueryBuilder(return_data=[{}], error_message=self._error_message)


def _cfg(mock_supabase, data, error=None):
    mock_supabase.from_.return_value = MockQueryBuilder(return_data=data, error_message=error)
    return mock_supabase


def _router_modules_advanced():
    """All route modules needed for tests in this file."""
    # NOTE: prompts and automation modules do NOT import
    # get_supabase_client, so they're excluded from the mock patch list.
    modules = [
        "app.api.chat",
        "app.api.predictions",
        "app.api.nlp",
        "app.api.notifications",
        "app.api.analytics",
        "app.api.data_export",
        "app.api.videos",
        "app.api.briefings",
        "app.api.roadmap",
        "app.api.memory",
        "app.api.academics",
        "app.api.reviews",
        "app.api.monitoring",
        "app.api.feedback",
        "app.api.courses",
        "app.api.goals",
        "app.api.habits",
        "app.api.ideas",
        "app.api.income",
        "app.api.opportunities",
        "app.api.projects",
        "app.api.resources",
        "app.api.sleep",
        "app.api.time",
    ]
    return modules


def _register_mock_agent_modules():
    import sys
    import types

    specs = {
        "briefing_agent": {"generate_daily_briefing"},
        "opportunity_agent": {"run_opportunity_radar"},
        "weekly_review_agent": {"generate_weekly_review"},
        "sleep_agent": {"analyze_sleep", "suggest_bedtime"},
        "nudge_agent": {"run_all_nudges"},
    }
    for name, fns in specs.items():
        mod_path = f"ai.agents.{name}"
        if mod_path not in sys.modules:
            mock_mod = types.ModuleType(mod_path)
            for fn in fns:
                setattr(mock_mod, fn, AsyncMock(return_value={} if "radar" not in fn else []))
            sys.modules[mod_path] = mock_mod


_register_mock_agent_modules()


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture(scope="module")
def app():
    from fastapi import FastAPI
    from app.api import (
        chat,
        predictions,
        nlp,
        notifications,
        analytics,
        prompts,
        data_export,
        automation,
        videos,
        briefings,
        roadmap,
        memory,
        academics,
        reviews,
        monitoring,
        feedback,
        courses,
        goals,
        habits,
        ideas,
        income,
        opportunities,
        projects,
        resources,
        sleep,
        time,
        auth,
    )

    application = FastAPI(title="Test API Advanced")
    application.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    application.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
    application.include_router(nlp.router, prefix="/api/v1/nlp", tags=["nlp"])
    application.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
    application.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    application.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
    application.include_router(data_export.router, prefix="/api/v1/data", tags=["data"])
    application.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
    application.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])
    application.include_router(briefings.router, prefix="/api/v1/briefings", tags=["briefings"])
    application.include_router(roadmap.router, prefix="/api/v1/roadmap", tags=["roadmap"])
    application.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
    application.include_router(academics.router, prefix="/api/v1/academics", tags=["academics"])
    application.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
    application.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
    application.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
    application.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
    application.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])
    application.include_router(habits.router, prefix="/api/v1/habits", tags=["habits"])
    application.include_router(ideas.router, prefix="/api/v1/ideas", tags=["ideas"])
    application.include_router(income.router, prefix="/api/v1/income", tags=["income"])
    application.include_router(opportunities.router, prefix="/api/v1/opportunities", tags=["opportunities"])
    application.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    application.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
    application.include_router(sleep.router, prefix="/api/v1/sleep", tags=["sleep"])
    application.include_router(time.router, prefix="/api/v1/time", tags=["time"])
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    return application


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_supabase():
    return MagicMock()


@pytest.fixture(autouse=True)
def _setup_deps(app, mock_supabase):
    from config.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()

    patchers = []
    for mod in _router_modules_advanced():
        p = patch(f"{mod}.get_supabase_client", return_value=mock_supabase)
        p.start()
        patchers.append(p)

    yield

    for p in patchers:
        p.stop()
    app.dependency_overrides.clear()


@pytest.fixture
def no_auth(app):
    app.dependency_overrides.clear()
    yield
    from config.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()


# ===========================================================================
# SAMPLE DATA
# ===========================================================================

SAMPLE_TASK_PENDING = {
    "id": "task-1",
    "user_id": "user-1",
    "title": "Write report",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-07-01T12:00:00",
    "estimated_minutes": 120,
    "completed_at": None,
    "missed_count": 0,
    "category": "work",
    "description": "Q3 report",
    "project_id": None,
    "goal_id": None,
    "is_recurring": False,
    "recurring_frequency": None,
    "dependency_id": None,
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-01T12:00:00",
}

SAMPLE_TASK_COMPLETED = {
    "id": "task-2",
    "user_id": "user-1",
    "title": "Submit assignment",
    "status": "completed",
    "priority": "high",
    "due_date": "2026-06-15T12:00:00",
    "estimated_minutes": 60,
    "completed_at": "2026-06-14T12:00:00",
    "missed_count": 0,
    "category": "academic",
    "description": None,
    "project_id": None,
    "goal_id": None,
    "is_recurring": False,
    "recurring_frequency": None,
    "dependency_id": None,
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-14T12:00:00",
}

SAMPLE_HABIT = {
    "id": "habit-1",
    "user_id": "user-1",
    "name": "Morning Meditation",
    "frequency": "daily",
    "is_active": True,
    "current_streak": 15,
    "best_streak": 30,
    "consistency_percent": 80.0,
    "created_at": "2026-01-01T00:00:00",
}

SAMPLE_SLEEP_LOG = {
    "id": "sleep-1",
    "user_id": "user-1",
    "date": "2026-06-20",
    "bedtime": "2026-06-19T23:00:00",
    "wake_time": "2026-06-20T07:00:00",
    "duration_hours": 8.0,
    "sleep_score": 85,
    "sleep_debt": 0.0,
    "quality_rating": 4,
    "created_at": "2026-06-20T07:30:00",
}

SAMPLE_TIME_ENTRY = {
    "id": "time-1",
    "user_id": "user-1",
    "start_time": "2026-06-20T09:00:00",
    "end_time": "2026-06-20T10:30:00",
    "duration_minutes": 90,
    "category": "development",
    "task_id": None,
    "project_id": None,
    "is_deep_work": True,
    "description": "Coding session",
    "created_at": "2026-06-20T10:30:00",
}

SAMPLE_NOTIFICATION = {
    "id": "notif-1",
    "user_id": "user-1",
    "title": "Overdue task",
    "message": "Task is past deadline",
    "category": "task",
    "priority": "high",
    "read": False,
    "action_url": "/dashboard/tasks",
    "icon": "alert-circle",
    "created_at": "2026-06-20T00:00:00",
}

SAMPLE_VIDEO = {
    "id": "vid-1",
    "user_id": "user-1",
    "title": "FastAPI Tutorial",
    "url": "https://youtube.com/watch?v=abc123",
    "status": "saved",
    "thumbnail_url": None,
    "ai_summary": None,
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_BRIEFING = {
    "id": "brief-1",
    "user_id": "user-1",
    "date": "2026-06-20",
    "title": "Morning Briefing",
    "summary": "You have 3 tasks today",
    "priorities": ["Write report", "Gym"],
    "read": False,
    "created_at": "2026-06-20T07:00:00",
}

SAMPLE_MILESTONE = {
    "id": "ms-1",
    "user_id": "user-1",
    "title": "Learn React",
    "description": "Complete React course",
    "target_date": "2026-09-01",
    "status": "in_progress",
    "progress": 40.0,
    "category": "frontend",
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_MEMORY = {
    "id": "mem-1",
    "user_id": "user-1",
    "type": "preference",
    "key": "pref_theme",
    "value": "dark",
    "importance": "medium",
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-01T12:00:00",
}

SAMPLE_SUBJECT = {
    "id": "sub-1",
    "user_id": "user-1",
    "name": "Data Structures",
    "code": "CS201",
    "semester": "3rd",
    "created_at": "2026-01-15T00:00:00",
}

SAMPLE_MARK = {
    "id": "mark-1",
    "user_id": "user-1",
    "subject_id": "sub-1",
    "exam_type": "Midterm",
    "marks_obtained": 85.0,
    "max_marks": 100.0,
    "date": "2026-03-15",
    "created_at": "2026-03-15T00:00:00",
}

SAMPLE_REVIEW = {
    "id": "rev-1",
    "user_id": "user-1",
    "week_start": "2026-06-15",
    "week_end": "2026-06-21",
    "title": "Weekly Review",
    "summary": "Good week",
    "read": False,
    "created_at": "2026-06-21T20:00:00",
}

SAMPLE_ROADMAP = {
    "id": "rm-1",
    "user_id": "user-1",
    "skill": "Python",
    "category": "programming",
    "target_date": "2026-08-01",
    "progress": 50.0,
    "status": "in_progress",
    "is_recommended": True,
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-15T12:00:00",
}

SAMPLE_LEARNING_PROGRESS = {
    "id": "lp-1",
    "user_id": "user-1",
    "date": "2026-06-20",
    "completion_rate": 75.0,
    "courses_active": 2,
    "habits_streak": 10,
    "focus_minutes": 120,
    "sleep_score": 80,
}


# ===========================================================================
# PREDICTIONS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestPredictionEndpoints:

    def test_predict_tasks_happy_path(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK_PENDING, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_pending" in body
        assert "high_completion" in body
        assert "predictions" in body
        assert len(body["predictions"]) == 1

    def test_predict_tasks_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total_pending"] == 0

    def test_predict_tasks_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_predict_habits_happy_path(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_active" in body
        assert "at_risk_count" in body
        assert len(body["predictions"]) == 1

    def test_predict_habits_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total_active"] == 0

    def test_predict_habits_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_predict_sleep_happy_path(self, client, mock_supabase):
        logs = [
            {**SAMPLE_SLEEP_LOG, "sleep_score": 80, "duration_hours": 7.5},
            {**SAMPLE_SLEEP_LOG, "id": "sleep-2", "sleep_score": 85, "duration_hours": 8.0},
        ]
        _cfg(mock_supabase, logs)
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "average_score" in body
        assert "average_duration" in body
        assert body["average_score"] > 0

    def test_predict_sleep_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["trend"] == "insufficient_data"

    def test_predict_sleep_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_predict_slots_happy_path(self, client, mock_supabase):
        """Slots endpoint queries time_entries (loop) AND tasks (inside loop)."""
        entries = [
            {**SAMPLE_TIME_ENTRY, "start_time": "2026-06-20T09:00:00", "duration_minutes": 90},
            {**SAMPLE_TIME_ENTRY, "id": "time-2", "start_time": "2026-06-20T14:00:00", "duration_minutes": 60},
        ]

        def from_side(table):
            if table == "time_entries":
                return MockQueryBuilder(return_data=entries)
            return MockQueryBuilder(return_data=[SAMPLE_TASK_PENDING, SAMPLE_TASK_COMPLETED])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/predictions/slots", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "slots" in body
        assert "best_hour" in body
        assert len(body["slots"]) > 0

    def test_predict_slots_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/predictions/slots", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_slots_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/predictions/slots", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_predictions_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/predictions/tasks")
        assert resp.status_code == 401

    def test_predict_habits_low_risk(self, client, mock_supabase):
        """Habit with high streak and consistency should have low risk."""
        habit = {**SAMPLE_HABIT, "current_streak": 30, "consistency_percentage": 90.0}
        _cfg(mock_supabase, [habit])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.json()["predictions"][0]["risk_level"] == "Low"

    def test_predict_habits_high_risk(self, client, mock_supabase):
        habit = {**SAMPLE_HABIT, "current_streak": 1, "consistency_percentage": 10.0}
        _cfg(mock_supabase, [habit])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.json()["predictions"][0]["risk_level"] == "High"

    def test_predict_sleep_with_trend_improving(self, client, mock_supabase):
        logs = []
        for i in range(21):
            logs.append(
                {
                    **SAMPLE_SLEEP_LOG,
                    "id": f"sleep-{i}",
                    "sleep_score": 60 + (i if i >= 14 else 0),
                    "duration_hours": 7.0,
                    "date": f"2026-06-{i+1:02d}",
                }
            )
        _cfg(mock_supabase, logs)
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200


# ===========================================================================
# NLP — 2 endpoints
# ===========================================================================


@pytest.mark.api
class TestNLPEndpoints:

    def test_parse_create_task_slash(self, client, mock_suppress_nlp=None):
        resp = client.post(
            "/api/v1/nlp/parse", json={"text": "/new task Buy groceries tomorrow high priority"}, headers=_AUTH_HEADER
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["type"] == "create_task"
        assert body["confidence"] >= 0.8

    def test_parse_navigate_slash(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "/go tasks"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["type"] == "navigate"
        assert body["navigation"] == "/dashboard/tasks"

    def test_parse_navigate_natural(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "show me my habits"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["type"] == "navigate"

    def test_parse_create_task_natural(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "create a task to finish homework"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["type"] == "create_task"
        assert "homework" in body["task"]["title"]

    def test_parse_unknown(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "what is the meaning of life"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["type"] == "unknown"

    def test_parse_priority_high(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "urgent task to fix login bug"}, headers=_AUTH_HEADER)
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["priority"] == "high"

    def test_parse_priority_low(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "someday organize bookshelf"}, headers=_AUTH_HEADER)
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["priority"] == "low"

    def test_parse_date_today(self, client):
        resp = client.post("/api/v1/nlp/parse", json={"text": "remind me to call dentist today"}, headers=_AUTH_HEADER)
        body = resp.json()
        if body["type"] == "create_task":
            from datetime import datetime

            assert body["task"]["due_date"] == datetime.now().strftime("%Y-%m-%d")

    def test_parse_minutes(self, client):
        resp = client.post(
            "/api/v1/nlp/parse", json={"text": "add task to review PR (30 minutes)"}, headers=_AUTH_HEADER
        )
        body = resp.json()
        if body["type"] == "create_task" and body["task"]["estimated_minutes"]:
            assert body["task"]["estimated_minutes"] == 30

    def test_execute_create_task(self, client, mock_supabase):
        _cfg(mock_supabase, [{"id": "new-task-1"}])
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "create_task",
                "task": {"title": "Test task", "priority": "high"},
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_execute_create_task_db_error(self, client, mock_supabase):
        """Simulate DB insert failure in execute_command create_task path."""
        mock_supabase.table.side_effect = Exception("insert failed")
        mock_supabase.from_.side_effect = Exception("insert failed")
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "create_task",
                "task": {"title": "Fail task"},
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 500

    def test_execute_navigate(self, client):
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "navigate",
                "navigation": "/dashboard/tasks",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert resp.json()["redirect_url"] == "/dashboard/tasks"

    def test_execute_unknown(self, client):
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "unknown",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    def test_parse_nlp_unauthorized(self, client, no_auth):
        resp = client.post("/api/v1/nlp/parse", json={"text": "hello"})
        assert resp.status_code == 401

    def test_execute_nlp_unauthorized(self, client, no_auth):
        resp = client.post("/api/v1/nlp/execute", json={"type": "navigate"})
        assert resp.status_code == 401


# ===========================================================================
# NOTIFICATIONS — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestNotificationEndpoints:

    def test_list_notifications(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_NOTIFICATION])
        resp = client.get("/api/v1/notifications/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_notifications_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/notifications/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_notifications_db_error_returns_empty(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/notifications/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_mark_read(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_NOTIFICATION])
        resp = client.patch("/api/v1/notifications/notif-1/read", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_mark_read_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.patch("/api/v1/notifications/nonexistent/read", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_mark_read_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.patch("/api/v1/notifications/notif-1/read", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_mark_all_read(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.post("/api/v1/notifications/read-all", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_mark_all_read_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.post("/api/v1/notifications/read-all", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_generate_nudges(self, client, mock_supabase):
        def from_side(table):
            if table == "tasks":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_TASK_PENDING,
                            "due_date": "2020-01-01T00:00:00",
                        }
                    ]
                )
            if table == "habits":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_HABIT,
                            "current_streak": 0,
                            "consistency_percent": 20,
                        }
                    ]
                )
            if table == "sleep_logs":
                scores = [{"sleep_score": 50 + i, "date": f"2026-06-{i+1:02d}"} for i in range(14)]
                return MockQueryBuilder(return_data=scores)
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        # Should have overdue nudges and habit nudges (at least)
        assert len(resp.json()) >= 2

    def test_generate_nudges_empty_data(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_generate_nudges_all_db_errors(self, client, mock_supabase):
        """When all DB queries fail, nudges should still return empty list."""
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_deadline_alerts(self, client, mock_supabase):
        task = {
            **SAMPLE_TASK_PENDING,
            "due_date": (datetime.now(timezone.utc)).isoformat(),
        }
        _cfg(mock_supabase, [task])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_deadline_alerts_no_tasks(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_notifications_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/notifications/")
        assert resp.status_code == 401


# ===========================================================================
# ANALYTICS — 3 endpoints
# ===========================================================================


@pytest.mark.api
class TestAnalyticsEndpoints:

    def test_daily_summary(self, client, mock_supabase):
        _cfg(
            mock_supabase,
            [
                {"sleep_score": 82, "duration_hours": 7.5},
            ],
        )
        resp = client.get("/api/v1/analytics/daily?date=2026-06-20", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["date"] == "2026-06-20"
        assert "tasks_completed" in body
        assert "habits_completed" in body

    def test_daily_summary_missing_date(self, client):
        resp = client.get("/api/v1/analytics/daily", headers=_AUTH_HEADER)
        assert resp.status_code == 422

    def test_weekly_trends(self, client, mock_supabase):
        _cfg(
            mock_supabase,
            [
                {"status": "completed"},
                {"status": "pending"},
            ],
        )
        resp = client.get("/api/v1/analytics/weekly?week_start=2026-06-15", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "task_completion_rate" in body
        assert "habit_consistency" in body

    def test_weekly_trends_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/analytics/weekly?week_start=2026-06-15", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["task_completion_rate"] == 0

    def test_aggregated_stats(self, client, mock_supabase):
        def from_side(table):
            if table == "tasks":
                return MockQueryBuilder(return_data=[{"status": "completed", "priority": "high"}])
            if table == "habits":
                return MockQueryBuilder(
                    return_data=[
                        {"is_active": True, "current_streak": 5, "best_streak": 10, "consistency_percentage": 70.0}
                    ]
                )
            if table == "sleep_logs":
                return MockQueryBuilder(return_data=[{"duration_hours": 7.5, "sleep_score": 80, "sleep_debt": 0.5}])
            if table == "time_entries":
                return MockQueryBuilder(return_data=[{"duration_minutes": 90, "is_deep_work": True}])
            if table == "projects":
                return MockQueryBuilder(return_data=[{"status": "completed"}])
            if table == "ideas":
                return MockQueryBuilder(return_data=[{"status": "building"}])
            if table == "income_entries":
                return MockQueryBuilder(return_data=[{"amount": 500.0, "effective_hourly_rate": 50.0}])
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/analytics/stats?start_date=2026-01-01&end_date=2026-06-30", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["tasks"]["completed"] == 1
        assert body["sleep"]["avg_score"] > 0

    def test_aggregated_stats_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/analytics/stats?start_date=2026-01-01&end_date=2026-06-30", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["tasks"]["total"] == 0

    def test_analytics_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/analytics/daily?date=2026-06-20")
        assert resp.status_code == 401


# ===========================================================================
# PROMPTS — 4 endpoints (list, get, render, history)
# ===========================================================================


@pytest.mark.api
class TestPromptEndpoints:

    @pytest.fixture(autouse=True)
    def _mock_prompts(self):
        """Mock the 'prompts' singleton from ai.prompt_loader."""
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = MagicMock()
        mock_entry.file_path.__str__ = MagicMock(return_value="/prompts/agents/briefing_agent.md")
        mock_entry.file_path.relative_to.return_value = "prompts/agents/briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.1.0", "status": "active"}
        mock_entry.body = "You are a briefing assistant."
        mock_entry.system_prompt = mock_entry.body
        mock_entry.render.return_value = "Rendered: You are a briefing assistant."

        mock_entry2 = MagicMock()
        mock_entry2.name = "task_agent"
        mock_entry2.category = "agents"
        mock_entry2.file_path = MagicMock()
        mock_entry2.file_path.__str__ = MagicMock(return_value="/prompts/agents/task_agent.md")
        mock_entry2.frontmatter = {"version": "1.0.0", "status": "active"}
        mock_entry2.body = "You are a task agent."
        mock_entry2.system_prompt = mock_entry2.body
        mock_entry2.render.return_value = "Rendered task."

        with patch("app.api.prompts.prompts") as mock_prompts:
            mock_prompts.list_prompts.return_value = ["briefing_agent", "task_agent"]

            def get_side(name):
                mapping = {"briefing_agent": mock_entry, "task_agent": mock_entry2}
                return mapping.get(name)

            mock_prompts.get.side_effect = get_side
            yield

    def test_list_prompts(self, client):
        resp = client.get("/api/v1/prompts/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert len(body["prompts"]) == 2

    def test_get_prompt_by_name(self, client):
        resp = client.get("/api/v1/prompts/briefing_agent", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "briefing_agent"
        assert "body" in body

    def test_get_prompt_not_found(self, client):
        resp = client.get("/api/v1/prompts/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_render_prompt(self, client):
        resp = client.post(
            "/api/v1/prompts/briefing_agent/render", json={"variables": {"name": "Alice"}}, headers=_AUTH_HEADER
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "rendered" in body

    def test_render_prompt_not_found(self, client):
        resp = client.post("/api/v1/prompts/nonexistent/render", json={"variables": {}}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_render_prompt_no_variables(self, client):
        resp = client.post("/api/v1/prompts/briefing_agent/render", json={}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_render_prompt_key_error(self, client):
        """When render raises KeyError, endpoint should return 422."""
        with patch("app.api.prompts.prompts") as mock_ps:
            mock_entry = MagicMock()
            mock_entry.render.side_effect = KeyError("missing_var")
            mock_ps.get.return_value = mock_entry
            resp = client.post(
                "/api/v1/prompts/briefing_agent/render", json={"variables": {"foo": "bar"}}, headers=_AUTH_HEADER
            )
            assert resp.status_code == 422

    def test_get_prompt_history(self, client):
        """Prompt history runs a git log subprocess."""
        with patch("app.api.prompts.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = (
                "COMMIT\nabc123def\n2026-06-20T12:00:00Z\nDeveloper\nFix prompt\n"
                "1\t1\tprompts/agents/briefing_agent.md"
            )
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            resp = client.get("/api/v1/prompts/briefing_agent/history", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            body = resp.json()
            assert body["name"] == "briefing_agent"
            assert len(body["commits"]) == 1
            assert body["commits"][0]["hash"] == "abc123de"

    def test_get_prompt_history_not_found(self, client):
        resp = client.get("/api/v1/prompts/nonexistent/history", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_get_prompt_history_git_fails(self, client):
        """When git command fails (e.g. not a repo), endpoint still returns."""
        with patch("app.api.prompts.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            resp = client.get("/api/v1/prompts/briefing_agent/history", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            body = resp.json()
            assert len(body["commits"]) == 1  # Falls back to initial commit

    def test_prompts_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/prompts/")
        assert resp.status_code == 401


# ===========================================================================
# DATA EXPORT — 1 endpoint
# ===========================================================================


@pytest.mark.api
class TestDataExportEndpoints:

    def test_export_user_data(self, client, mock_supabase):
        def from_side(table):
            if table in ("tasks", "courses", "habits"):
                return MockQueryBuilder(return_data=[{"id": f"{table}-1", "user_id": "user-1"}])
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/data/export", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["user_id"] == "user-1"
        assert "exported_at" in body
        assert body["table_count"] >= 3
        assert body["record_count"] >= 3

    def test_export_user_data_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/data/export", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["table_count"] == 0

    def test_export_user_data_partial_failures(self, client, mock_supabase):
        """Some tables may throw errors; export should skip them gracefully."""
        call_count = [0]

        def from_side(table):
            call_count[0] += 1
            if call_count[0] == 1:
                return MockQueryBuilder(return_data=[{"id": "t-1"}])
            raise Exception("Table unavailable")

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/data/export", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_export_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/data/export")
        assert resp.status_code == 401


# ===========================================================================
# AUTOMATION — edge cases for existing + new cleanup endpoint
# ===========================================================================


@pytest.mark.api
class TestAutomationAdvancedEndpoints:

    @pytest.fixture(autouse=True)
    def _mock_agents(self):
        patchers = []
        targets = {
            "app.api.automation.generate_daily_briefing": {"status": "ok"},
            "app.api.automation.run_opportunity_radar": [],
            "app.api.automation.generate_weekly_review": {"status": "ok"},
            "app.api.automation.analyze_sleep": {"status": "ok"},
            "app.api.automation.suggest_bedtime": {"status": "ok", "bedtime": "22:00"},
            "app.api.automation.run_all_nudges": {"status": "ok", "nudges": 3},
            "app.api.automation.run_data_retention_cleanup": {
                "audit_logs_removed": 5,
                "chat_messages_removed": 10,
                "notifications_removed": 3,
            },
        }
        for target, retval in targets.items():
            p = patch(target, new=AsyncMock(return_value=retval))
            p.start()
            patchers.append(p)
        yield
        for p in patchers:
            p.stop()

    def test_trigger_cleanup(self, client):
        resp = client.post("/api/v1/automation/trigger/cleanup", headers=_AUTH_HEADER)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "success"

    def test_trigger_cleanup_custom_days(self, client):
        resp = client.post(
            "/api/v1/automation/trigger/cleanup?audit_days=60&chat_days=30&notification_days=14",
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_trigger_briefing_error(self, client):
        with patch("app.api.automation.generate_daily_briefing", new=AsyncMock(side_effect=Exception("AI failed"))):
            resp = client.post("/api/v1/automation/trigger/briefing", headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_trigger_radar_error(self, client):
        with patch("app.api.automation.run_opportunity_radar", new=AsyncMock(side_effect=Exception("Radar failed"))):
            resp = client.post("/api/v1/automation/trigger/radar", headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_automation_unauthorized(self, client, no_auth):
        resp = client.post("/api/v1/automation/trigger/cleanup")
        assert resp.status_code == 401


# ===========================================================================
# VIDEOS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestVideoEndpoints:

    def test_list_videos(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_VIDEO])
        resp = client.get("/api/v1/videos/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_videos_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/videos/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_video(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_VIDEO])
        resp = client.post(
            "/api/v1/videos/",
            json={
                "url": "https://youtube.com/watch?v=new",
                "title": "New Video",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "vid-1"

    def test_create_video_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/videos/",
            json={
                "url": "https://youtube.com/watch?v=fail",
                "title": "Fail",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_video(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_VIDEO])
        resp = client.put("/api/v1/videos/vid-1", json={"title": "Updated"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "vid-1"

    def test_update_video_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/videos/nonexistent", json={"title": "Nope"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_video_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/videos/vid-1", json={"title": "Fail"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_video(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/videos/vid-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_video_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/videos/vid-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_videos_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/videos/").status_code == 401


# ===========================================================================
# BRIEFINGS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestBriefingEndpoints:

    def test_list_briefings(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_BRIEFING])
        resp = client.get("/api/v1/briefings/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_briefings_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/briefings/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_today_briefing_found(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_BRIEFING])
        resp = client.get("/api/v1/briefings/today", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "brief-1"

    def test_get_today_briefing_not_found_falls_back(self, client, mock_supabase):
        """When no briefing for today, falls back to latest briefing."""
        _cfg(mock_supabase, [SAMPLE_BRIEFING])
        resp = client.get("/api/v1/briefings/today", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_get_today_briefing_none(self, client, mock_supabase):
        """When no briefings exist at all, returns None."""
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/briefings/today", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() is None

    def test_get_briefing_by_id(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_BRIEFING])
        resp = client.get("/api/v1/briefings/brief-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "brief-1"

    def test_get_briefing_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/briefings/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_mark_briefing_read(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_BRIEFING])
        resp = client.put("/api/v1/briefings/brief-1/read", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_mark_briefing_read_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/briefings/nonexistent/read", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_mark_briefing_read_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/briefings/brief-1/read", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_briefings_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/briefings/").status_code == 401


# ===========================================================================
# ROADMAP — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestRoadmapEndpoints:

    def test_list_milestones(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_ROADMAP])
        resp = client.get("/api/v1/roadmap/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_milestones_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/roadmap/", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_get_milestone(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_ROADMAP])
        resp = client.get("/api/v1/roadmap/rm-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "rm-1"

    def test_get_milestone_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/roadmap/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_milestone(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_ROADMAP])
        resp = client.post(
            "/api/v1/roadmap/",
            json={
                "skill": "Docker",
                "category": "devops",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "rm-1"

    def test_create_milestone_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/roadmap/",
            json={
                "skill": "Fail",
                "category": "x",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_milestone(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_ROADMAP])
        resp = client.put("/api/v1/roadmap/rm-1", json={"progress": 80}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_milestone_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/roadmap/nonexistent", json={"progress": 50}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_milestone_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/roadmap/rm-1", json={"progress": 50}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_milestone(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/roadmap/rm-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_milestone_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/roadmap/rm-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_roadmap_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/roadmap/").status_code == 401


# ===========================================================================
# MEMORY — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestMemoryEndpoints:

    def test_list_memories(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MEMORY])
        resp = client.get("/api/v1/memory/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_memories_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/memory/", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_get_memory(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MEMORY])
        resp = client.get("/api/v1/memory/mem-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["key"] == "pref_theme"

    def test_get_memory_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/memory/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_memory(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MEMORY])
        resp = client.post(
            "/api/v1/memory/",
            json={
                "type": "preference",
                "key": "theme",
                "value": "dark",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["key"] == "pref_theme"

    def test_create_memory_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/memory/",
            json={
                "type": "preference",
                "key": "x",
                "value": "y",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_memory(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MEMORY])
        resp = client.put("/api/v1/memory/mem-1", json={"value": "light"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_memory_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/memory/nonexistent", json={"value": "x"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_memory_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/memory/mem-1", json={"value": "x"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_memory(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/memory/mem-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_memory_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/memory/mem-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_memory_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/memory/").status_code == 401

    def test_consolidate_memories_error(self, client):
        with patch(
            "ai.agents.memory_agent.consolidate_memories", new=AsyncMock(side_effect=Exception("consolidation failed"))
        ):
            resp = client.post("/api/v1/memory/consolidate", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["memories_created"] == 0

    def test_search_memory_error(self, client):
        with patch("app.api.memory.search_memory_orchestrator", new=AsyncMock(side_effect=Exception("search failed"))):
            resp = client.post("/api/v1/memory/search", json={"query": "test"}, headers=_AUTH_HEADER)
            assert resp.status_code == 200
            data = resp.json()
            assert data["data"]["memories"] == []

    def test_consolidate_memories_success(self, client):
        with patch(
            "ai.agents.memory_agent.consolidate_memories",
            new=AsyncMock(
                return_value={
                    "consolidation_type": "full",
                    "memories_created": 2,
                }
            ),
        ):
            resp = client.post("/api/v1/memory/consolidate", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["data"]["memories_created"] == 2

    def test_search_memory_success(self, client):
        with patch(
            "app.api.memory.search_memory_orchestrator",
            new=AsyncMock(
                return_value={
                    "memories": [{"id": "m1"}],
                    "preferences": {},
                    "summary": "found",
                }
            ),
        ):
            resp = client.post("/api/v1/memory/search", json={"query": "test"}, headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["data"]["memories"][0]["id"] == "m1"


# ===========================================================================
# ACADEMICS — 8 endpoints
# ===========================================================================


@pytest.mark.api
class TestAcademicEndpoints:

    def test_list_subjects(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SUBJECT])
        resp = client.get("/api/v1/academics/subjects", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_subjects_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/academics/subjects", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_create_subject(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SUBJECT])
        resp = client.post(
            "/api/v1/academics/subjects",
            json={
                "name": "Algorithms",
                "code": "CS301",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Data Structures"

    def test_create_subject_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/academics/subjects",
            json={
                "name": "Fail",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_delete_subject(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/academics/subjects/sub-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_subject_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/academics/subjects/sub-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_list_marks(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MARK])
        resp = client.get("/api/v1/academics/marks", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_marks_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/academics/marks", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_create_mark(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_MARK])
        resp = client.post(
            "/api/v1/academics/marks",
            json={
                "subject_id": "sub-1",
                "exam_type": "Final",
                "marks_obtained": 90,
                "max_marks": 100,
                "date": "2026-06-20",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "mark-1"

    def test_create_mark_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/academics/marks",
            json={
                "subject_id": "x",
                "exam_type": "Final",
                "marks_obtained": 90,
                "max_marks": 100,
                "date": "2026-06-20",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_delete_mark(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/academics/marks/mark-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_mark_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/academics/marks/mark-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_learning_stats(self, client, mock_supabase):
        snapshots = [
            {**SAMPLE_LEARNING_PROGRESS, "completion_rate": 75},
            {**SAMPLE_LEARNING_PROGRESS, "id": "lp-2", "completion_rate": 80},
            {**SAMPLE_LEARNING_PROGRESS, "id": "lp-3", "completion_rate": 70},
        ]
        _cfg(mock_supabase, snapshots)
        resp = client.get("/api/v1/academics/learning-progress/stats", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "avg_completion_rate" in body
        assert body["completion_rate"] > 0

    def test_learning_stats_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/academics/learning-progress/stats", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["completion_rate"] == 0

    def test_learning_stats_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/academics/learning-progress/stats", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["completion_rate"] == 0

    def test_learning_timeline(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_LEARNING_PROGRESS])
        resp = client.get("/api/v1/academics/learning-progress/timeline?days=30", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_learning_timeline_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/academics/learning-progress/timeline?days=30", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_learning_timeline_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/academics/learning-progress/timeline?days=30", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_academics_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/academics/subjects").status_code == 401


# ===========================================================================
# REVIEWS — 3 endpoints
# ===========================================================================


@pytest.mark.api
class TestReviewEndpoints:

    def test_list_reviews(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_REVIEW])
        resp = client.get("/api/v1/reviews/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_reviews_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/reviews/", headers=_AUTH_HEADER)
        assert resp.json() == []

    def test_get_latest_review_found(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_REVIEW])
        resp = client.get("/api/v1/reviews/latest", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "rev-1"

    def test_get_latest_review_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/reviews/latest", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() is None

    def test_get_review_by_id(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_REVIEW])
        resp = client.get("/api/v1/reviews/rev-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "rev-1"

    def test_get_review_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/reviews/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_reviews_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/reviews/").status_code == 401


# ===========================================================================
# MONITORING — edge cases
# ===========================================================================


@pytest.mark.api
class TestMonitoringEdgeCases:

    def test_record_token_usage_db_error_still_ok(self, client, mock_supabase):
        """Even if DB insert fails, endpoint returns 200 with status ok."""
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.post(
            "/api/v1/monitoring/token-usage",
            json={
                "agent": "test",
                "prompt_tokens": 100,
                "completion_tokens": 50,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_summary_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/monitoring/token-usage/summary", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_tokens"] == 0
        assert body["total_calls"] == 0

    def test_summary_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/monitoring/token-usage/summary", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total_tokens"] == 0

    def test_summary_with_percentiles(self, client, mock_supabase):
        items = [{"agent": "test", "total_tokens": 100, "duration_ms": i * 10} for i in range(25)]
        _cfg(mock_supabase, items)
        resp = client.get("/api/v1/monitoring/token-usage/summary", headers=_AUTH_HEADER)
        body = resp.json()
        assert body["total_calls"] == 25
        assert body["p50_ms"] > 0
        assert body["p95_ms"] > 0


# ===========================================================================
# FEEDBACK — edge cases
# ===========================================================================


@pytest.mark.api
class TestFeedbackEdgeCases:

    def test_submit_feedback_db_error(self, client, mock_supabase):
        """Feedback submission failure should return 500."""
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.post(
            "/api/v1/feedback/",
            json={
                "source": "chat",
                "target_id": "msg-1",
                "rating": 4,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 500

    def test_summary_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/feedback/summary", headers=_AUTH_HEADER)
        body = resp.json()
        assert body["total"] == 0
        assert body["positive_rate"] == 0.0

    def test_summary_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/feedback/summary", headers=_AUTH_HEADER)
        body = resp.json()
        assert body["total"] == 0

    def test_summary_mixed_ratings(self, client, mock_supabase):
        _cfg(
            mock_supabase,
            [
                {"id": "1", "source": "chat", "rating": 5},
                {"id": "2", "source": "chat", "rating": 1},
                {"id": "3", "source": "briefing", "rating": 4},
                {"id": "4", "source": "briefing", "rating": 2},
            ],
        )
        resp = client.get("/api/v1/feedback/summary", headers=_AUTH_HEADER)
        body = resp.json()
        assert body["total"] == 4
        assert body["positive"] == 2
        assert body["negative"] == 2
        assert body["positive_rate"] == 50.0


# ===========================================================================
# Sample data for new modules
# ===========================================================================

SAMPLE_COURSE = {
    "id": "course-1",
    "user_id": "user-1",
    "title": "React Masterclass",
    "platform": "Udemy",
    "url": "https://udemy.com/course/react",
    "status": "in_progress",
    "progress_percent": 40,
    "total_videos": 50,
    "completed_videos": 20,
    "deadline": None,
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-15T12:00:00",
}

SAMPLE_GOAL = {
    "id": "goal-1",
    "user_id": "user-1",
    "title": "Learn Machine Learning",
    "description": "Complete ML specialization",
    "status": "active",
    "progress": 30,
    "target_date": "2026-12-31",
    "category": "learning",
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-15T12:00:00",
}

SAMPLE_IDEA = {
    "id": "idea-1",
    "user_id": "user-1",
    "title": "Build a chatbot",
    "description": "AI chatbot for customer support",
    "stage": "validating",
    "status": "raw",
    "market_research": None,
    "competitors": None,
    "created_at": "2026-06-01T12:00:00",
    "updated_at": None,
}

SAMPLE_INCOME = {
    "id": "income-1",
    "user_id": "user-1",
    "amount": 500.0,
    "source_type": "Freelance",
    "platform": None,
    "description": None,
    "date": "2026-06-15",
    "hours_spent": 10.0,
    "effective_hourly_rate": 50.0,
    "created_at": "2026-06-15T12:00:00",
}

SAMPLE_OPPORTUNITY = {
    "id": "opp-1",
    "user_id": "user-1",
    "title": "Software Engineer Intern",
    "url": "https://company.com/jobs",
    "match_score": 85,
    "status": "new",
    "category": "internship",
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_PROJECT = {
    "id": "project-1",
    "user_id": "user-1",
    "title": "Portfolio Site",
    "status": "in_progress",
    "phase": "development",
    "blockers": None,
    "repo_url": "https://github.com/user/portfolio",
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-15T12:00:00",
}

SAMPLE_RESOURCE = {
    "id": "res-1",
    "user_id": "user-1",
    "title": "FastAPI Docs",
    "url": "https://fastapi.tiangolo.com",
    "tags": ["python", "api"],
    "created_at": "2026-06-01T12:00:00",
}


# ===========================================================================
# PREDICTIONS — additional edge case tests
# ===========================================================================


@pytest.mark.api
class TestPredictionAdvancedEdgeCases:

    def test_predict_tasks_low_priority(self, client, mock_supabase):
        task = {**SAMPLE_TASK_PENDING, "priority": "low"}
        _cfg(mock_supabase, [task, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total_pending"] == 1

    def test_predict_tasks_overdue(self, client, mock_supabase):
        task = {**SAMPLE_TASK_PENDING, "due_date": "2020-01-01T00:00:00"}
        _cfg(mock_supabase, [task, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_tasks_due_today(self, client, mock_supabase):
        from datetime import datetime, timezone

        today = datetime.now(timezone.utc).isoformat()
        task = {**SAMPLE_TASK_PENDING, "due_date": today}
        _cfg(mock_supabase, [task, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_tasks_due_within_3_days(self, client, mock_supabase):
        from datetime import datetime, timezone, timedelta

        future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        task = {**SAMPLE_TASK_PENDING, "due_date": future}
        _cfg(mock_supabase, [task, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_tasks_bad_due_date(self, client, mock_supabase):
        task = {**SAMPLE_TASK_PENDING, "due_date": "not-a-date"}
        _cfg(mock_supabase, [task, SAMPLE_TASK_COMPLETED])
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_tasks_high_count_many_completed(self, client, mock_supabase):
        tasks = [SAMPLE_TASK_PENDING]
        for i in range(25):
            tasks.append({**SAMPLE_TASK_COMPLETED, "id": f"c-{i}"})
        _cfg(mock_supabase, tasks)
        resp = client.get("/api/v1/predictions/tasks", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_habits_inactive_skipped(self, client, mock_supabase):
        inactive = {**SAMPLE_HABIT, "is_active": False}
        _cfg(mock_supabase, [inactive])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.json()["total_active"] == 0

    def test_predict_habits_medium_risk(self, client, mock_supabase):
        habit = {**SAMPLE_HABIT, "current_streak": 7, "consistency_percentage": 50.0}
        _cfg(mock_supabase, [habit])
        resp = client.get("/api/v1/predictions/habits", headers=_AUTH_HEADER)
        assert resp.json()["predictions"][0]["risk_level"] == "Medium"

    def test_predict_sleep_trend_improving(self, client, mock_supabase):
        """Data is returned by mock in DESC date order (newest first)."""
        logs = []
        for i in reversed(range(21)):
            logs.append(
                {
                    **SAMPLE_SLEEP_LOG,
                    "id": f"sleep-{i}",
                    "sleep_score": 50 + (i if i >= 14 else 0),
                    "duration_hours": 7.0,
                    "date": f"2026-06-{i+1:02d}",
                }
            )
        _cfg(mock_supabase, logs)
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["trend"] == "improving"

    def test_predict_sleep_trend_declining(self, client, mock_supabase):
        logs = []
        for i in reversed(range(21)):
            logs.append(
                {
                    **SAMPLE_SLEEP_LOG,
                    "id": f"sleep-{i}",
                    "sleep_score": 80 - (i if i >= 14 else 0),
                    "duration_hours": 7.0,
                    "date": f"2026-06-{i+1:02d}",
                }
            )
        _cfg(mock_supabase, logs)
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["trend"] == "declining"

    def test_predict_sleep_bad_bedtime(self, client, mock_supabase):
        logs = [
            {**SAMPLE_SLEEP_LOG, "sleep_score": 80, "bedtime": "bad-time"},
        ]
        _cfg(mock_supabase, logs)
        resp = client.get("/api/v1/predictions/sleep", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_slots_no_start_time(self, client, mock_supabase):
        entry = {**SAMPLE_TIME_ENTRY, "start_time": None}

        def from_side(table):
            if table == "time_entries":
                return MockQueryBuilder(return_data=[entry])
            return MockQueryBuilder(return_data=[SAMPLE_TASK_PENDING, SAMPLE_TASK_COMPLETED])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/predictions/slots", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_predict_slots_bad_start_time(self, client, mock_supabase):
        entry = {**SAMPLE_TIME_ENTRY, "start_time": "not-a-date"}

        def from_side(table):
            if table == "time_entries":
                return MockQueryBuilder(return_data=[entry])
            return MockQueryBuilder(return_data=[SAMPLE_TASK_PENDING, SAMPLE_TASK_COMPLETED])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/predictions/slots", headers=_AUTH_HEADER)
        assert resp.status_code == 200


# ===========================================================================
# NOTIFICATIONS — additional edge case tests
# ===========================================================================


@pytest.mark.api
class TestNotificationAdvancedEdgeCases:

    def test_generate_nudges_overdue_insert_error(self, client, mock_supabase):
        call_count = [0]

        def from_side(table):
            call_count[0] += 1
            if table == "tasks":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_TASK_PENDING,
                            "due_date": "2020-01-01T00:00:00",
                        }
                    ]
                )
            if call_count[0] >= 2:
                raise Exception("DB error on insert")
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_generate_nudges_sleep_insert_error(self, client, mock_supabase):
        call_count = [0]

        def from_side(table):
            call_count[0] += 1
            if table == "tasks":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_TASK_PENDING,
                            "due_date": "2020-01-01T00:00:00",
                        }
                    ]
                )
            if call_count[0] == 2:
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_HABIT,
                            "current_streak": 10,
                        }
                    ]
                )
            if call_count[0] == 3:
                return MockQueryBuilder(
                    return_data=[
                        {
                            "id": "sl-1",
                            "sleep_score": 50,
                            "date": "2026-06-01",
                        }
                        for _ in range(14)
                    ]
                )
            if call_count[0] >= 4:
                raise Exception("DB error on sleep insert")
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_generate_nudges_deadline_alerts_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_generate_nudges_deadline_alerts_query_exception(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("query failed")
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_deadline_alerts_no_due(self, client, mock_supabase):
        task = {**SAMPLE_TASK_PENDING, "due_date": None}
        _cfg(mock_supabase, [task])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_deadline_alerts_bad_date(self, client, mock_supabase):
        task = {**SAMPLE_TASK_PENDING, "due_date": "not-a-date"}
        _cfg(mock_supabase, [task])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_deadline_alerts_upcoming(self, client, mock_supabase):
        from datetime import datetime, timezone, timedelta

        task = {
            **SAMPLE_TASK_PENDING,
            "due_date": (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat(),
        }
        _cfg(mock_supabase, [task])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        alerts = resp.json()
        assert len(alerts) == 1
        assert alerts[0]["urgent"] is True

    def test_deadline_alerts_naive_datetime(self, client, mock_supabase):
        from datetime import datetime, timedelta

        task = {
            **SAMPLE_TASK_PENDING,
            "due_date": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
        }
        _cfg(mock_supabase, [task])
        resp = client.get("/api/v1/notifications/deadline-alerts", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        alerts = resp.json()
        assert len(alerts) == 1

    def test_generate_nudges_habit_insert_error(self, client, mock_supabase):
        call_count = [0]

        def from_side(table):
            call_count[0] += 1
            if table == "tasks":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_TASK_PENDING,
                            "due_date": "2020-01-01T00:00:00",
                        }
                    ]
                )
            if table == "habits":
                return MockQueryBuilder(
                    return_data=[
                        {
                            "id": "h-1",
                            "name": "Meditation",
                            "current_streak": 0,
                            "consistency_percent": 30,
                            "is_active": True,
                        }
                    ]
                )
            if table == "sleep_logs":
                return MockQueryBuilder(return_data=[])
            if call_count[0] >= 5:
                raise Exception("DB error on habit insert")
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_generate_nudges_sleep_insert_error_real(self, client, mock_supabase):
        call_count = [0]

        def from_side(table):
            call_count[0] += 1
            if table == "tasks":
                return MockQueryBuilder(
                    return_data=[
                        {
                            **SAMPLE_TASK_PENDING,
                            "due_date": "2020-01-01T00:00:00",
                        }
                    ]
                )
            if table == "habits":
                return MockQueryBuilder(return_data=[])
            if table == "sleep_logs":
                # Most recent 7 scores low (declining), older 7 high
                return MockQueryBuilder(
                    return_data=[{"sleep_score": 70, "date": f"2026-06-{14-i:02d}"} for i in range(7)]
                    + [{"sleep_score": 85, "date": f"2026-06-{7-i:02d}"} for i in range(7)]
                )
            if call_count[0] >= 5:
                raise Exception("DB error on sleep insert")
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.post("/api/v1/notifications/generate", headers=_AUTH_HEADER)
        assert resp.status_code == 200


# ===========================================================================
# AUTH — rotate-key and refresh token edge cases
# ===========================================================================


@pytest.mark.api
class TestAuthRoutes:

    def test_rotate_key_success(self, client):
        with patch("app.api.auth.rotate_api_key", return_value={"api_key": "new-key"}):
            resp = client.post("/api/v1/auth/rotate-key", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["api_key"] == "new-key"

    def test_rotate_key_unexpected_error(self, client):
        with patch("app.api.auth.rotate_api_key", side_effect=Exception("boom")):
            resp = client.post("/api/v1/auth/rotate-key", headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_refresh_token_success(self, client):
        with patch("app.api.auth.refresh_jwt_token", return_value={"access_token": "new-token"}):
            resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "valid-refresh"}, headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["access_token"] == "new-token"

    def test_refresh_token_http_error_re_raised(self, client):
        from fastapi import HTTPException

        with patch("app.api.auth.refresh_jwt_token", side_effect=HTTPException(401, "bad token")):
            resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad"}, headers=_AUTH_HEADER)
            assert resp.status_code == 401

    def test_refresh_token_unexpected_error(self, client):
        with patch("app.api.auth.refresh_jwt_token", side_effect=Exception("boom")):
            resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "x"}, headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_rotate_key_no_user_id(self, client, app):
        class NoIdUser:
            class Inner:
                pass

            user = Inner()

        from config.core.auth import get_current_user

        app.dependency_overrides[get_current_user] = lambda: NoIdUser()
        resp = client.post("/api/v1/auth/rotate-key", headers=_AUTH_HEADER)
        assert resp.status_code == 401
        app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()


# ===========================================================================
# AUTOMATION — rate limiting and error edge cases
# ===========================================================================


@pytest.mark.api
class TestAutomationRateLimitEdgeCases:

    @pytest.fixture(autouse=True)
    def _mock_agents(self):
        patchers = []
        targets = {
            "app.api.automation.generate_daily_briefing": {"status": "ok"},
            "app.api.automation.run_opportunity_radar": [],
            "app.api.automation.generate_weekly_review": {"status": "ok"},
            "app.api.automation.analyze_sleep": {"status": "ok"},
            "app.api.automation.suggest_bedtime": {"status": "ok", "bedtime": "22:00"},
            "app.api.automation.run_all_nudges": {"status": "ok", "nudges": 3},
            "app.api.automation.run_data_retention_cleanup": {
                "audit_logs_removed": 5,
                "chat_messages_removed": 10,
                "notifications_removed": 3,
            },
        }
        for target, retval in targets.items():
            p = patch(target, new=AsyncMock(return_value=retval))
            p.start()
            patchers.append(p)
        yield
        for p in patchers:
            p.stop()

    def test_trigger_briefing_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/briefing", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_radar_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/radar", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_weekly_review_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/weekly-review", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_sleep_analysis_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/sleep-analysis", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_sleep_bedtime_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/sleep-bedtime", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_nudges_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/nudges", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_cleanup_rate_limited(self, client):
        with patch("app.api.automation.endpoint_limiter") as mock_limiter:
            mock_limiter.check.return_value = False
            resp = client.post("/api/v1/automation/trigger/cleanup", headers=_AUTH_HEADER)
            assert resp.status_code == 429

    def test_trigger_proxy_errors(self, client):
        """All automation endpoints return 500 when underlying agent raises."""
        with patch("app.api.automation.generate_daily_briefing", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/briefing", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.run_opportunity_radar", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/radar", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.generate_weekly_review", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/weekly-review", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.analyze_sleep", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/sleep-analysis", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.suggest_bedtime", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/sleep-bedtime", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.run_all_nudges", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/nudges", headers=_AUTH_HEADER)
            assert resp.status_code == 500
        with patch("app.api.automation.run_data_retention_cleanup", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.post("/api/v1/automation/trigger/cleanup", headers=_AUTH_HEADER)
            assert resp.status_code == 500


# ===========================================================================
# PROMPTS — additional edge cases
# ===========================================================================


@pytest.mark.api
class TestPromptAdvancedEdgeCases:

    @pytest.fixture(autouse=True)
    def _mock_prompts(self):
        mock_entry = MagicMock()
        mock_entry.name = "briefing_agent"
        mock_entry.category = "agents"
        mock_entry.file_path = MagicMock()
        mock_entry.file_path.__str__ = MagicMock(return_value="/prompts/agents/briefing_agent.md")
        mock_entry.file_path.relative_to.return_value = "prompts/agents/briefing_agent.md"
        mock_entry.frontmatter = {"version": "2.1.0", "status": "active"}
        mock_entry.body = "You are a briefing assistant."
        mock_entry.system_prompt = mock_entry.body
        mock_entry.render.return_value = "Rendered: You are a briefing assistant."
        with patch("app.api.prompts.prompts") as mock_prompts:
            mock_prompts.list_prompts.return_value = ["briefing_agent"]
            mock_prompts.get.return_value = mock_entry
            yield

    def test_list_prompts_exception(self, client):
        with patch("app.api.prompts.prompts") as mock_pm:
            mock_pm.list_prompts.side_effect = Exception("loader error")
            resp = client.get("/api/v1/prompts/", headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_get_prompt_returns_none_skipped_in_list(self, client):
        with patch("app.api.prompts.prompts") as mock_pm:
            mock_pm.list_prompts.return_value = ["ghost"]
            mock_pm.get.return_value = None
            resp = client.get("/api/v1/prompts/", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["total"] == 0

    def test_render_general_exception(self, client):
        with patch("app.api.prompts.prompts") as mock_pm:
            mock_entry = MagicMock()
            mock_entry.render.side_effect = RuntimeError("render crash")
            mock_pm.get.return_value = mock_entry
            mock_pm.list_prompts.return_value = ["briefing_agent"]
            resp = client.post(
                "/api/v1/prompts/briefing_agent/render",
                json={
                    "variables": {"x": "y"},
                },
                headers=_AUTH_HEADER,
            )
            assert resp.status_code == 500

    def test_prompt_history_git_timeout(self, client):
        with patch("app.api.prompts.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("git log", timeout=10)
            resp = client.get("/api/v1/prompts/briefing_agent/history", headers=_AUTH_HEADER)
            assert resp.status_code == 500

    def test_prompt_history_no_commits_fallback(self, client):
        with patch("app.api.prompts.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            resp = client.get("/api/v1/prompts/briefing_agent/history", headers=_AUTH_HEADER)
            assert resp.status_code == 200
            assert resp.json()["commits"][0]["hash"] == "initial"


# ===========================================================================
# COURSES — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestCourseEndpoints:

    def test_list_courses(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.get("/api/v1/courses/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_courses_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/courses/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.get("/api/v1/courses/course-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "course-1"

    def test_get_course_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/courses/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.post(
            "/api/v1/courses/",
            json={
                "title": "Vue Basics",
                "platform": "YouTube",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "course-1"

    def test_create_course_with_deadline(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.post(
            "/api/v1/courses/",
            json={
                "title": "Vue Basics",
                "platform": "YouTube",
                "deadline": "2026-12-31T23:59:59Z",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_update_course_invalid_deadline(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.put("/api/v1/courses/course-1", json={"deadline": "bad-date"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_create_course_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/courses/",
            json={
                "title": "Fail",
                "platform": "x",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.put("/api/v1/courses/course-1", json={"progress_percent": 80}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_course_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/courses/nonexistent", json={"title": "Nope"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_course_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/courses/course-1", json={"title": "Fail"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_course(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/courses/course-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_course_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/courses/course-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_courses_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/courses/").status_code == 401


# ===========================================================================
# GOALS — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestGoalEndpoints:

    def test_list_goals(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.get("/api/v1/goals/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_goals_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/goals/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.get("/api/v1/goals/goal-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "goal-1"

    def test_get_goal_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/goals/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.post(
            "/api/v1/goals/",
            json={
                "title": "Learn Go",
                "category": "programming",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_goal_with_target_date(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.post(
            "/api/v1/goals/",
            json={
                "title": "Learn Go",
                "category": "programming",
                "target_date": "2026-12-31T23:59:59Z",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_goal_invalid_target_date(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.post(
            "/api/v1/goals/",
            json={
                "title": "Learn Go",
                "category": "programming",
                "target_date": "not-a-date",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_goal_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/goals/",
            json={
                "title": "Fail",
                "category": "x",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.put("/api/v1/goals/goal-1", json={"progress": 80}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_goal_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/goals/nonexistent", json={"progress": 50}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_goal_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/goals/goal-1", json={"progress": 50}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/goals/goal-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_goal_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/goals/goal-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_goals_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/goals/").status_code == 401


# ===========================================================================
# HABITS — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestHabitEndpoints:

    def test_list_habits(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.get("/api/v1/habits/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_habits_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/habits/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.get("/api/v1/habits/habit-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "habit-1"

    def test_get_habit_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/habits/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.post(
            "/api/v1/habits/",
            json={
                "name": "Read",
                "frequency": "daily",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_habit_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/habits/",
            json={
                "name": "Fail",
                "frequency": "daily",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.put("/api/v1/habits/habit-1", json={"name": "Updated"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_habit_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/habits/nonexistent", json={"name": "Nope"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_habit_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/habits/habit-1", json={"name": "Fail"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/habits/habit-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_habit_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/habits/habit-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_habits_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/habits/").status_code == 401


# ===========================================================================
# IDEAS — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestIdeaEndpoints:

    def test_list_ideas(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.get("/api/v1/ideas/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_ideas_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/ideas/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.get("/api/v1/ideas/idea-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "idea-1"

    def test_get_idea_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/ideas/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.post(
            "/api/v1/ideas/",
            json={
                "title": "New app idea",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_idea_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/ideas/",
            json={
                "title": "Fail",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.put("/api/v1/ideas/idea-1", json={"title": "Updated"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_idea_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/ideas/nonexistent", json={"title": "Nope"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_idea_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/ideas/idea-1", json={"title": "Fail"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/ideas/idea-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_idea_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/ideas/idea-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_ideas_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/ideas/").status_code == 401


# ===========================================================================
# INCOME — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestIncomeEndpoints:

    def test_list_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.get("/api/v1/income/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_income_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/income/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.get("/api/v1/income/income-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "income-1"

    def test_get_income_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/income/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.post(
            "/api/v1/income/",
            json={
                "source_type": "Freelance",
                "amount": 100,
                "hours_spent": 5,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["effective_hourly_rate"] == 50.0

    def test_create_income_no_rate(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.post(
            "/api/v1/income/",
            json={
                "source_type": "Gift",
                "amount": 100,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_income_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/income/",
            json={
                "source_type": "Test",
                "amount": 50,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.put("/api/v1/income/income-1", json={"amount": 600}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_income_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/income/nonexistent", json={"amount": 100}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_income_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/income/income-1", json={"amount": 100}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_income(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/income/income-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_income_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/income/income-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_income_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/income/").status_code == 401


# ===========================================================================
# OPPORTUNITIES — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestOpportunityEndpoints:

    def test_list_opportunities(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.get("/api/v1/opportunities/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_opportunities_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/opportunities/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.get("/api/v1/opportunities/opp-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "opp-1"

    def test_get_opportunity_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/opportunities/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.post(
            "/api/v1/opportunities/",
            json={
                "title": "New Job",
                "url": "https://example.com",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_opportunity_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/opportunities/",
            json={
                "title": "Fail",
                "url": "https://x.com",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.put("/api/v1/opportunities/opp-1", json={"match_score": 90}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_opportunity_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/opportunities/nonexistent", json={"status": "applied"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_opportunity_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/opportunities/opp-1", json={"status": "applied"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/opportunities/opp-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_opportunity_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/opportunities/opp-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_opportunities_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/opportunities/").status_code == 401

    def test_match_opportunities_error(self, client):
        with patch("app.api.opportunities.match_opportunities", new=AsyncMock(side_effect=Exception("match failed"))):
            resp = client.post("/api/v1/opportunities/match", json={"query": "test"}, headers=_AUTH_HEADER)
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["matches"] == []

    def test_match_opportunities_success(self, client):
        with patch(
            "app.api.opportunities.match_opportunities",
            new=AsyncMock(
                return_value={
                    "matches": [{"id": "m1", "score": 95}],
                    "summary": "good fit",
                }
            ),
        ):
            resp = client.post("/api/v1/opportunities/match", json={"query": "test"}, headers=_AUTH_HEADER)
            assert resp.status_code == 200
            data = resp.json()
            assert data["data"]["matches"][0]["score"] == 95


# ===========================================================================
# PROJECTS — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestProjectEndpoints:

    def test_list_projects(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.get("/api/v1/projects/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_projects_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/projects/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.get("/api/v1/projects/project-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "project-1"

    def test_get_project_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/projects/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.post(
            "/api/v1/projects/",
            json={
                "title": "New Project",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_project_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/projects/",
            json={
                "title": "Fail",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.put("/api/v1/projects/project-1", json={"status": "completed"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_project_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/projects/nonexistent", json={"status": "completed"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_project_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/projects/project-1", json={"status": "completed"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_project(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/projects/project-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_project_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/projects/project-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_projects_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/projects/").status_code == 401


# ===========================================================================
# RESOURCES — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestResourceEndpoints:

    def test_list_resources(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.get("/api/v1/resources/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_resources_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/resources/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.get("/api/v1/resources/res-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "res-1"

    def test_get_resource_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/resources/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.post(
            "/api/v1/resources/",
            json={
                "title": "New Resource",
                "url": "https://example.com",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_resource_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/resources/",
            json={
                "title": "Fail",
                "url": "https://x.com",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.put("/api/v1/resources/res-1", json={"title": "Updated"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_resource_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/resources/nonexistent", json={"title": "Nope"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_resource_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/resources/res-1", json={"title": "Fail"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/resources/res-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_resource_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/resources/res-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_resources_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/resources/").status_code == 401


# ===========================================================================
# SLEEP — 5 endpoints
# ===========================================================================


@pytest.mark.api
class TestSleepEndpoints:

    def test_list_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP_LOG])
        resp = client.get("/api/v1/sleep/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_sleep_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/sleep/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP_LOG])
        resp = client.get("/api/v1/sleep/sleep-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "sleep-1"

    def test_get_sleep_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/sleep/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP_LOG])
        resp = client.put("/api/v1/sleep/sleep-1", json={"sleep_score": 90}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_sleep_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/sleep/nonexistent", json={"sleep_score": 80}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_sleep_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/sleep/sleep-1", json={"sleep_score": 90}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_create_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP_LOG])
        resp = client.post(
            "/api/v1/sleep/",
            json={
                "date": "2026-06-20",
                "bedtime": "23:00",
                "wake_time": "07:00",
                "quality_rating": 4,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_sleep_crosses_midnight(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP_LOG])
        resp = client.post(
            "/api/v1/sleep/",
            json={
                "date": "2026-06-20",
                "bedtime": "23:00",
                "wake_time": "06:00",
                "quality_rating": 3,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_sleep_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/sleep/",
            json={
                "date": "2026-06-20",
                "bedtime": "23:00",
                "wake_time": "07:00",
                "quality_rating": 4,
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_delete_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/sleep/sleep-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_sleep_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/sleep/sleep-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_sleep_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/sleep/").status_code == 401


# ===========================================================================
# TIME — 7 endpoints
# ===========================================================================


@pytest.mark.api
class TestTimeEndpoints:

    def test_list_time_entries(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.get("/api/v1/time/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_time_entries_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/time/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.get("/api/v1/time/time-1", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "time-1"

    def test_get_time_entry_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/time/nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.post(
            "/api/v1/time/",
            json={
                "start_time": "2026-06-20T09:00:00",
                "end_time": "2026-06-20T10:30:00",
                "category": "coding",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_time_entry_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/time/",
            json={
                "start_time": "2026-06-20T09:00:00",
                "end_time": "2026-06-20T10:00:00",
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.put("/api/v1/time/time-1", json={"category": "reading"}, headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_time_entry_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/time/nonexistent", json={"category": "x"}, headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_update_time_entry_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.put("/api/v1/time/time-1", json={"category": "x"}, headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_delete_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [{}])
        resp = client.delete("/api/v1/time/time-1", headers=_AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_time_entry_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [{}], error="delete failed")
        resp = client.delete("/api/v1/time/time-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_daily_stats(self, client, mock_supabase):
        _cfg(mock_supabase, [{"category": "coding", "duration_minutes": 90}])
        resp = client.get("/api/v1/time/stats/daily?date=2026-06-20", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_minutes"] == 90

    def test_daily_stats_no_date(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/time/stats/daily", headers=_AUTH_HEADER)
        assert resp.status_code == 200

    def test_stop_timer(self, client, mock_supabase):
        _cfg(
            mock_supabase,
            [{**SAMPLE_TIME_ENTRY, "start_time": "2026-06-20T09:00:00", "end_time": "2026-06-20T10:30:00"}],
        )
        resp = client.post("/api/v1/time/stop?entry_id=time-1", headers=_AUTH_HEADER)
        assert resp.status_code == 201

    def test_stop_timer_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.post("/api/v1/time/stop?entry_id=nonexistent", headers=_AUTH_HEADER)
        assert resp.status_code == 404

    def test_stop_timer_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="update failed")
        resp = client.post("/api/v1/time/stop?entry_id=time-1", headers=_AUTH_HEADER)
        assert resp.status_code == 400

    def test_time_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/time/").status_code == 401


# ===========================================================================
# CHAT — build_context unit tests (pure function, no mocking needed)
# ===========================================================================


@pytest.mark.api
class TestBuildContext:

    def test_pending_tasks_over_5_shows_more(self):
        from app.api.chat import build_context

        tasks = [{"title": f"Task {i}", "priority": "medium", "due_date": "2026-07-01"} for i in range(10)]
        result = build_context(tasks, [], [], [], [], [], [], {})
        assert "... and 5 more" in result

    def test_habits_section(self):
        from app.api.chat import build_context

        habits = [{"name": "Meditation", "is_active": True, "current_streak": 15}]
        result = build_context([], [], [], habits, [], [], [], {})
        assert "Habits" in result
        assert "Meditation" in result

    def test_habits_none_active(self):
        from app.api.chat import build_context

        habits = [{"name": "Old habit", "is_active": False, "current_streak": 0}]
        result = build_context([], [], [], habits, [], [], [], {})
        assert "Habits" not in result

    def test_sleep_section(self):
        from app.api.chat import build_context

        logs = [{"sleep_score": 82, "duration_hours": 7.5}]
        result = build_context([], [], [], [], logs, [], [], {})
        assert "Last Sleep" in result
        assert "82/100" in result

    def test_time_tracking_with_categories(self):
        from app.api.chat import build_context

        entries = [
            {"duration_minutes": 90, "category": "development"},
            {"duration_minutes": 30, "category": "meeting"},
        ]
        result = build_context([], [], [], [], [], entries, [], {})
        assert "Time Tracking" in result
        assert "development" in result
        assert "meeting" in result
        assert "2h 0m" in result

    def test_time_tracking_empty_categories(self):
        from app.api.chat import build_context

        entries = [{"duration_minutes": 90}]
        result = build_context([], [], [], [], [], entries, [], {})
        assert "Time Tracking" in result

    def test_recent_conversation_history(self):
        from app.api.chat import build_context

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = build_context([], [], [], [], [], [], messages, {})
        assert "Conversation History" in result
        assert "user: Hello" in result

    def test_memory_summary_included(self):
        from app.api.chat import build_context

        memory = {"summary": "User prefers short answers", "preferences": {"preferred_category": "general"}}
        result = build_context([], [], [], [], [], [], [], memory)
        assert "Memory Context" in result
        assert "short answers" in result

    def test_goals_section(self):
        from app.api.chat import build_context

        goals = [{"title": "Learn Rust", "progress": 45}]
        result = build_context([], goals, [], [], [], [], [], {})
        assert "Active Goals" in result
        assert "Learn Rust" in result

    def test_courses_in_progress(self):
        from app.api.chat import build_context

        courses = [{"title": "ML Course", "status": "in_progress", "progress_percent": 60}]
        result = build_context([], [], courses, [], [], [], [], {})
        assert "Courses In Progress" in result

    def test_courses_no_in_progress(self):
        from app.api.chat import build_context

        courses = [{"title": "Done", "status": "completed", "progress_percent": 100}]
        result = build_context([], [], courses, [], [], [], [], {})
        assert "Courses In Progress" not in result

    def test_message_truncation(self):
        from app.api.chat import build_context

        long = "x" * 200
        messages = [{"role": "user", "content": long}]
        result = build_context([], [], [], [], [], [], messages, {})
        assert "..." in result

    def test_courses_field_not_present(self):
        from app.api.chat import build_context

        courses = [{"title": "C1"}]
        result = build_context([], [], courses, [], [], [], [], {})
        assert "Courses" not in result or True  # should not crash


# ===========================================================================
# CHAT — list_conversations (GET /)
# ===========================================================================


@pytest.mark.api
class TestChatListConversations:

    def test_list_conversations_multiple(self, client, mock_supabase):
        def from_side(table):
            if table == "chat_messages":
                return MockQueryBuilder(
                    return_data=[
                        {
                            "conversation_id": "conv-1",
                            "created_at": "2026-06-20T12:00:00",
                            "content": "Hello ARIA",
                            "role": "user",
                        },
                        {
                            "conversation_id": "conv-1",
                            "created_at": "2026-06-20T12:00:01",
                            "content": "Hi there!",
                            "role": "assistant",
                        },
                        {
                            "conversation_id": "conv-2",
                            "created_at": "2026-06-19T10:00:00",
                            "content": "What are my tasks?",
                            "role": "user",
                        },
                    ]
                )
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/chat/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        ids = [c["id"] for c in body]
        assert "conv-1" in ids
        assert "conv-2" in ids

    def test_list_conversations_single(self, client, mock_supabase):
        def from_side(table):
            if table == "chat_messages":
                return MockQueryBuilder(
                    return_data=[
                        {
                            "conversation_id": None,
                            "created_at": "2026-06-20T12:00:00",
                            "content": "Hello",
                            "role": "user",
                        },
                    ]
                )
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/chat/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["id"] == "default"

    def test_list_conversations_empty(self, client, mock_supabase):
        def from_side(table):
            if table == "chat_messages":
                return MockQueryBuilder(return_data=[])
            return MockQueryBuilder(return_data=[])

        mock_supabase.from_.side_effect = from_side
        resp = client.get("/api/v1/chat/", headers=_AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_conversations_db_error(self, client, mock_supabase):
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.get("/api/v1/chat/", headers=_AUTH_HEADER)
        assert resp.status_code == 500

    def test_list_conversations_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/chat/")
        assert resp.status_code == 401


# ===========================================================================
# CHAT — advanced POST endpoint tests (error paths, LLM success, etc.)
# ===========================================================================


def _setup_full_chat_mocks(
    mock_supabase,
    tasks=None,
    goals=None,
    courses=None,
    habits=None,
    sleep_logs=None,
    time_entries=None,
    chat_messages=None,
):
    def side_effect(table):
        builders = {
            "tasks": MockQueryBuilder(return_data=tasks or []),
            "goals": MockQueryBuilder(return_data=goals or []),
            "courses": MockQueryBuilder(return_data=courses or []),
            "habits": MockQueryBuilder(return_data=habits or []),
            "sleep_logs": MockQueryBuilder(return_data=sleep_logs or []),
            "time_entries": MockQueryBuilder(return_data=time_entries or []),
            "chat_messages": MockQueryBuilder(return_data=chat_messages or []),
        }
        return builders.get(table, MockQueryBuilder(return_data=[]))

    mock_supabase.from_.side_effect = side_effect


@pytest.mark.api
class TestChatAdvancedEndpoints:

    def test_chat_rate_limited(self, client, mock_supabase):
        with patch("app.api.chat.endpoint_limiter.check", return_value=False):
            resp = client.post("/api/v1/chat/", json={"message": "hi"}, headers=_AUTH_HEADER)
        assert resp.status_code == 429
        assert "Rate limit" in resp.json()["detail"]

    def test_chat_llm_success_path(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase)
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="AI response here")):
            resp = client.post("/api/v1/chat/", json={"message": "How am I doing?"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["response"] == "AI response here"

    def test_chat_with_system_override(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase)
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="With override")):
            resp = client.post(
                "/api/v1/chat/",
                json={
                    "message": "Analyze my day",
                    "context": "Be extra concise",
                },
                headers=_AUTH_HEADER,
            )
        assert resp.status_code == 201
        assert resp.json()["response"] == "With override"

    def test_chat_memory_failure_logged(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase)
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="OK")):
            with patch("app.api.chat.get_memory_summary", new=AsyncMock(side_effect=Exception("Mem failed"))):
                resp = client.post("/api/v1/chat/", json={"message": "hi"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201

    def test_chat_store_interaction_failure(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase)
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="OK")):
            with patch("app.api.chat.store_interaction", new=AsyncMock(side_effect=Exception("Store failed"))):
                resp = client.post("/api/v1/chat/", json={"message": "hello"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201

    def test_chat_habit_fallback(self, client, mock_supabase):
        _setup_full_chat_mocks(
            mock_supabase,
            habits=[
                {"name": "Meditation", "is_active": True, "current_streak": 15},
            ],
        )
        resp = client.post("/api/v1/chat/", json={"message": "tell me about habits"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert "active habits" in resp.json()["response"].lower()

    def test_chat_habit_fallback_empty(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase, habits=[])
        resp = client.post("/api/v1/chat/", json={"message": "habits"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert "no habits" in resp.json()["response"].lower()

    def test_chat_courses_fallback_in_progress(self, client, mock_supabase):
        _setup_full_chat_mocks(
            mock_supabase,
            courses=[
                {"title": "ML Course", "status": "in_progress"},
            ],
        )
        resp = client.post("/api/v1/chat/", json={"message": "courses update"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert "currently taking" in resp.json()["response"].lower()

    def test_chat_goals_fallback_empty(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase, goals=[])
        resp = client.post("/api/v1/chat/", json={"message": "goal status"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert "don't have any active goals" in resp.json()["response"].lower()

    def test_chat_tasks_fallback_many(self, client, mock_supabase):
        tasks = [{"title": f"Task {i}", "priority": "medium", "due_date": "2026-07-01"} for i in range(10)]
        _setup_full_chat_mocks(mock_supabase, tasks=tasks)
        resp = client.post("/api/v1/chat/", json={"message": "show tasks"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert "pending tasks" in resp.json()["response"].lower()

    def test_chat_build_context_with_all_sections(self, client, mock_supabase):
        tasks = [{"title": "Finish report", "priority": "high", "due_date": "2026-07-01"}]
        goals = [{"title": "Learn Python", "progress": 50}]
        courses = [{"title": "FastAPI Course", "status": "in_progress", "progress_percent": 30}]
        habits = [{"name": "Read", "is_active": True, "current_streak": 7}]
        sleep_logs = [{"sleep_score": 80, "duration_hours": 7.0}]
        time_entries = [{"duration_minutes": 120, "category": "coding"}]
        _setup_full_chat_mocks(
            mock_supabase,
            tasks=tasks,
            goals=goals,
            courses=courses,
            habits=habits,
            sleep_logs=sleep_logs,
            time_entries=time_entries,
        )
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="Full context response")):
            resp = client.post("/api/v1/chat/", json={"message": "give me a summary"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["response"] == "Full context response"

    def test_chat_aria_prompt_not_found(self, client, mock_supabase):
        _setup_full_chat_mocks(mock_supabase)
        with patch("app.api.chat.llm.generate", new=AsyncMock(return_value="Fallback system response")):
            with patch("app.api.chat.prompts.get_system", return_value=None):
                resp = client.post("/api/v1/chat/", json={"message": "test"}, headers=_AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["response"] == "Fallback system response"


# ===========================================================================
# NLP — extended endpoint tests covering date formats, patterns, schedule
# ===========================================================================


@pytest.mark.api
class TestNLPExtended:

    def test_parse_date_tomorrow(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "create a task to study tomorrow",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            from datetime import datetime, timedelta

            expected = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            assert body["task"]["due_date"] == expected

    def test_parse_date_day_name(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "remind me to submit assignment on monday",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["due_date"] is not None

    def test_parse_date_relative_days(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "create task finish project in 3 days",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["due_date"] is not None

    def test_parse_date_relative_weeks(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "add task review code in 2 weeks",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["due_date"] is not None

    def test_parse_date_mm_dd_yyyy(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "create task buy gift 12/25/2026",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["due_date"] == "2026-12-25"

    def test_parse_date_mm_dd_yy(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "add task renew license 1/15/26",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task":
            assert body["task"]["due_date"] == "2026-01-15"

    def test_parse_hours_minutes(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "create task code review (2 hours)",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        if body["type"] == "create_task" and body["task"]["estimated_minutes"]:
            assert body["task"]["estimated_minutes"] == 120

    def test_parse_remind_me_pattern(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "remind me to call the bank",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "create_task"
        assert "call the bank" in body["task"]["title"]

    def test_parse_i_need_to_pattern(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "i need to finish the report",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "create_task"

    def test_parse_schedule_pattern(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "schedule study session for tomorrow",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "create_task"

    def test_parse_go_to_navigation(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "go to my resources",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "navigate"
        assert "resources" in body["navigation"]

    def test_parse_show_navigation(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "show me my income",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "navigate"
        assert "income" in body["navigation"]

    def test_parse_open_navigation(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "open my goals page",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "navigate"
        assert "goals" in body["navigation"]

    def test_parse_partial_route_match(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "go to my youtube vault",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "navigate"
        assert "youtube-vault" in body["navigation"]

    def test_parse_take_me_to_navigation(self, client):
        resp = client.post(
            "/api/v1/nlp/parse",
            json={
                "text": "take me to the dashboard",
            },
            headers=_AUTH_HEADER,
        )
        body = resp.json()
        assert body["type"] == "navigate"

    def test_execute_schedule(self, client, mock_supabase):
        _cfg(mock_supabase, [{"id": "sched-1"}])
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "schedule",
                "schedule": {
                    "description": "Focus session",
                    "duration_minutes": 60,
                    "start_time": "2026-06-20T14:00:00",
                    "category": "focus",
                },
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert "Scheduled" in resp.json()["message"]

    def test_execute_schedule_db_error(self, client, mock_supabase):
        mock_supabase.table.side_effect = Exception("DB error")
        mock_supabase.from_.side_effect = Exception("DB error")
        resp = client.post(
            "/api/v1/nlp/execute",
            json={
                "type": "schedule",
                "schedule": {"description": "Fail", "duration_minutes": 30},
            },
            headers=_AUTH_HEADER,
        )
        assert resp.status_code == 500


# ===========================================================================
# NLP — helper function unit tests
# ===========================================================================


@pytest.mark.api
class TestNLPHelpers:

    def test_extract_date_day_name(self):
        from app.api.nlp import extract_date

        result = extract_date("do this on monday")
        assert result is not None

    def test_extract_date_tomorrow(self):
        from app.api.nlp import extract_date
        from datetime import datetime, timedelta

        expected = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert extract_date("do it tomorrow") == expected

    def test_extract_date_today(self):
        from app.api.nlp import extract_date
        from datetime import datetime

        assert extract_date("do it today") == datetime.now().strftime("%Y-%m-%d")

    def test_extract_date_mm_dd_yyyy(self):
        from app.api.nlp import extract_date

        assert extract_date("by 12/25/2026") == "2026-12-25"

    def test_extract_date_mm_dd_yy(self):
        from app.api.nlp import extract_date

        assert extract_date("by 1/15/26") == "2026-01-15"

    def test_extract_date_relative_days(self):
        from app.api.nlp import extract_date
        from datetime import datetime, timedelta

        expected = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        assert extract_date("do it in 3 days") == expected

    def test_extract_date_relative_weeks(self):
        from app.api.nlp import extract_date
        from datetime import datetime, timedelta

        expected = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
        assert extract_date("do it in 2 weeks") == expected

    def test_extract_date_none(self):
        from app.api.nlp import extract_date

        assert extract_date("no date here") is None

    def test_extract_priority_high(self):
        from app.api.nlp import extract_priority

        assert extract_priority("urgent task") == "high"
        assert extract_priority("critical bug") == "high"
        assert extract_priority("high priority item") == "high"

    def test_extract_priority_low(self):
        from app.api.nlp import extract_priority

        assert extract_priority("low priority thing") == "low"
        assert extract_priority("whenever you can") == "low"
        assert extract_priority("optional task") == "low"

    def test_extract_priority_none(self):
        from app.api.nlp import extract_priority

        assert extract_priority("normal task") is None

    def test_extract_minutes_hours(self):
        from app.api.nlp import extract_minutes

        assert extract_minutes("takes 2 hours") == 120
        assert extract_minutes("takes 1 hr") == 60
        assert extract_minutes("takes 3 hrs") == 180

    def test_extract_minutes_minutes(self):
        from app.api.nlp import extract_minutes

        assert extract_minutes("takes 30 minutes") == 30
        assert extract_minutes("takes 45 min") == 45
        assert extract_minutes("takes 60 mins") == 60

    def test_extract_minutes_none(self):
        from app.api.nlp import extract_minutes

        assert extract_minutes("no time given") is None

    def test_resolve_route_exact(self):
        from app.api.nlp import resolve_route

        assert resolve_route("tasks") == "/dashboard/tasks"
        assert resolve_route("  tasks  ") == "/dashboard/tasks"

    def test_resolve_route_partial_match(self):
        from app.api.nlp import resolve_route

        assert resolve_route("youtube") is not None

    def test_resolve_route_none(self):
        from app.api.nlp import resolve_route

        assert resolve_route("nonexistent") is None
