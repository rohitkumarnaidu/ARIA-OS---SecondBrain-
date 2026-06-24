"""Tests for /api/v1/briefings/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.api
class TestBriefingsRoutes:
    """Test daily briefing endpoints."""

    def _make_user(self):
        return MagicMock(user=MagicMock(id="test-user"))

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_briefings_success(self, mock_supabase, mock_auth):
        """GET / should return paginated briefings."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value\
            .order.return_value.range.return_value.execute.return_value = \
            MagicMock(data=[{"id": "1", "title": "Morning Briefing", "date": "2026-06-24"}])

        from app.api.briefings import list_briefings

        result = await list_briefings(limit=20, offset=0, current_user=mock_user)
        assert len(result) == 1
        assert result[0]["title"] == "Morning Briefing"

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_briefings_empty(self, mock_supabase, mock_auth):
        """GET / should return empty list when no data."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value\
            .order.return_value.range.return_value.execute.return_value = \
            MagicMock(data=[])

        from app.api.briefings import list_briefings

        result = await list_briefings(limit=20, offset=0, current_user=mock_user)
        assert result == []

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_today_briefing_found(self, mock_supabase, mock_auth):
        """GET /today should return today's briefing when it exists."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        mock_client.from_.return_value.select.return_value.eq.return_value\
            .eq.return_value.limit.return_value.execute.return_value = \
            MagicMock(data=[{"id": "1", "title": "Today", "date": "2026-06-24"}])

        from app.api.briefings import get_today_briefing

        result = await get_today_briefing(current_user=mock_user)
        assert result["title"] == "Today"

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_today_briefing_fallback_to_latest(self, mock_supabase, mock_auth):
        """GET /today should fallback to latest briefing when no today."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        # First query chain: from_().select().eq().eq().limit().execute() → empty
        mock_client.from_.return_value.select.return_value.eq.return_value\
            .eq.return_value.limit.return_value.execute.return_value = \
            MagicMock(data=[])

        # Second query chain: from_().select().eq().order().limit().execute() → latest
        mock_client.from_.return_value.select.return_value.eq.return_value\
            .order.return_value.limit.return_value.execute.return_value = \
            MagicMock(data=[{"id": "2", "title": "Latest", "date": "2026-06-23"}])

        from app.api.briefings import get_today_briefing

        result = await get_today_briefing(current_user=mock_user)
        assert result["title"] == "Latest"

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_today_briefing_none(self, mock_supabase, mock_auth):
        """GET /today should return None when no briefings exist."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        mock_client.from_.return_value.select.return_value.eq.return_value\
            .eq.return_value.limit.return_value.execute.return_value = \
            MagicMock(data=[])

        mock_client.from_.return_value.select.return_value.eq.return_value\
            .order.return_value.limit.return_value.execute.return_value = \
            MagicMock(data=[])

        from app.api.briefings import get_today_briefing

        result = await get_today_briefing(current_user=mock_user)
        assert result is None

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_briefing_found(self, mock_supabase, mock_auth):
        """GET /{id} should return a briefing by ID."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = \
            MagicMock(data=[{"id": "b1", "title": "Briefing 1", "date": "2026-06-24"}])

        from app.api.briefings import get_briefing

        result = await get_briefing("b1", current_user=mock_user)
        assert result["title"] == "Briefing 1"

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_briefing_not_found(self, mock_supabase, mock_auth):
        """GET /{id} should 404 when not found."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = \
            MagicMock(data=[])

        from app.api.briefings import get_briefing
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_briefing("nonexistent", current_user=mock_user)
        assert exc.value.status_code == 404

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_mark_briefing_read_success(self, mock_supabase, mock_auth):
        """PUT /{id}/read should mark as read."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = \
            MagicMock(error=None, data=[{"id": "b1", "read": True}])

        from app.api.briefings import mark_briefing_read

        result = await mark_briefing_read("b1", current_user=mock_user)
        assert result["read"] is True

    @patch("app.api.briefings.get_current_user")
    @patch("app.api.briefings.get_supabase_client")
    @pytest.mark.asyncio
    async def test_mark_briefing_read_not_found(self, mock_supabase, mock_auth):
        """PUT /{id}/read should 404 when briefing missing."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = \
            MagicMock(error=None, data=[])

        from app.api.briefings import mark_briefing_read
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await mark_briefing_read("nonexistent", current_user=mock_user)
        assert exc.value.status_code == 404
