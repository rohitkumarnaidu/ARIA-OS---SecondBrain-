"""Tests for /api/v1/data/ endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.api
class TestDataExportRoutes:
    """Test data export (GDPR) endpoints."""

    def _make_user(self):
        return MagicMock(user=MagicMock(id="test-user"))

    @patch("app.api.data_export.get_current_user")
    @patch("app.api.data_export.get_supabase_client")
    @pytest.mark.asyncio
    async def test_export_user_data_success(self, mock_supabase, mock_auth):
        """GET /export should return all user data."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"id": "1", "user_id": "test-user", "title": "Test " + table}]
            )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.data_export import export_user_data

        result = await export_user_data(current_user=mock_user)
        assert result.user_id == "test-user"
        assert result.table_count > 0
        assert result.record_count > 0
        assert "tasks" in result.data
        assert result.data["tasks"][0]["id"] == "1"

    @patch("app.api.data_export.get_current_user")
    @patch("app.api.data_export.get_supabase_client")
    @pytest.mark.asyncio
    async def test_export_user_data_skips_empty_tables(self, mock_supabase, mock_auth):
        """GET /export should skip tables with no data."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            m.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.data_export import export_user_data

        result = await export_user_data(current_user=mock_user)
        assert result.table_count == 0
        assert result.record_count == 0
        assert result.data == {}

    @patch("app.api.data_export.get_current_user")
    @patch("app.api.data_export.get_supabase_client")
    @pytest.mark.asyncio
    async def test_export_user_data_handles_table_exception(self, mock_supabase, mock_auth):
        """GET /export should skip tables that raise exceptions."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        call_count = 0

        def side_effect(table):
            nonlocal call_count
            call_count += 1
            m = MagicMock()
            if call_count == 1:
                m.select.return_value.eq.return_value.execute.side_effect = Exception("DB error")
            else:
                m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": "1", "user_id": "test-user"}]
                )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.data_export import export_user_data

        result = await export_user_data(current_user=mock_user)
        assert "tasks" not in result.data
        assert result.table_count >= 0
        assert result.record_count >= 0

    @patch("app.api.data_export.get_current_user")
    @patch("app.api.data_export.get_supabase_client")
    @pytest.mark.asyncio
    async def test_export_user_data_structure(self, mock_supabase, mock_auth):
        """GET /export response should have correct ExportResponse fields."""
        mock_user = self._make_user()
        mock_auth.return_value = mock_user
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        def side_effect(table):
            m = MagicMock()
            m.select.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"id": "1", "user_id": "test-user"}]
            )
            return m

        mock_client.from_ = MagicMock(side_effect=side_effect)

        from app.api.data_export import export_user_data

        result = await export_user_data(current_user=mock_user)
        assert result.user_id == "test-user"
        assert result.exported_at is not None
        assert isinstance(result.data, dict)
        assert isinstance(result.table_count, int)
        assert isinstance(result.record_count, int)
