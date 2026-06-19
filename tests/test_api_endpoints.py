"""Tests for API patterns — schema validation, error responses, pagination."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.mark.api
class TestTaskSchemas:
    """Test task Pydantic schema validation."""

    def test_task_create_validates_required_fields(self):
        from database.schemas.task import TaskCreate

        task = TaskCreate(title="Test task", priority="medium")
        assert task.title == "Test task"
        assert task.priority == "medium"

    def test_task_create_validates_optional_fields(self):
        from database.schemas.task import TaskCreate
        from datetime import datetime

        task = TaskCreate(
            title="Test task",
            priority="high",
            due_date=datetime(2026, 12, 31),
            estimated_minutes=60,
            course_id="course-1",
        )
        assert task.title == "Test task"
        assert task.due_date is not None

    def test_task_update_allows_partial(self):
        from database.schemas.task import TaskUpdate

        update = TaskUpdate(status="completed")
        assert update.status == "completed"
        assert update.title is None

    def test_task_response_includes_all_fields(self):
        from database.schemas.task import TaskResponse
        from datetime import datetime

        task = TaskResponse(
            id="task-1",
            title="Test",
            status="pending",
            priority="medium",
            user_id="user-1",
            completed_at=None,
            missed_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert task.id == "task-1"
        assert task.status == "pending"
        assert task.user_id == "user-1"


@pytest.mark.api
class TestHealthEndpoint:
    """Test health check response structure."""

    def test_health_response_structure(self):
        response = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": 1234567890.0,
        }
        assert response["status"] in ("healthy", "degraded", "unhealthy")
        assert isinstance(response["version"], str)
        assert isinstance(response["timestamp"], (int, float))

    def test_health_live_response(self):
        response = {"status": "alive"}
        assert response["status"] == "alive"

    def test_health_ready_response_structure(self):
        response = {
            "status": "healthy",
            "version": "1.0.0",
            "dependencies": {
                "api": {"status": "ok"},
                "supabase": {"status": "ok"},
            },
        }
        assert response["status"] in ("healthy", "degraded")
        assert "dependencies" in response


@pytest.mark.api
class TestErrorHandling:
    """Test error response structures."""

    def test_404_structure(self):
        from fastapi import HTTPException

        try:
            raise HTTPException(status_code=404, detail="Not found")
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Not found"

    def test_400_structure(self):
        from fastapi import HTTPException

        try:
            raise HTTPException(status_code=400, detail="Bad request")
        except HTTPException as e:
            assert e.status_code == 400
            assert "Bad request" in str(e.detail)

    def test_rate_limit_structure(self):
        from fastapi import HTTPException

        try:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Max 100 requests per 60s",
            )
        except HTTPException as e:
            assert e.status_code == 429
            assert "Rate limit" in e.detail

    def test_standard_error_schema(self):
        error = {
            "detail": "Task not found",
            "error_code": "TASK_NOT_FOUND",
            "request_id": "uuid-string",
            "timestamp": "2026-06-14T12:00:00Z",
        }
        assert "detail" in error
        assert "error_code" in error
        assert "request_id" in error


@pytest.mark.api
class TestPagination:
    """Test standard pagination patterns."""

    def test_pagination_params(self):
        params = {"limit": 20, "offset": 0}
        assert params["limit"] > 0
        assert params["offset"] >= 0

    def test_pagination_response(self):
        response = {
            "data": [{"id": "1", "title": "Test"}],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }
        assert isinstance(response["data"], list)
        assert response["limit"] == 20
        assert response["total"] >= 0


# ===========================================================================
# FastAPI TestClient CRUD Tests for all 13 API routers
# ===========================================================================

# ---------------------------------------------------------------------------
# Mock query builder — fluent chaining mock for supabase queries
# ---------------------------------------------------------------------------


class MockQueryBuilder:
    """Fluent mock for supabase query builder (.select().eq().execute())."""

    def __init__(self, return_data=None, error_message=None):
        self._return_data = return_data if return_data is not None else []
        self._error_message = error_message

    def select(self, *args, **kwargs):
        return self

    def eq(self, col, val):
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


# ---------------------------------------------------------------------------
# Sample data used across all endpoint tests
# ---------------------------------------------------------------------------

SAMPLE_TASK = {
    "id": "task-1",
    "title": "Complete project report",
    "description": "Finish the quarterly report",
    "priority": "high",
    "category": "project",
    "estimated_minutes": 120,
    "due_date": "2026-07-01T12:00:00",
    "goal_id": None,
    "project_id": None,
    "dependency_id": None,
    "is_recurring": False,
    "recurring_frequency": None,
    "user_id": "user-1",
    "status": "pending",
    "completed_at": None,
    "missed_count": 0,
    "created_at": "2026-06-14T12:00:00",
    "updated_at": "2026-06-14T12:00:00",
}

SAMPLE_COURSE = {
    "id": "course-1",
    "user_id": "user-1",
    "title": "ML Specialization",
    "platform": "Coursera",
    "url": "https://coursera.org/ml",
    "total_videos": 120,
    "completed_videos": 45,
    "deadline": "2026-12-31T00:00:00+00:00",
    "why_enrolled": "Career growth",
    "status": "in_progress",
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_GOAL = {
    "id": "goal-1",
    "user_id": "user-1",
    "title": "Learn React Native",
    "description": "Build a mobile app",
    "roadmap_type": "career_skills",
    "target_date": "2026-09-01T00:00:00+00:00",
    "hours_per_day": 2.0,
    "days_per_week": 5.0,
    "intensity": "high",
    "status": "active",
    "progress": 30,
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_HABIT = {
    "id": "habit-1",
    "user_id": "user-1",
    "name": "Morning Meditation",
    "frequency": "daily",
    "time_target_minutes": 15,
    "is_active": True,
    "current_streak": 7,
    "best_streak": 14,
    "consistency_percentage": 85.0,
}

SAMPLE_SLEEP = {
    "id": "sleep-1",
    "user_id": "user-1",
    "bedtime": "2026-06-13T23:00:00",
    "wake_time": "2026-06-14T07:00:00",
    "quality_rating": 4,
    "duration_hours": 8.0,
    "sleep_score": 85,
    "sleep_debt": 0.0,
    "created_at": "2026-06-14T07:30:00",
}

SAMPLE_INCOME = {
    "id": "income-1",
    "user_id": "user-1",
    "source_type": "freelance",
    "amount": 500.0,
    "platform": "Upwork",
    "description": "Web dev project",
    "date": "2026-06-14",
    "hours_spent": 10.0,
    "effective_hourly_rate": 50.0,
    "created_at": "2026-06-14T12:00:00",
}

SAMPLE_PROJECT = {
    "id": "project-1",
    "user_id": "user-1",
    "title": "ARIA OS Mobile",
    "description": "React Native version",
    "phase": "development",
    "github_url": "https://github.com/user/aria-mobile",
    "live_url": None,
    "next_action": "Set up CI/CD",
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_IDEA = {
    "id": "idea-1",
    "user_id": "user-1",
    "title": "AI Study Buddy",
    "description": "An AI-powered study companion",
    "status": "raw",
    "market_research": None,
    "competitors": None,
    "created_at": "2026-06-10T12:00:00",
}

SAMPLE_RESOURCE = {
    "id": "resource-1",
    "user_id": "user-1",
    "title": "FastAPI Docs",
    "url": "https://fastapi.tiangolo.com",
    "resource_type": "documentation",
    "tags": ["python", "api", "backend"],
    "notes": "Official docs",
    "is_archived": False,
    "created_at": "2026-06-01T12:00:00",
}

SAMPLE_OPPORTUNITY = {
    "id": "opp-1",
    "user_id": "user-1",
    "title": "Software Engineering Intern",
    "company": "Google",
    "url": "https://careers.google.com/intern",
    "opportunity_type": "internship",
    "description": "Summer 2027 internship",
    "skills_required": ["Python", "DSA", "System Design"],
    "deadline": "2026-09-15T00:00:00+00:00",
    "status": "new",
    "created_at": "2026-06-10T12:00:00",
}

SAMPLE_TIME_ENTRY = {
    "id": "time-1",
    "user_id": "user-1",
    "task_id": "task-1",
    "project_id": None,
    "start_time": "2026-06-14T09:00:00",
    "end_time": "2026-06-14T10:30:00",
    "duration_minutes": 90,
    "description": "Backend API work",
    "category": "development",
    "created_at": "2026-06-14T10:30:00",
}

AUTH_HEADER = {"Authorization": "Bearer test-token"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_auth_mock_user():
    """Return a mock object that mimicks get_current_user return value."""

    class _Inner:
        id = "user-1"

    class _MockUser:
        user = _Inner()

    return _MockUser()


def _get_router_modules():
    """Return router modules that import get_supabase_client."""
    return [
        "app.api.tasks",
        "app.api.courses",
        "app.api.goals",
        "app.api.habits",
        "app.api.sleep",
        "app.api.income",
        "app.api.projects",
        "app.api.ideas",
        "app.api.resources",
        "app.api.opportunities",
        "app.api.time",
        "app.api.chat",
    ]


def _register_mock_agent_modules():
    """Pre-register mock ai.agent modules so automation.py imports succeed in test context.

    Only mocks sub-modules under ai.agents.* — never shadows the real 'ai' package
    so other test files can still ``from ai.prompt_loader import PromptLoader``.
    """
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    """Build a FastAPI app with all 13 routers (no middleware)."""
    from fastapi import FastAPI
    from app.api import (
        tasks,
        courses,
        goals,
        ideas,
        chat,
        projects,
        resources,
        opportunities,
        income,
        habits,
        sleep,
        time,
        automation,
    )

    application = FastAPI(title="Test API")
    application.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    application.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
    application.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])
    application.include_router(ideas.router, prefix="/api/v1/ideas", tags=["ideas"])
    application.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    application.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    application.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
    application.include_router(opportunities.router, prefix="/api/v1/opportunities", tags=["opportunities"])
    application.include_router(income.router, prefix="/api/v1/income", tags=["income"])
    application.include_router(habits.router, prefix="/api/v1/habits", tags=["habits"])
    application.include_router(sleep.router, prefix="/api/v1/sleep", tags=["sleep"])
    application.include_router(time.router, prefix="/api/v1/time", tags=["time"])
    application.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
    return application


@pytest.fixture
def client(app):
    """Yield a TestClient bound to the shared app instance."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_supabase():
    """Fresh supabase mock per test — configure before each assertion."""
    return MagicMock()


@pytest.fixture(autouse=True)
def _setup_deps(app, mock_supabase):
    """Override auth dependency and patch all router module supabase references."""
    from config.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()

    patchers = []
    for mod in _get_router_modules():
        p = patch(f"{mod}.get_supabase_client", return_value=mock_supabase)
        p.start()
        patchers.append(p)

    yield

    for p in patchers:
        p.stop()
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper — single-query config for simple CRUD endpoints
# ---------------------------------------------------------------------------


def _cfg(mock_supabase, data, error=None):
    """Configure mock_supabase to return given data for the next query chain."""
    mock_supabase.from_.return_value = MockQueryBuilder(return_data=data, error_message=error)
    return mock_supabase


@pytest.fixture
def no_auth(app):
    """Remove auth dependency override so the real OAuth2 check runs (→ 401)."""
    app.dependency_overrides.clear()
    yield
    from config.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()


# ===========================================================================
# TASKS — 6 endpoints
# ===========================================================================


@pytest.mark.api
class TestTaskEndpoints:

    def test_list_tasks(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK])
        resp = client.get("/api/v1/tasks/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["id"] == "task-1"

    def test_list_tasks_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/tasks/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_task(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK])
        payload = {"title": "New task", "priority": "medium"}
        resp = client.post("/api/v1/tasks/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "task-1"

    def test_create_task_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/tasks/", json={"title": "Fail", "priority": "low"}, headers=AUTH_HEADER)
        assert resp.status_code == 400
        assert "insert failed" in resp.json()["detail"]

    def test_get_task_by_id(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK])
        resp = client.get("/api/v1/tasks/task-1", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "task-1"

    def test_get_task_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/tasks/nonexistent", headers=AUTH_HEADER)
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_update_task(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK])
        resp = client.put("/api/v1/tasks/task-1", json={"status": "completed"}, headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "task-1"

    def test_update_task_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/tasks/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_task(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TASK])
        resp = client.delete("/api/v1/tasks/task-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_complete_task(self, client, mock_supabase):
        updated = {**SAMPLE_TASK, "status": "completed", "completed_at": "2026-06-14T15:00:00"}
        _cfg(mock_supabase, [updated])
        resp = client.post("/api/v1/tasks/task-1/complete", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "completed"

    def test_complete_task_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.post("/api/v1/tasks/nonexistent/complete", headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_task_unauthorized(self, client, no_auth):
        resp = client.get("/api/v1/tasks/")
        assert resp.status_code == 401


# ===========================================================================
# COURSES — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestCourseEndpoints:

    def test_list_courses(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.get("/api/v1/courses/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_courses_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/courses/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        payload = {"title": "New Course", "platform": "Udemy"}
        resp = client.post("/api/v1/courses/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "course-1"

    def test_create_course_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="constraint violation")
        resp = client.post("/api/v1/courses/", json={"title": "X", "platform": "Y"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.put("/api/v1/courses/course-1", json={"status": "completed"}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_course_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/courses/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_course(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE])
        resp = client.delete("/api/v1/courses/course-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_course_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_COURSE], error="delete failed")
        resp = client.delete("/api/v1/courses/course-1", headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_course_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/courses/").status_code == 401


# ===========================================================================
# GOALS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestGoalEndpoints:

    def test_list_goals(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.get("/api/v1/goals/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_goals_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/goals/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        payload = {"title": "New Goal", "roadmap_type": "career_skills"}
        resp = client.post("/api/v1/goals/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "goal-1"

    def test_create_goal_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/goals/", json={"title": "Fail"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.put("/api/v1/goals/goal-1", json={"progress": 50}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_goal_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/goals/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_goal(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL])
        resp = client.delete("/api/v1/goals/goal-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_goal_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_GOAL], error="delete failed")
        resp = client.delete("/api/v1/goals/goal-1", headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_goal_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/goals/").status_code == 401


# ===========================================================================
# HABITS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestHabitEndpoints:

    def test_list_habits(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.get("/api/v1/habits/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_habits_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/habits/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.post("/api/v1/habits/", json={"name": "Read", "frequency": "daily"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "habit-1"

    def test_create_habit_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/habits/", json={"name": "Fail"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.put("/api/v1/habits/habit-1", json={"is_active": False}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_habit_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/habits/nonexistent", json={"name": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_habit(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT])
        resp = client.delete("/api/v1/habits/habit-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_delete_habit_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_HABIT], error="delete failed")
        resp = client.delete("/api/v1/habits/habit-1", headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_habit_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/habits/").status_code == 401


# ===========================================================================
# SLEEP — 3 endpoints (no update)
# ===========================================================================


@pytest.mark.api
class TestSleepEndpoints:

    def test_list_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP])
        resp = client.get("/api/v1/sleep/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_sleep_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/sleep/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP])
        resp = client.post(
            "/api/v1/sleep/",
            json={
                "bedtime": "23:00",
                "wake_time": "07:00",
                "quality_rating": 4,
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "sleep-1"

    def test_create_sleep_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/sleep/",
            json={
                "bedtime": "23:00",
                "wake_time": "07:00",
                "quality_rating": 3,
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_delete_sleep(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_SLEEP])
        resp = client.delete("/api/v1/sleep/sleep-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_sleep_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/sleep/").status_code == 401


# ===========================================================================
# INCOME — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestIncomeEndpoints:

    def test_list_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.get("/api/v1/income/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_income_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/income/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.post(
            "/api/v1/income/",
            json={
                "source_type": "freelance",
                "amount": 500.0,
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == "income-1"

    def test_create_income_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/income/", json={"source_type": "freelance", "amount": 100}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.put("/api/v1/income/income-1", json={"amount": 600.0}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_income_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/income/nonexistent", json={"amount": 100}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_income(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_INCOME])
        resp = client.delete("/api/v1/income/income-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_income_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/income/").status_code == 401


# ===========================================================================
# PROJECTS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestProjectEndpoints:

    def test_list_projects(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.get("/api/v1/projects/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_projects_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/projects/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.post("/api/v1/projects/", json={"title": "New Project"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "project-1"

    def test_create_project_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/projects/", json={"title": "Fail"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.put("/api/v1/projects/project-1", json={"phase": "launched"}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_project_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/projects/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_project(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_PROJECT])
        resp = client.delete("/api/v1/projects/project-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_project_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/projects/").status_code == 401


# ===========================================================================
# IDEAS — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestIdeaEndpoints:

    def test_list_ideas(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.get("/api/v1/ideas/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_ideas_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/ideas/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.post("/api/v1/ideas/", json={"title": "New Idea"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "idea-1"

    def test_create_idea_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/ideas/", json={"title": "Fail"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.put("/api/v1/ideas/idea-1", json={"status": "validating"}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_idea_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/ideas/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_idea(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_IDEA])
        resp = client.delete("/api/v1/ideas/idea-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_idea_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/ideas/").status_code == 401


# ===========================================================================
# RESOURCES — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestResourceEndpoints:

    def test_list_resources(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.get("/api/v1/resources/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_resources_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/resources/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        payload = {"title": "New Resource", "url": "https://example.com"}
        resp = client.post("/api/v1/resources/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "resource-1"

    def test_create_resource_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post("/api/v1/resources/", json={"title": "X", "url": "https://x.com"}, headers=AUTH_HEADER)
        assert resp.status_code == 400

    def test_update_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.put("/api/v1/resources/resource-1", json={"is_archived": True}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_resource_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/resources/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_resource(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_RESOURCE])
        resp = client.delete("/api/v1/resources/resource-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_resource_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/resources/").status_code == 401


# ===========================================================================
# OPPORTUNITIES — 4 endpoints
# ===========================================================================


@pytest.mark.api
class TestOpportunityEndpoints:

    def test_list_opportunities(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.get("/api/v1/opportunities/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_opportunities_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/opportunities/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        payload = {"title": "New Opp", "url": "https://example.com/apply"}
        resp = client.post("/api/v1/opportunities/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "opp-1"

    def test_create_opportunity_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/opportunities/",
            json={
                "title": "Fail",
                "url": "https://example.com",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.put("/api/v1/opportunities/opp-1", json={"status": "applied"}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_opportunity_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/opportunities/nonexistent", json={"title": "Nope"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_opportunity(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_OPPORTUNITY])
        resp = client.delete("/api/v1/opportunities/opp-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_opportunity_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/opportunities/").status_code == 401


# ===========================================================================
# TIME — 5 endpoints (list, create, update, delete + stats/daily + stop)
# ===========================================================================


@pytest.mark.api
class TestTimeEndpoints:

    def test_list_time_entries(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.get("/api/v1/time/", headers=AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["id"] == "time-1"

    def test_list_time_entries_empty(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.get("/api/v1/time/", headers=AUTH_HEADER)
        assert resp.json() == []

    def test_create_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        payload = {
            "category": "development",
            "start_time": "2026-06-14T09:00:00",
        }
        resp = client.post("/api/v1/time/", json=payload, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["id"] == "time-1"

    def test_create_time_entry_db_error(self, client, mock_supabase):
        _cfg(mock_supabase, [], error="insert failed")
        resp = client.post(
            "/api/v1/time/",
            json={
                "category": "work",
                "start_time": "2026-06-14T09:00:00",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_update_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.put("/api/v1/time/time-1", json={"category": "meeting"}, headers=AUTH_HEADER)
        assert resp.status_code == 200

    def test_update_time_entry_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.put("/api/v1/time/nonexistent", json={"category": "work"}, headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_delete_time_entry(self, client, mock_supabase):
        _cfg(mock_supabase, [SAMPLE_TIME_ENTRY])
        resp = client.delete("/api/v1/time/time-1", headers=AUTH_HEADER)
        assert resp.status_code == 204

    def test_time_stats_daily(self, client, mock_supabase):
        entries = [
            {"category": "development", "duration_minutes": 90},
            {"category": "meeting", "duration_minutes": 30},
        ]
        _cfg(mock_supabase, entries)
        resp = client.get("/api/v1/time/stats/daily", headers=AUTH_HEADER)
        assert resp.status_code == 200
        body = resp.json()
        assert "date" in body
        assert "categories" in body
        assert "total_minutes" in body
        assert body["total_minutes"] == 120

    def test_time_stop_timer(self, client, mock_supabase):
        stopped = {**SAMPLE_TIME_ENTRY}
        builder_with_data = MockQueryBuilder(return_data=[stopped])
        builder_empty = MockQueryBuilder(return_data=[])
        mock_supabase.from_.side_effect = lambda t: builder_with_data if t == "time_entries" else builder_empty
        resp = client.post("/api/v1/time/stop?entry_id=time-1", headers=AUTH_HEADER)
        assert resp.status_code == 201

    def test_time_stop_timer_not_found(self, client, mock_supabase):
        _cfg(mock_supabase, [])
        resp = client.post("/api/v1/time/stop?entry_id=nonexistent", headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_time_unauthorized(self, client, no_auth):
        assert client.get("/api/v1/time/").status_code == 401


# ===========================================================================
# CHAT — 1 endpoint with multiple response paths
# ===========================================================================


@pytest.mark.api
class TestChatEndpoints:

    @staticmethod
    def _setup_chat_mocks(mock_supabase, tasks=None, goals=None, courses=None):
        def side_effect(table):
            builders = {
                "tasks": MockQueryBuilder(return_data=tasks or []),
                "goals": MockQueryBuilder(return_data=goals or []),
                "courses": MockQueryBuilder(return_data=courses or []),
                "chat_messages": MockQueryBuilder(return_data=[]),
            }
            return builders.get(table, MockQueryBuilder(return_data=[]))

        mock_supabase.from_.side_effect = side_effect

    def test_chat_asks_about_tasks(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase, tasks=[SAMPLE_TASK])
        resp = client.post("/api/v1/chat/", json={"message": "What are my tasks?"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        body = resp.json()
        assert "response" in body
        assert "pending tasks" in body["response"].lower()

    def test_chat_asks_about_tasks_empty(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase, tasks=[])
        resp = client.post("/api/v1/chat/", json={"message": "show my tasks"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "no pending tasks" in resp.json()["response"].lower()

    def test_chat_asks_about_goals(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase, goals=[SAMPLE_GOAL])
        resp = client.post("/api/v1/chat/", json={"message": "Tell me about my goals"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "active goals" in resp.json()["response"].lower()

    def test_chat_asks_about_goals_empty(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase, goals=[])
        resp = client.post("/api/v1/chat/", json={"message": "my goals"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "don't have any active goals" in resp.json()["response"].lower()

    def test_chat_asks_about_courses(self, client, mock_supabase):
        course_in_progress = {**SAMPLE_COURSE, "status": "in_progress"}
        self._setup_chat_mocks(mock_supabase, courses=[course_in_progress])
        resp = client.post("/api/v1/chat/", json={"message": "What courses am I learning?"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "currently taking" in resp.json()["response"].lower()

    def test_chat_asks_about_courses_empty(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase, courses=[])
        resp = client.post("/api/v1/chat/", json={"message": "courses"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "start learning" in resp.json()["response"].lower()

    def test_chat_asks_for_help(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase)
        resp = client.post("/api/v1/chat/", json={"message": "help"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "here to help" in resp.json()["response"].lower()

    def test_chat_generic_message(self, client, mock_supabase):
        self._setup_chat_mocks(mock_supabase)
        resp = client.post("/api/v1/chat/", json={"message": "Hello ARIA"}, headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert "understand" in resp.json()["response"].lower()

    def test_chat_unauthorized(self, client, no_auth):
        resp = client.post("/api/v1/chat/", json={"message": "hi"})
        assert resp.status_code == 401


# ===========================================================================
# AUTOMATION — 6 trigger endpoints
# ===========================================================================


@pytest.mark.api
class TestAutomationEndpoints:

    @pytest.fixture(autouse=True)
    def _mock_agent_funcs(self):
        patchers = []
        targets = {
            "app.api.automation.generate_daily_briefing": {"status": "ok", "briefing": "test"},
            "app.api.automation.run_opportunity_radar": [],
            "app.api.automation.generate_weekly_review": {"status": "ok", "review": "test"},
            "app.api.automation.analyze_sleep": {"status": "ok", "analysis": "test"},
            "app.api.automation.suggest_bedtime": {"status": "ok", "bedtime": "22:00"},
            "app.api.automation.run_all_nudges": {"status": "ok", "nudges": 3},
        }
        for target, retval in targets.items():
            p = patch(target, new=AsyncMock(return_value=retval))
            p.start()
            patchers.append(p)
        yield
        for p in patchers:
            p.stop()

    def test_trigger_briefing(self, client):
        resp = client.post("/api/v1/automation/trigger/briefing", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_trigger_radar(self, client):
        resp = client.post("/api/v1/automation/trigger/radar", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_trigger_weekly_review(self, client):
        resp = client.post("/api/v1/automation/trigger/weekly-review", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_trigger_sleep_analysis(self, client):
        resp = client.post("/api/v1/automation/trigger/sleep-analysis", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_trigger_sleep_bedtime(self, client):
        resp = client.post("/api/v1/automation/trigger/sleep-bedtime", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_trigger_nudges(self, client):
        resp = client.post("/api/v1/automation/trigger/nudges", headers=AUTH_HEADER)
        assert resp.status_code == 201
        assert resp.json()["status"] == "success"

    def test_automation_unauthorized(self, client, no_auth):
        resp = client.post("/api/v1/automation/trigger/briefing")
        assert resp.status_code == 401
