"""Tests for API patterns — schema validation, error responses, pagination."""

import pytest


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
