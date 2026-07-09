"""Tests for /api/v1/reviews/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_user():
    return MagicMock(user=MagicMock(id="test-user"))


@pytest.mark.api
class TestReviewsRoutes:
    """Test CRUD operations for weekly reviews."""

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_reviews_success(self, mock_supabase):
        """GET / should return paginated list."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "week_start": "2026-06-15", "title": "W25 Review"}]
        )

        from app.api.reviews import list_reviews

        result = await list_reviews(current_user=current_user, limit=20, offset=0)
        assert len(result) == 1
        assert result[0]["title"] == "W25 Review"

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_list_reviews_empty(self, mock_supabase):
        """GET / should return empty list when no data."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.reviews import list_reviews

        result = await list_reviews(current_user=current_user, limit=20, offset=0)
        assert result == []

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_latest_review_found(self, mock_supabase):
        """GET /latest should return the most recent review."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "week_start": "2026-06-15"}]
        )

        from app.api.reviews import get_latest_review

        result = await get_latest_review(current_user=current_user)
        assert result["id"] == "1"

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_latest_review_not_found(self, mock_supabase):
        """GET /latest should return None when no reviews exist."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        from app.api.reviews import get_latest_review

        result = await get_latest_review(current_user=current_user)
        assert result is None

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_review_by_id(self, mock_supabase):
        """GET /{id} should return a review by ID."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[{"id": "review-1", "week_start": "2026-06-15"}])
        )

        from app.api.reviews import get_review

        result = await get_review("review-1", current_user=current_user)
        assert result["id"] == "review-1"

    @patch("app.api.reviews.get_supabase_client")
    @pytest.mark.asyncio
    async def test_get_review_not_found(self, mock_supabase):
        """GET /{id} should raise 404 when review not found."""
        current_user = _mock_user()
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[])
        )

        from app.api.reviews import get_review
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_review("missing-id", current_user=current_user)
        assert exc.value.status_code == 404
