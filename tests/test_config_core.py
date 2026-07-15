"""Tests for config core modules: api_key_auth, auth, supabase, config."""

import pytest
import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock

# ===========================================================================
# api_key_auth — authenticate_with_api_key
# ===========================================================================


@pytest.mark.asyncio
class TestApiKeyAuth:

    FAKE_KEY = "sb_test_key_12345"
    FAKE_HASH = hashlib.sha256(FAKE_KEY.encode()).hexdigest()
    USER_ID = "user-1"
    FUTURE = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    PAST = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    def _mock_supabase(self, api_key_row=None, user_row=None):
        """Build a mock supabase client that returns given data per table."""
        supabase = MagicMock()

        def from_side_effect(table):
            b = MagicMock()
            if table == "api_keys":
                b.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[api_key_row] if api_key_row else []
                )
            elif table == "users":
                b.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[user_row] if user_row else []
                )
            else:
                b.select.return_value.execute.return_value = MagicMock(data=[])
            return b

        supabase.from_ = from_side_effect
        return supabase

    async def test_authenticate_with_valid_key(self):
        key_row = {
            "user_id": self.USER_ID,
            "expires_at": self.FUTURE,
            "is_active": True,
        }
        # The source code does user.id = user_id on the result, so mock must
        # return an object that supports attribute assignment, not a raw dict.
        from types import SimpleNamespace

        mock_user_obj = SimpleNamespace(id="old-id", email="test@example.com")
        supabase = self._mock_supabase(api_key_row=key_row, user_row=mock_user_obj)

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key

            user = await authenticate_with_api_key(self.FAKE_KEY)
            assert user.id == self.USER_ID
            assert user.email == "test@example.com"

    async def test_authenticate_with_invalid_key_raises_401(self):
        supabase = self._mock_supabase(api_key_row=None)

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc:
                await authenticate_with_api_key("nonexistent_key")
            assert exc.value.status_code == 401
            assert "Invalid API key" in exc.value.detail

    async def test_authenticate_with_deactivated_key_raises_401(self):
        key_row = {
            "user_id": self.USER_ID,
            "expires_at": self.FUTURE,
            "is_active": False,
        }
        supabase = self._mock_supabase(api_key_row=key_row)

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc:
                await authenticate_with_api_key(self.FAKE_KEY)
            assert exc.value.status_code == 401
            assert "deactivated" in exc.value.detail

    async def test_authenticate_with_expired_key_raises_401(self):
        key_row = {
            "user_id": self.USER_ID,
            "expires_at": self.PAST,
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc:
                await authenticate_with_api_key(self.FAKE_KEY)
            assert exc.value.status_code == 401
            assert "expired" in exc.value.detail

    async def test_authenticate_key_user_not_found_raises_401(self):
        key_row = {
            "user_id": self.USER_ID,
            "expires_at": self.FUTURE,
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row, user_row=None)

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc:
                await authenticate_with_api_key(self.FAKE_KEY)
            assert exc.value.status_code == 401
            assert "User not found" in exc.value.detail

    async def test_authenticate_unexpected_error_raises_500(self):
        supabase = MagicMock()
        supabase.from_.side_effect = Exception("DB connection failed")

        with patch("config.core.api_key_auth.get_supabase_client", return_value=supabase):
            from config.core.api_key_auth import authenticate_with_api_key
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc:
                await authenticate_with_api_key(self.FAKE_KEY)
            assert exc.value.status_code == 500


# ===========================================================================
# auth — get_current_user, create_access_token, rotate_api_key
# ===========================================================================


class TestAuthCore:

    USER_ID = "user-1"

    @pytest.mark.asyncio
    async def test_get_current_user_with_jwt(self):
        import jwt as pyjwt
        from config.core.config import settings

        token = pyjwt.encode(
            {"sub": self.USER_ID, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        mock_user = MagicMock()
        mock_user.id = self.USER_ID

        with patch("config.core.auth._verify_supabase_token", new=AsyncMock(return_value=mock_user)):
            from config.core.auth import get_current_user

            result = await get_current_user(token)
            assert result.id == self.USER_ID

    @pytest.mark.asyncio
    async def test_get_current_user_with_api_key(self):
        """Test that a token starting with 'sb_' routes through authenticate_with_api_key."""
        from config.core.auth import get_current_user

        mock_user = MagicMock()
        mock_user.id = self.USER_ID

        with patch(
            "config.core.api_key_auth.authenticate_with_api_key",
            new=AsyncMock(return_value=mock_user),
        ):
            result = await get_current_user("sb_test_api_key_xyz")
            assert result.id == self.USER_ID

    @pytest.mark.asyncio
    async def test_get_current_user_with_api_key_failure_raises_401(self):
        """Test that when authenticate_with_api_key raises HTTPException,
        get_current_user raises credentials_exception (401)."""
        from config.core.auth import get_current_user
        from fastapi import HTTPException

        with patch(
            "config.core.api_key_auth.authenticate_with_api_key",
            new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid")),
        ):
            with pytest.raises(HTTPException) as exc:
                await get_current_user("sb_bad_key")
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_jwt_raises_401(self):
        from config.core.auth import get_current_user
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_current_user("invalid.jwt.token")
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub_in_jwt_raises_401(self):
        import jwt as pyjwt
        from config.core.config import settings

        token = pyjwt.encode(
            {"not_sub": "value", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        from config.core.auth import get_current_user
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await get_current_user(token)
        assert exc.value.status_code == 401

    def test_create_access_token_with_default_expiry(self):
        from config.core.auth import create_access_token
        import jwt as pyjwt
        from config.core.config import settings

        token = create_access_token({"sub": self.USER_ID})
        decoded = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert decoded["sub"] == self.USER_ID
        assert "exp" in decoded

    def test_create_access_token_with_custom_expiry(self):
        from config.core.auth import create_access_token
        import jwt as pyjwt
        from config.core.config import settings

        delta = timedelta(minutes=5)
        token = create_access_token({"sub": self.USER_ID, "role": "admin"}, expires_delta=delta)
        decoded = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert decoded["sub"] == self.USER_ID
        assert decoded["role"] == "admin"

    def test_create_access_token_empty_data(self):
        from config.core.auth import create_access_token
        import jwt as pyjwt
        from config.core.config import settings

        token = create_access_token({})
        decoded = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert "exp" in decoded

    def test_rotate_api_key_returns_new_key_and_expiry(self):
        from config.core.auth import rotate_api_key
        from unittest.mock import MagicMock, patch

        mock_supabase = MagicMock()
        with patch("config.core.supabase.get_supabase_client", return_value=mock_supabase):
            result = rotate_api_key("user-1")
        assert result["new_key"].startswith("sb_")
        assert "old_key_expires_at" in result
        assert isinstance(result["old_key_expires_at"], str)

    def test_rotate_api_key_caches_new_key(self):
        from config.core.auth import rotated_keys_cache, rotate_api_key
        from unittest.mock import MagicMock, patch

        rotated_keys_cache.clear()
        mock_supabase = MagicMock()
        with patch("config.core.supabase.get_supabase_client", return_value=mock_supabase):
            result = rotate_api_key("user-1")
        key_hash = hashlib.sha256(result["new_key"].encode()).hexdigest()
        cache_key = f"rotated:{key_hash}"
        assert cache_key in rotated_keys_cache
        assert rotated_keys_cache[cache_key]["user_id"] == "user-1"

    def test_rotate_api_key_cache_expires_in_24h(self):
        from config.core.auth import rotated_keys_cache, rotate_api_key
        from unittest.mock import MagicMock, patch

        rotated_keys_cache.clear()
        mock_supabase = MagicMock()
        with patch("config.core.supabase.get_supabase_client", return_value=mock_supabase):
            result = rotate_api_key("user-1")
        key_hash = hashlib.sha256(result["new_key"].encode()).hexdigest()
        cache_key = f"rotated:{key_hash}"
        expires = rotated_keys_cache[cache_key]["expires"]
        remaining = (expires - datetime.now(timezone.utc)).total_seconds()
        assert 23 * 3600 < remaining < 25 * 3600


# ===========================================================================
# supabase — get_supabase_client
# ===========================================================================


class TestSupabaseClient:

    def test_get_supabase_client_returns_client(self):
        """get_supabase_client should create and return a supabase client."""
        with (
            patch("config.core.supabase.create_client") as mock_create,
            patch("config.core.supabase.settings") as mock_settings,
        ):
            mock_settings.supabase_url = "https://test.supabase.co"
            mock_settings.supabase_key = "test-key"
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            import config.core.supabase as sb_mod

            sb_mod._supabase_client = None

            from config.core.supabase import get_supabase_client

            client = get_supabase_client()
            assert client is mock_client
            mock_create.assert_called_once()

    def test_get_supabase_client_caches_singleton(self):
        """get_supabase_client should return the same instance on second call."""
        with patch("config.core.supabase.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            import config.core.supabase as sb_mod

            sb_mod._supabase_client = None
            sb_mod._supabase_client = mock_client

            from config.core.supabase import get_supabase_client

            client = get_supabase_client()
            assert client is mock_client
            # create_client should NOT be called again since singleton exists
            mock_create.assert_not_called()

    def test_get_supabase_client_raises_on_missing_config(self):
        """get_supabase_client should raise ValueError when URL or key is empty."""
        with patch("config.core.supabase.settings") as mock_settings:
            mock_settings.supabase_url = ""
            mock_settings.supabase_key = ""

            import config.core.supabase as sb_mod

            sb_mod._supabase_client = None

            from config.core.supabase import get_supabase_client

            with pytest.raises(ValueError, match="Supabase URL and key must be configured"):
                get_supabase_client()

    def test_get_supabase_client_raises_on_missing_url(self):
        with patch("config.core.supabase.settings") as mock_settings:
            mock_settings.supabase_url = ""
            mock_settings.supabase_key = "valid-key"

            import config.core.supabase as sb_mod

            sb_mod._supabase_client = None

            from config.core.supabase import get_supabase_client

            with pytest.raises(ValueError):
                get_supabase_client()


# ===========================================================================
# config — Settings
# ===========================================================================


class TestSettings:

    def test_settings_defaults(self):
        """Settings should have sensible defaults."""
        from config.core.config import Settings

        s = Settings()
        assert s.app_name == "Second Brain OS"
        assert s.app_version == "1.0.0"
        assert s.environment == "development"
        assert s.debug is True
        assert s.log_level == "INFO"
        assert s.jwt_algorithm == "HS256"
        assert s.use_local_ai is True
        assert s.ollama_model == "mistral"
        assert s.ollama_base_url == "http://localhost:11434"
        assert s.circuit_breaker_threshold == 5
        assert s.rate_limit_max == 100

    def test_settings_supabase_empty_by_default(self):
        from config.core.config import Settings

        s = Settings()
        assert s.supabase_url == ""
        assert s.supabase_key == ""

    def test_settings_optional_fields_default_to_none(self):
        from config.core.config import Settings

        s = Settings()
        assert s.claude_api_key is None
        assert s.resend_api_key is None
        assert s.sentry_dsn is None
        assert s.posthog_api_key is None
        assert s.brave_api_key is None

    def test_settings_override_with_env_vars(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "Override OS")
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key-123")
        monkeypatch.setenv("JWT_SECRET", "custom-secret")
        monkeypatch.setenv("OLLAMA_MODEL", "llama3")
        monkeypatch.setenv("USE_LOCAL_AI", "false")
        monkeypatch.setenv("RATE_LIMIT_MAX", "200")

        from config.core.config import Settings

        s = Settings()
        assert s.app_name == "Override OS"
        assert s.environment == "production"
        assert s.debug is False
        assert s.supabase_url == "https://test.supabase.co"
        assert s.supabase_key == "test-key-123"
        assert s.jwt_secret == "custom-secret"
        assert s.ollama_model == "llama3"
        assert s.use_local_ai is False
        assert s.rate_limit_max == 200

    def test_settings_case_insensitive_env_vars(self, monkeypatch):
        monkeypatch.setenv("app_name", "Lowercase App")
        monkeypatch.setenv("jwt_algorithm", "HS512")

        from config.core.config import Settings

        s = Settings()
        assert s.app_name == "Lowercase App"
        assert s.jwt_algorithm == "HS512"

    def test_settings_singleton_importable(self):
        from config.core.config import settings

        assert hasattr(settings, "app_name")
        assert hasattr(settings, "jwt_secret")

    @pytest.mark.asyncio
    async def test_verify_supabase_token_calls_auth(self):
        from config.core.auth import _verify_supabase_token
        import hashlib

        cache_key = hashlib.md5(f"verify_token:('test-token',):{sorted([])}".encode()).hexdigest()
        from shared.utils.cache import cache

        await cache.delete(cache_key)

        mock_supabase = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user-1"
        mock_supabase.auth.get_user.return_value = mock_user
        with patch("config.core.supabase.get_supabase_client", return_value=mock_supabase):
            result = await _verify_supabase_token("test-token")
            assert result.id == "user-1"
            mock_supabase.auth.get_user.assert_called_once_with("test-token")


# ===========================================================================
# auth — refresh_jwt_token (100% coverage gap closure)
# ===========================================================================


class TestRefreshJwtToken:
    """Enterprise-grade tests for refresh_jwt_token (auth.py lines 97-118)."""

    def test_refresh_jwt_token_success(self):
        """Valid refresh token returns new access + refresh pair."""
        from config.core.auth import refresh_jwt_token
        import jwt as pyjwt
        from config.core.config import settings

        now = datetime.now(timezone.utc)
        refresh_token = pyjwt.encode(
            {"sub": "user-1", "type": "refresh", "exp": now + timedelta(days=30)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        result = refresh_jwt_token(refresh_token)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert isinstance(result["expires_in"], int)
        assert result["expires_in"] > 0

        decoded_access = pyjwt.decode(result["access_token"], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert decoded_access["sub"] == "user-1"
        assert decoded_access["type"] == "access"
        decoded_refresh = pyjwt.decode(
            result["refresh_token"], settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        assert decoded_refresh["sub"] == "user-1"
        assert decoded_refresh["type"] == "refresh"

    def test_refresh_jwt_token_missing_sub_returns_401(self):
        """Token without 'sub' claim raises HTTPException 401."""
        from config.core.auth import refresh_jwt_token
        from fastapi import HTTPException
        import jwt as pyjwt
        from config.core.config import settings

        now = datetime.now(timezone.utc)
        token = pyjwt.encode(
            {"type": "refresh", "exp": now + timedelta(days=30)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(HTTPException) as exc:
            refresh_jwt_token(token)
        assert exc.value.status_code == 401
        assert "Invalid refresh token" in exc.value.detail

    def test_refresh_jwt_token_wrong_type_returns_401(self):
        """Token with type != 'refresh' raises HTTPException 401."""
        from config.core.auth import refresh_jwt_token
        from fastapi import HTTPException
        import jwt as pyjwt
        from config.core.config import settings

        now = datetime.now(timezone.utc)
        token = pyjwt.encode(
            {"sub": "user-1", "type": "access", "exp": now + timedelta(days=30)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(HTTPException) as exc:
            refresh_jwt_token(token)
        assert exc.value.status_code == 401
        assert "Invalid refresh token" in exc.value.detail

    def test_refresh_jwt_token_expired_returns_401(self):
        """Expired token raises HTTPException 401."""
        from config.core.auth import refresh_jwt_token
        from fastapi import HTTPException
        import jwt as pyjwt
        from config.core.config import settings

        past = datetime.now(timezone.utc) - timedelta(hours=1)
        token = pyjwt.encode(
            {"sub": "user-1", "type": "refresh", "exp": past},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(HTTPException) as exc:
            refresh_jwt_token(token)
        assert exc.value.status_code == 401
        assert "Invalid or expired refresh token" in exc.value.detail

    def test_refresh_jwt_token_invalid_signature_returns_401(self):
        """Token signed with wrong secret raises HTTPException 401."""
        from config.core.auth import refresh_jwt_token
        from fastapi import HTTPException
        import jwt as pyjwt

        now = datetime.now(timezone.utc)
        token = pyjwt.encode(
            {"sub": "user-1", "type": "refresh", "exp": now + timedelta(days=30)},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc:
            refresh_jwt_token(token)
        assert exc.value.status_code == 401
        assert "Invalid or expired refresh token" in exc.value.detail


# ===========================================================================
# api_gateway — ApiGateway (authenticate, check, audit)
# ===========================================================================


class TestApiGateway:
    """Enterprise API Gateway tests — key auth, rate limiting, audit logging."""

    FAKE_KEY = "sb_test_gateway_key_12345"
    USER_ID = "user-gateway-1"

    def _mock_supabase(self, api_key_row=None):
        supabase = MagicMock()

        def from_side_effect(table):
            b = MagicMock()
            if table == "api_keys":
                b.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                    data=[api_key_row] if api_key_row else []
                )
            else:
                b.select.return_value.execute.return_value = MagicMock(data=[])
            return b

        supabase.from_ = from_side_effect
        return supabase

    def _make_request(self, api_key=None, client_ip="127.0.0.1", method="GET", path="/api/v1/tasks"):
        from types import SimpleNamespace

        request = MagicMock()
        mock_client = MagicMock()
        mock_client.host = client_ip
        request.client = mock_client
        request.headers = {}
        if api_key:
            request.headers["X-API-Key"] = api_key
        request.state = SimpleNamespace()
        request.method = method
        request.url.path = path
        return request

    # ── authenticate ──────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_authenticate_valid_key(self):
        key_row = {
            "user_id": self.USER_ID,
            "tier": "pro",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway

            gateway = ApiGateway()
            user_id, tier = await gateway.authenticate(self.FAKE_KEY)
            assert user_id == self.USER_ID
            assert tier == "pro"

    @pytest.mark.asyncio
    async def test_authenticate_invalid_key_raises_401(self):
        supabase = self._mock_supabase(api_key_row=None)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway
            from fastapi import HTTPException

            gateway = ApiGateway()
            with pytest.raises(HTTPException) as exc:
                await gateway.authenticate("nonexistent_key")
            assert exc.value.status_code == 401
            assert "Invalid" in exc.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_deactivated_key_raises_401(self):
        key_row = {
            "user_id": self.USER_ID,
            "tier": "free",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "is_active": False,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway
            from fastapi import HTTPException

            gateway = ApiGateway()
            with pytest.raises(HTTPException) as exc:
                await gateway.authenticate(self.FAKE_KEY)
            assert exc.value.status_code == 401
            assert "deactivated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_expired_key_raises_401(self):
        key_row = {
            "user_id": self.USER_ID,
            "tier": "free",
            "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway
            from fastapi import HTTPException

            gateway = ApiGateway()
            with pytest.raises(HTTPException) as exc:
                await gateway.authenticate(self.FAKE_KEY)
            assert exc.value.status_code == 401
            assert "expired" in exc.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_no_expiry_succeeds(self):
        """A key with expires_at=None should be valid."""
        key_row = {
            "user_id": self.USER_ID,
            "tier": "enterprise",
            "expires_at": None,
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway

            gateway = ApiGateway()
            user_id, tier = await gateway.authenticate(self.FAKE_KEY)
            assert user_id == self.USER_ID
            assert tier == "enterprise"

    # ── check ─────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_check_no_api_key_sets_internal_tier(self):
        request = self._make_request(api_key=None)
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        await gateway.check(request, "items")
        assert request.state.tier == "internal"
        assert request.state.rate_limit_remaining >= 0

    @pytest.mark.asyncio
    async def test_check_with_api_key(self):
        key_row = {
            "user_id": self.USER_ID,
            "tier": "pro",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        request = self._make_request(api_key=self.FAKE_KEY)
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            from config.core.api_gateway import ApiGateway

            gateway = ApiGateway()
            await gateway.check(request, "items")
            assert request.state.user_id == self.USER_ID
            assert request.state.tier == "pro"

    @pytest.mark.asyncio
    async def test_check_require_auth_missing_key_raises_401(self):
        request = self._make_request(api_key=None)
        from config.core.api_gateway import ApiGateway
        from fastapi import HTTPException

        gateway = ApiGateway()
        with pytest.raises(HTTPException) as exc:
            await gateway.check(request, "items", require_auth=True)
        assert exc.value.status_code == 401
        assert "Missing X-API-Key" in exc.value.detail

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self):
        """Free tier (10 req/min) is exhausted on the 11th call."""
        key_row = {
            "user_id": self.USER_ID,
            "tier": "free",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "is_active": True,
        }
        supabase = self._mock_supabase(api_key_row=key_row)
        request = self._make_request(api_key=self.FAKE_KEY, client_ip="rate-test-ip")
        from config.core.api_gateway import ApiGateway
        from fastapi import HTTPException

        gateway = ApiGateway()
        with patch("config.core.api_gateway.get_supabase_client", return_value=supabase):
            for _ in range(10):
                await gateway.check(request, "items")
            with pytest.raises(HTTPException) as exc:
                await gateway.check(request, "items")
            assert exc.value.status_code == 429
            assert "Rate limit exceeded" in exc.value.detail

    @pytest.mark.asyncio
    async def test_check_sets_rate_limit_remaining(self):
        request = self._make_request(api_key=None, client_ip="remaining-test")
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        await gateway.check(request, "items")
        assert request.state.rate_limit_remaining == 9999

    @pytest.mark.asyncio
    async def test_check_no_client_falls_back_to_unknown(self):
        """When request.client is None, falls back to 'unknown' IP."""
        request = self._make_request(api_key=None)
        request.client = None
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        await gateway.check(request, "items")
        assert request.state.tier == "internal"

    # ── audit ─────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_audit_mutation_logs(self):
        request = self._make_request(method="POST", path="/api/v1/tasks")
        request.state.user_id = self.USER_ID
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        with patch("config.core.api_gateway.log_audit", new=AsyncMock()) as mock_log:
            await gateway.audit(request, 201)
            mock_log.assert_awaited_once()
            _call = mock_log.await_args
            assert _call is not None
            _, kwargs = _call
            assert kwargs["user_id"] == self.USER_ID
            assert kwargs["resource"] == "tasks"

    @pytest.mark.asyncio
    async def test_audit_get_method_skips(self):
        request = self._make_request(method="GET", path="/api/v1/tasks")
        request.state.user_id = self.USER_ID
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        with patch("config.core.api_gateway.log_audit", new=AsyncMock()) as mock_log:
            await gateway.audit(request, 200)
            mock_log.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_audit_error_status_skips(self):
        request = self._make_request(method="POST", path="/api/v1/tasks")
        request.state.user_id = self.USER_ID
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        with patch("config.core.api_gateway.log_audit", new=AsyncMock()) as mock_log:
            await gateway.audit(request, 500)
            mock_log.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_audit_no_user_id_skips(self):
        request = self._make_request(method="POST", path="/api/v1/tasks")
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        with patch("config.core.api_gateway.log_audit", new=AsyncMock()) as mock_log:
            await gateway.audit(request, 201)
            mock_log.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_audit_extracts_resource_from_path(self):
        request = self._make_request(method="PUT", path="/api/v1/goals/g-42")
        request.state.user_id = self.USER_ID
        from config.core.api_gateway import ApiGateway

        gateway = ApiGateway()
        with patch("config.core.api_gateway.log_audit", new=AsyncMock()) as mock_log:
            await gateway.audit(request, 200)
            mock_log.assert_awaited_once()
            _call = mock_log.await_args
            assert _call is not None
            _, kwargs = _call
            assert kwargs["resource"] == "goals"

    # ── singleton ─────────────────────────────────────────────────────

    def test_gateway_singleton(self):
        from config.core.api_gateway import ApiGateway, gateway

        assert isinstance(gateway, ApiGateway)
        assert hasattr(gateway, "_requests")

    def test_tier_limits_attribute(self):
        from config.core.api_gateway import ApiGateway

        tiers = ApiGateway.TIERS
        assert tiers["free"]["max_requests"] == 10
        assert tiers["pro"]["max_requests"] == 100
        assert tiers["enterprise"]["max_requests"] == 1000
        assert tiers["internal"]["max_requests"] == 10000
