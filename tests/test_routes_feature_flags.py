"""Tests for /api/v1/feature-flags/ endpoints."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_flag():
    flag = MagicMock()
    flag.key = "test-flag"
    flag.enabled = True
    flag.rollout_percentage = 50
    flag.user_segments = ["beta"]
    flag.metadata = {"owner": "dev"}
    flag.updated_at = "2026-01-01T00:00:00Z"
    flag.to_dict.return_value = {
        "key": "test-flag",
        "enabled": True,
        "rollout_percentage": 50,
        "user_segments": ["beta"],
        "metadata": {"owner": "dev"},
        "updated_at": "2026-01-01T00:00:00Z",
    }
    return flag


@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.user.id = "test-user"
    return user


@pytest.fixture
def mock_response():
    from fastapi import Response
    return Response()


@pytest.mark.api
class TestFeatureFlagRoutes:
    """Test feature flag CRUD and evaluation endpoints."""

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_list_feature_flags_success(self, mock_flags, mock_flag, mock_current_user, mock_response):
        mock_flags.all_flags.return_value = {"test-flag": mock_flag}
        from app.api.feature_flags import list_feature_flags

        result = await list_feature_flags(response=mock_response, current_user=mock_current_user)
        assert result["data"][0]["key"] == "test-flag"
        assert result["data"][0]["enabled"] is True
        mock_flags.all_flags.assert_called_once()

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_list_feature_flags_empty(self, mock_flags, mock_current_user, mock_response):
        mock_flags.all_flags.return_value = {}
        from app.api.feature_flags import list_feature_flags

        result = await list_feature_flags(response=mock_response, current_user=mock_current_user)
        assert result["data"] == []

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_get_feature_flag_success(self, mock_flags, mock_flag, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = mock_flag
        from app.api.feature_flags import get_feature_flag

        result = await get_feature_flag(key="test-flag", response=mock_response, current_user=mock_current_user)
        assert result["key"] == "test-flag"
        mock_flags.get_flag.assert_called_once_with("test-flag")

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_get_feature_flag_not_found(self, mock_flags, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = None
        from app.api.feature_flags import get_feature_flag
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_feature_flag(key="nonexistent", response=mock_response, current_user=mock_current_user)
        assert exc.value.status_code == 404

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_evaluate_feature_flag(self, mock_flags, mock_current_user, mock_response):
        mock_flags.get.return_value = True
        mock_flags.get_variant.return_value = "A"
        from app.api.feature_flags import evaluate_feature_flag

        result = await evaluate_feature_flag(key="test-flag", response=mock_response, current_user=mock_current_user)
        assert result["enabled"] is True
        assert result["variant"] == "A"
        mock_flags.get.assert_called_once_with("test-flag", user_id="test-user", default=False)
        mock_flags.get_variant.assert_called_once_with("test-flag", user_id="test-user")

    @patch("app.api.feature_flags.FeatureFlag")
    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_create_feature_flag_success(self, mock_flags, mock_ff_class, mock_flag, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = None
        mock_ff_class.return_value = mock_flag
        from app.api.feature_flags import create_feature_flag
        from database.schemas.feature_flag import FeatureFlagCreate

        flag_data = FeatureFlagCreate(
            key="new-flag",
            enabled=True,
            rollout_percentage=100,
            user_segments=[],
            metadata={},
        )
        result = await create_feature_flag(flag_data=flag_data, response=mock_response, current_user=mock_current_user)
        assert result["key"] == "test-flag"
        mock_flags.set.assert_called_once_with("new-flag", mock_flag)

    @patch("app.api.feature_flags.FeatureFlag")
    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_create_feature_flag_conflict(self, mock_flags, mock_ff_class, mock_flag, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = mock_flag
        from app.api.feature_flags import create_feature_flag
        from database.schemas.feature_flag import FeatureFlagCreate
        from fastapi import HTTPException

        flag_data = FeatureFlagCreate(key="existing", enabled=True)
        with pytest.raises(HTTPException) as exc:
            await create_feature_flag(flag_data=flag_data, response=mock_response, current_user=mock_current_user)
        assert exc.value.status_code == 409

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_update_feature_flag_success(self, mock_flags, mock_flag, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = mock_flag
        from app.api.feature_flags import update_feature_flag
        from database.schemas.feature_flag import FeatureFlagUpdate

        flag_data = FeatureFlagUpdate(enabled=False)
        await update_feature_flag(
            key="test-flag",
            flag_data=flag_data,
            response=mock_response,
            current_user=mock_current_user,
        )
        assert mock_flag.enabled is False
        mock_flags.set.assert_called_once_with("test-flag", mock_flag)

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_update_feature_flag_all_fields(self, mock_flags, mock_flag, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = mock_flag
        from app.api.feature_flags import update_feature_flag
        from database.schemas.feature_flag import FeatureFlagUpdate

        flag_data = FeatureFlagUpdate(
            rollout_percentage=100,
            user_segments=["all"],
            metadata={"env": "prod"},
        )
        await update_feature_flag(
            key="test-flag",
            flag_data=flag_data,
            response=mock_response,
            current_user=mock_current_user,
        )
        assert mock_flag.rollout_percentage == 100
        assert mock_flag.user_segments == ["all"]
        assert mock_flag.metadata == {"env": "prod"}

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_update_feature_flag_not_found(self, mock_flags, mock_current_user, mock_response):
        mock_flags.get_flag.return_value = None
        from app.api.feature_flags import update_feature_flag
        from database.schemas.feature_flag import FeatureFlagUpdate
        from fastapi import HTTPException

        flag_data = FeatureFlagUpdate(enabled=False)
        with pytest.raises(HTTPException) as exc:
            await update_feature_flag(
                key="nonexistent",
                flag_data=flag_data,
                response=mock_response,
                current_user=mock_current_user,
            )
        assert exc.value.status_code == 404

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_delete_feature_flag_success(self, mock_flags, mock_current_user, mock_response):
        mock_flags.delete.return_value = True
        from app.api.feature_flags import delete_feature_flag

        result = await delete_feature_flag(key="test-flag", response=mock_response, current_user=mock_current_user)
        assert result is None
        mock_flags.delete.assert_called_once_with("test-flag")

    @patch("app.api.feature_flags.flags")
    @pytest.mark.asyncio
    async def test_delete_feature_flag_not_found(self, mock_flags, mock_current_user, mock_response):
        mock_flags.delete.return_value = False
        from app.api.feature_flags import delete_feature_flag
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await delete_feature_flag(key="nonexistent", response=mock_response, current_user=mock_current_user)
        assert exc.value.status_code == 404
