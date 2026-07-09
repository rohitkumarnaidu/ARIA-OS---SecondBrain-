"""Tests for /api/v1/roadmap/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_user():
    return MagicMock(user=MagicMock(id="test-user"))


@pytest.mark.api
class TestRoadmapRoutes:
    """Test CRUD operations for roadmap milestones."""

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_milestones_success(self, mock_supabase):
        """GET / should return paginated list."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "title": "Learn Rust", "category": "programming"}]
        )

        from app.api.roadmap import list_milestones

        result = await list_milestones(current_user=current_user, limit=50, offset=0)
        assert len(result) == 1
        assert result[0]["title"] == "Learn Rust"

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_milestones_empty(self, mock_supabase):
        """GET / should return empty list when no data."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.roadmap import list_milestones

        result = await list_milestones(current_user=current_user, limit=50, offset=0)
        assert result == []

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_milestone_success(self, mock_supabase):
        """GET /{id} should return a milestone by ID."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[{"id": "ms-1", "title": "Learn Docker", "category": "devops"}])
        )

        from app.api.roadmap import get_milestone

        result = await get_milestone("ms-1", current_user=current_user)
        assert result["id"] == "ms-1"

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_milestone_not_found(self, mock_supabase):
        """GET /{id} should raise 404 when milestone not found."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[])
        )

        from app.api.roadmap import get_milestone
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_milestone("missing-id", current_user=current_user)
        assert exc.value.status_code == 404

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_milestone_success(self, mock_supabase):
        """POST / should create a milestone."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "skill": "Kubernetes", "category": "devops", "user_id": "test-user"}], error=None
        )

        from app.api.roadmap import create_milestone
        from database.schemas.roadmap import RoadmapMilestoneCreate

        milestone = RoadmapMilestoneCreate(skill="Kubernetes", category="devops")
        result = await create_milestone(milestone, current_user=current_user)
        assert result["skill"] == "Kubernetes"

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_milestone_db_error(self, mock_supabase):
        """POST / should raise 400 on insert error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            error=MagicMock(message="Insert failed")
        )

        from app.api.roadmap import create_milestone
        from database.schemas.roadmap import RoadmapMilestoneCreate
        from fastapi import HTTPException

        milestone = RoadmapMilestoneCreate(skill="Fail", category="devops")
        with pytest.raises(HTTPException) as exc:
            await create_milestone(milestone, current_user=current_user)
        assert exc.value.status_code == 400

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_milestone_success(self, mock_supabase):
        """PUT /{id} should update a milestone."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[{"id": "ms-1", "skill": "Updated Skill"}], error=None)
        )

        from app.api.roadmap import update_milestone
        from database.schemas.roadmap import RoadmapMilestoneUpdate

        update = RoadmapMilestoneUpdate(skill="Updated Skill")
        result = await update_milestone("ms-1", update, current_user=current_user)
        assert result["skill"] == "Updated Skill"

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_milestone_not_found(self, mock_supabase):
        """PUT /{id} should raise 404 when milestone not found."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[], error=None)
        )

        from app.api.roadmap import update_milestone
        from database.schemas.roadmap import RoadmapMilestoneUpdate
        from fastapi import HTTPException

        update = RoadmapMilestoneUpdate(skill="Missing")
        with pytest.raises(HTTPException) as exc:
            await update_milestone("missing-id", update, current_user=current_user)
        assert exc.value.status_code == 404

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_milestone_db_error(self, mock_supabase):
        """PUT /{id} should raise 400 on update error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=MagicMock(message="Update failed"))
        )

        from app.api.roadmap import update_milestone
        from database.schemas.roadmap import RoadmapMilestoneUpdate
        from fastapi import HTTPException

        update = RoadmapMilestoneUpdate(skill="Fail")
        with pytest.raises(HTTPException) as exc:
            await update_milestone("ms-1", update, current_user=current_user)
        assert exc.value.status_code == 400

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_milestone_success(self, mock_supabase):
        """DELETE /{id} should return None."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=None)
        )

        from app.api.roadmap import delete_milestone

        result = await delete_milestone("ms-1", current_user=current_user)
        assert result is None

    @patch("app.api.roadmap.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_milestone_db_error(self, mock_supabase):
        """DELETE /{id} should raise 400 on delete error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=MagicMock(message="Delete failed"))
        )

        from app.api.roadmap import delete_milestone
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await delete_milestone("ms-1", current_user=current_user)
        assert exc.value.status_code == 400
