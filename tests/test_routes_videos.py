"""Tests for /api/v1/videos/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_user():
    return MagicMock(user=MagicMock(id="test-user"))


@pytest.mark.api
class TestVideosRoutes:
    """Test CRUD operations for videos."""

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_videos_success(self, mock_supabase):
        """GET / should return paginated list."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "title": "FastAPI Tutorial", "url": "https://youtube.com/watch?v=abc"}]
        )

        from app.api.videos import list_videos

        result = await list_videos(current_user=current_user, limit=50, offset=0)
        assert len(result) == 1
        assert result[0]["title"] == "FastAPI Tutorial"

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_videos_empty(self, mock_supabase):
        """GET / should return empty list when no data."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.videos import list_videos

        result = await list_videos(current_user=current_user, limit=50, offset=0)
        assert result == []

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_video_success(self, mock_supabase):
        """POST / should create a video."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "title": "New Video", "user_id": "test-user"}], error=None
        )

        from app.api.videos import create_video
        from database.schemas.video import VideoCreate

        video = VideoCreate(url="https://youtube.com/watch?v=xyz", title="New Video")
        result = await create_video(video, current_user=current_user)
        assert result["title"] == "New Video"

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_create_video_error(self, mock_supabase):
        """POST / should raise 400 on insert error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value = MagicMock(
            error=MagicMock(message="Insert failed")
        )

        from app.api.videos import create_video
        from database.schemas.video import VideoCreate
        from fastapi import HTTPException

        video = VideoCreate(url="https://youtube.com/watch?v=xyz", title="Fail Video")
        with pytest.raises(HTTPException) as exc:
            await create_video(video, current_user=current_user)
        assert exc.value.status_code == 400

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_video_success(self, mock_supabase):
        """PUT /{id} should update a video."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[{"id": "vid-1", "title": "Updated Title"}], error=None)
        )

        from app.api.videos import update_video
        from database.schemas.video import VideoUpdate

        update = VideoUpdate(title="Updated Title")
        result = await update_video("vid-1", update, current_user=current_user)
        assert result["title"] == "Updated Title"

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_video_not_found(self, mock_supabase):
        """PUT /{id} should raise 404 when video not found."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[], error=None)
        )

        from app.api.videos import update_video
        from database.schemas.video import VideoUpdate
        from fastapi import HTTPException

        update = VideoUpdate(title="Missing")
        with pytest.raises(HTTPException) as exc:
            await update_video("missing-id", update, current_user=current_user)
        assert exc.value.status_code == 404

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_update_video_db_error(self, mock_supabase):
        """PUT /{id} should raise 400 on update error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=MagicMock(message="Update failed"))
        )

        from app.api.videos import update_video
        from database.schemas.video import VideoUpdate
        from fastapi import HTTPException

        update = VideoUpdate(title="Fail")
        with pytest.raises(HTTPException) as exc:
            await update_video("vid-1", update, current_user=current_user)
        assert exc.value.status_code == 400

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_video_success(self, mock_supabase):
        """DELETE /{id} should return None."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=None)
        )

        from app.api.videos import delete_video

        result = await delete_video("vid-1", current_user=current_user)
        assert result is None

    @patch("app.api.videos.get_supabase_client")
    @pytest.mark.asyncio
    async def test_delete_video_db_error(self, mock_supabase):
        """DELETE /{id} should raise 400 on delete error."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(error=MagicMock(message="Delete failed"))
        )

        from app.api.videos import delete_video
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await delete_video("vid-1", current_user=current_user)
        assert exc.value.status_code == 400
