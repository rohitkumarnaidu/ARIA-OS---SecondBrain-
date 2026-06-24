"""Tests for the skills API router — CRUD operations for skills categories, user skills, and evidence."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

_AUTH_HEADER = {"Authorization": "Bearer test-token"}
_TEST_USER_ID = "user-1"


def _make_auth_mock():
    class Inner:
        id = _TEST_USER_ID
    class MockUser:
        user = Inner()
    return MockUser()


class MockQueryBuilder:
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
    def or_(self, *args, **kwargs):
        return self
    def in_(self, col, vals):
        return self
    def text_search(self, col, q):
        return self
    def execute(self):
        r = MagicMock()
        r.data = self._return_data
        r.error = None
        return r
    def insert(self, data):
        r = MagicMock()
        r.execute.return_value = MagicMock(data=[{"id": "mock-id", **data}], error=None)
        return r
    def update(self, data):
        self._update_data = data
        return self
    def delete(self):
        return self


@pytest.fixture
def mock_supabase():
    with patch("apps.api.app.api.skills.get_supabase_client") as mock:
        client = MagicMock()
        client.from_.return_value = MockQueryBuilder(return_data=[{"id": "cat-1", "name": "Web Dev", "slug": "web-dev", "description": "", "sort_order": 0, "level": 0, "is_active": True, "metadata": {}, "created_at": 0, "updated_at": 0}])
        mock.return_value = client
        yield mock


@pytest.mark.asyncio
async def test_list_categories(mock_supabase):
    from apps.api.app.api.skills import list_categories
    result = await list_categories(current_user=_make_auth_mock())
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_skills(mock_supabase):
    from apps.api.app.api.skills import list_skills
    result = await list_skills(current_user=_make_auth_mock())
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_skill_not_found(mock_supabase):
    from apps.api.app.api.skills import get_skill
    from fastapi import HTTPException
    mock_supabase.return_value.from_.return_value.execute.return_value.data = []
    with pytest.raises(HTTPException) as exc:
        await get_skill("nonexistent", current_user=_make_auth_mock())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_user_skills(mock_supabase):
    from apps.api.app.api.skills import list_user_skills
    result = await list_user_skills(current_user=_make_auth_mock())
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_certifications(mock_supabase):
    from apps.api.app.api.skills import list_certifications
    result = await list_certifications(current_user=_make_auth_mock())
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_recommendations(mock_supabase):
    from apps.api.app.api.skills import list_recommendations
    result = await list_recommendations(current_user=_make_auth_mock())
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_log_activity(mock_supabase):
    from apps.api.app.api.skills import log_activity
    from database.schemas.skill import SkillActivityLogCreate
    act = SkillActivityLogCreate(user_id=_TEST_USER_ID, activity_type="skill_tree_viewed")
    result = await log_activity(act, current_user=_make_auth_mock())
    assert result is not None
