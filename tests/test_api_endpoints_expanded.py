"""Expanded API endpoint tests for uncovered modules: feature_flags and skills.

Feature flags use TestClient (in-memory store, no supabase).
Skills use direct async function calls (bypasses response_model validation
of 24 response schemas, focusing on route logic).
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


_AUTH_HEADER = {"Authorization": "Bearer test-token"}
_TEST_USER_ID = "user-1"


def _make_auth_mock_user():
    class _Inner:
        id = _TEST_USER_ID

    class _MockUser:
        user = _Inner()

    return _MockUser()


class MockQueryBuilder:
    """Fluent mock for supabase query builder (.select().eq().execute())."""

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

    def gte(self, col, val):
        return self

    def lte(self, col, val):
        return self

    def text_search(self, col, val):
        return self

    def lt(self, col, val):
        return self

    def or_(self, condition):
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


# ===========================================================================
# FEATURE FLAGS — 15 tests via TestClient
# ===========================================================================


@pytest.mark.api
class TestFeatureFlagEndpoints:
    """Feature flag CRUD + evaluation via TestClient."""

    def _mock_flag(self, key="test.feature", enabled=True, pct=100):
        from shared.utils.feature_flags import FeatureFlag

        return FeatureFlag(key=key, enabled=enabled, rollout_percentage=pct)

    def _make_app(self):
        app = FastAPI()
        from app.api.feature_flags import router
        from config.core.auth import get_current_user

        app.include_router(router, prefix="/api/v1/feature-flags", tags=["feature_flags"])
        app.dependency_overrides[get_current_user] = lambda: _make_auth_mock_user()
        return app

    def test_list_flags(self):
        app = self._make_app()
        flag = self._mock_flag()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.all_flags", return_value={"test.feature": flag}):
                resp = client.get("/api/v1/feature-flags/", headers=_AUTH_HEADER)
                assert resp.status_code == 200
                assert len(resp.json()["data"]) == 1

    def test_list_flags_empty(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.all_flags", return_value={}):
                resp = client.get("/api/v1/feature-flags/", headers=_AUTH_HEADER)
                assert resp.status_code == 200
                assert resp.json()["data"] == []

    def test_get_flag_found(self):
        app = self._make_app()
        flag = self._mock_flag()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {"test.feature": flag}):
                resp = client.get("/api/v1/feature-flags/test.feature", headers=_AUTH_HEADER)
                assert resp.status_code == 200
                assert resp.json()["key"] == "test.feature"

    def test_get_flag_not_found(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {}):
                resp = client.get("/api/v1/feature-flags/nonexistent", headers=_AUTH_HEADER)
                assert resp.status_code == 404

    def test_evaluate_flag_enabled(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.get", return_value=True), patch(
                "app.api.feature_flags.flags.get_variant", return_value=None
            ):
                resp = client.get("/api/v1/feature-flags/test.feature/evaluate", headers=_AUTH_HEADER)
                assert resp.status_code == 200
                assert resp.json()["enabled"] is True

    def test_evaluate_flag_disabled(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.get", return_value=False), patch(
                "app.api.feature_flags.flags.get_variant", return_value=None
            ):
                resp = client.get("/api/v1/feature-flags/disabled.flag/evaluate", headers=_AUTH_HEADER)
                assert resp.status_code == 200
                assert resp.json()["enabled"] is False

    def test_create_flag(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {}), patch(
                "app.api.feature_flags.flags.set"
            ) as mock_set:
                resp = client.post(
                    "/api/v1/feature-flags/",
                    json={"key": "new.flag", "enabled": True},
                    headers=_AUTH_HEADER,
                )
                assert resp.status_code == 201
                mock_set.assert_called_once()

    def test_create_flag_already_exists(self):
        app = self._make_app()
        flag = self._mock_flag("existing")
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {"existing": flag}):
                resp = client.post(
                    "/api/v1/feature-flags/",
                    json={"key": "existing", "enabled": True},
                    headers=_AUTH_HEADER,
                )
                assert resp.status_code == 409

    def test_update_flag(self):
        app = self._make_app()
        flag = self._mock_flag("update.me")
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {"update.me": flag}), patch(
                "app.api.feature_flags.flags.set"
            ) as mock_set:
                resp = client.put(
                    "/api/v1/feature-flags/update.me",
                    json={"enabled": False},
                    headers=_AUTH_HEADER,
                )
                assert resp.status_code == 200
                mock_set.assert_called_once()

    def test_update_flag_not_found(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags._flags", {}):
                resp = client.put(
                    "/api/v1/feature-flags/nonexistent",
                    json={"enabled": True},
                    headers=_AUTH_HEADER,
                )
                assert resp.status_code == 404

    def test_delete_flag(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.delete", return_value=True):
                resp = client.delete("/api/v1/feature-flags/delete.me", headers=_AUTH_HEADER)
                assert resp.status_code == 204

    def test_delete_flag_not_found(self):
        app = self._make_app()
        with TestClient(app) as client:
            with patch("app.api.feature_flags.flags.delete", return_value=False):
                resp = client.delete("/api/v1/feature-flags/nonexistent", headers=_AUTH_HEADER)
                assert resp.status_code == 404

    def test_list_flags_unauthorized(self):
        app = FastAPI()
        from app.api.feature_flags import router
        app.include_router(router, prefix="/api/v1/feature-flags", tags=["feature_flags"])
        with TestClient(app) as client:
            resp = client.get("/api/v1/feature-flags/")
            assert resp.status_code == 401

    def test_create_flag_unauthorized(self):
        app = FastAPI()
        from app.api.feature_flags import router
        app.include_router(router, prefix="/api/v1/feature-flags", tags=["feature_flags"])
        with TestClient(app) as client:
            resp = client.post("/api/v1/feature-flags/", json={"key": "test", "enabled": True})
            assert resp.status_code == 401


# ===========================================================================
# SKILLS — tested via direct async function calls
# ===========================================================================


class _SkillsTestBase:
    """Mixin: patches _get_supabase for every test method."""

    @pytest.fixture(autouse=True)
    def _mock_sb(self):
        with patch("app.api.skills._get_supabase") as m:
            sb = MagicMock()
            m.return_value = sb
            self._sb = sb
            yield


@pytest.mark.api
class TestSkillCategoryFunctions(_SkillsTestBase):
    """skill_categories CRUD: list, get, create, update, delete."""

    SAMPLE = {
        "category_id": "cat-1",
        "name": "Programming Languages",
        "slug": "programming-languages",
        "description": "Languages category",
        "icon": "code",
        "color": "#6366F1",
        "sort_order": 1,
        "parent_category_id": None,
        "is_active": True,
        "metadata": {},
        "level": 1,
        "path": None,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_categories(self):
        from app.api.skills import list_categories

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_categories(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert len(result) == 1
        assert result[0]["name"] == "Programming Languages"

    @pytest.mark.asyncio
    async def test_list_categories_empty(self):
        from app.api.skills import list_categories

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        result = await list_categories(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_category(self):
        from app.api.skills import get_category

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_category(category_id="cat-1", current_user=_make_auth_mock_user())
        assert result["category_id"] == "cat-1"

    @pytest.mark.asyncio
    async def test_get_category_not_found(self):
        from app.api.skills import get_category
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_category(category_id="nonexistent", current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_category(self):
        from app.api.skills import create_category
        from database.schemas.skill import SkillCategoryCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_category(
            category=SkillCategoryCreate(name="Test", slug="test", description="desc"),
            current_user=_make_auth_mock_user(),
        )
        assert result["name"] == "Programming Languages"

    @pytest.mark.asyncio
    async def test_update_category(self):
        from app.api.skills import update_category
        from database.schemas.skill import SkillCategoryUpdate

        updated = {**self.SAMPLE, "name": "Updated"}
        self._sb.from_.return_value = MockQueryBuilder(return_data=[updated])
        result = await update_category(
            category_id="cat-1", update=SkillCategoryUpdate(name="Updated"), current_user=_make_auth_mock_user()
        )
        assert result["name"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_category_not_found(self):
        from app.api.skills import update_category
        from database.schemas.skill import SkillCategoryUpdate
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await update_category(
                category_id="nonexistent",
                update=SkillCategoryUpdate(name="Nope"),
                current_user=_make_auth_mock_user(),
            )
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_category(self):
        from app.api.skills import delete_category

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_category(category_id="cat-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillFunctions(_SkillsTestBase):
    """Skills CRUD: list, get, create, update, delete."""

    SAMPLE = {
        "skill_id": "skill-1",
        "category_id": "cat-1",
        "name": "Python",
        "slug": "python",
        "description": "General-purpose programming",
        "level_min": 0,
        "level_max": 5,
        "aliases": [],
        "metadata": {},
        "is_deprecated": False,
        "skill_health": None,
        "deprecated_at": None,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_skills(self):
        from app.api.skills import list_skills

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_skills(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_skills_filtered_by_category(self):
        from app.api.skills import list_skills

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_skills(category_id="cat-1", current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_skill(self):
        from app.api.skills import get_skill

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_skill(skill_id="skill-1", current_user=_make_auth_mock_user())
        assert result["skill_id"] == "skill-1"

    @pytest.mark.asyncio
    async def test_get_skill_not_found(self):
        from app.api.skills import get_skill
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_skill(skill_id="nonexistent", current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_skill(self):
        from app.api.skills import create_skill
        from database.schemas.skill import SkillCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_skill(
            skill=SkillCreate(category_id="cat-1", name="Python", slug="python"),
            current_user=_make_auth_mock_user(),
        )
        assert result["skill_id"] == "skill-1"

    @pytest.mark.asyncio
    async def test_update_skill(self):
        from app.api.skills import update_skill
        from database.schemas.skill import SkillUpdate

        updated = {**self.SAMPLE, "name": "Advanced Python"}
        self._sb.from_.return_value = MockQueryBuilder(return_data=[updated])
        result = await update_skill(
            skill_id="skill-1", update=SkillUpdate(name="Advanced Python"), current_user=_make_auth_mock_user()
        )
        assert result["name"] == "Advanced Python"

    @pytest.mark.asyncio
    async def test_delete_skill(self):
        from app.api.skills import delete_skill

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_skill(skill_id="skill-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillRelationshipFunctions(_SkillsTestBase):
    """Skill relationships: list, create, delete."""

    SAMPLE = {
        "relationship_id": "rel-1",
        "from_skill_id": "skill-1",
        "to_skill_id": "skill-2",
        "relationship_type": "prerequisite",
        "min_level_from": None,
        "min_level_to": None,
        "weight": 1.0,
        "is_directed": True,
        "metadata": {},
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_relationships(self):
        from app.api.skills import list_relationships

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_relationships(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_relationship(self):
        from app.api.skills import create_relationship
        from database.schemas.skill import SkillRelationshipCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_relationship(
            rel=SkillRelationshipCreate(from_skill_id="skill-1", to_skill_id="skill-2", relationship_type="prerequisite"),
            current_user=_make_auth_mock_user(),
        )
        assert result["relationship_id"] == "rel-1"

    @pytest.mark.asyncio
    async def test_delete_relationship(self):
        from app.api.skills import delete_relationship

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_relationship(relationship_id="rel-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillTagFunctions(_SkillsTestBase):
    """Tags: list, create, link, delete."""

    SAMPLE = {
        "tag_id": "tag-1",
        "name": "backend",
        "slug": "backend",
        "description": "",
        "color": None,
        "metadata": {},
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_tags(self):
        from app.api.skills import list_tags

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_tags(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_tag(self):
        from app.api.skills import create_tag
        from database.schemas.skill import TagCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_tag(
            tag=TagCreate(name="backend", slug="backend"),
            current_user=_make_auth_mock_user(),
        )
        assert result["tag_id"] == "tag-1"

    @pytest.mark.asyncio
    async def test_link_skill_tag(self):
        from app.api.skills import link_skill_tag
        from database.schemas.skill import SkillTagCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"status": "linked"}])
        result = await link_skill_tag(
            link=SkillTagCreate(skill_id="skill-1", tag_id="tag-1"),
            current_user=_make_auth_mock_user(),
        )
        assert result["status"] == "linked"

    @pytest.mark.asyncio
    async def test_delete_tag(self):
        from app.api.skills import delete_tag

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_tag(tag_id="tag-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillExternalMappingFunctions(_SkillsTestBase):
    """External mappings: list, create, update, delete."""

    SAMPLE = {
        "mapping_id": "em-1",
        "skill_id": "skill-1",
        "external_system": "linkedin",
        "external_id": "python-123",
        "external_name": "Python",
        "mapping_type": "exact",
        "confidence": 1.0,
        "metadata": {},
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_external_mappings(self):
        from app.api.skills import list_external_mappings

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_external_mappings(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_external_mapping(self):
        from app.api.skills import create_external_mapping
        from database.schemas.skill import SkillExternalMappingCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_external_mapping(
            mapping=SkillExternalMappingCreate(
                skill_id="skill-1", external_system="linkedin", external_id="py-123", external_name="Python"
            ),
            current_user=_make_auth_mock_user(),
        )
        assert result["mapping_id"] == "em-1"

    @pytest.mark.asyncio
    async def test_delete_external_mapping(self):
        from app.api.skills import delete_external_mapping

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_external_mapping(mapping_id="em-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestUserSkillFunctions(_SkillsTestBase):
    """User skills: list, create, update, delete."""

    SAMPLE = {
        "user_skill_id": "us-1",
        "user_id": _TEST_USER_ID,
        "skill_id": "skill-1",
        "level": 3,
        "state": "learning",
        "confidence_score": 0.0,
        "evidence_score": 0.0,
        "level_change_90d": 0.0,
        "is_emerging": False,
        "is_stale": False,
        "last_activity_at": None,
        "metadata": {},
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_user_skills(self):
        from app.api.skills import list_user_skills

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_user_skills(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_delete_user_skill(self):
        from app.api.skills import delete_user_skill

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_user_skill(user_skill_id="us-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillEvidenceFunctions(_SkillsTestBase):
    """Evidence: list."""

    SAMPLE = {
        "evidence_id": "ev-1",
        "user_skill_id": "us-1",
        "user_id": _TEST_USER_ID,
        "source_type": "project",
        "title": "Built a web app",
        "description": "Django project",
        "url": None,
        "signed_hash": "abc123",
        "previous_hash": None,
        "metadata": {},
        "collected_at": 1717200000,
        "state": "active",
        "quality_score": 0.0,
        "trust_score": 0.0,
        "weight": 1.0,
        "verified_at": None,
        "expires_at": None,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_evidence(self):
        from app.api.skills import list_evidence

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_evidence(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillTargetFunctions(_SkillsTestBase):
    """Targets: list."""

    SAMPLE = {
        "target_id": "tgt-1",
        "user_skill_id": "us-1",
        "user_id": _TEST_USER_ID,
        "target_level": 5,
        "current_level": 0,
        "priority": "medium",
        "target_date": None,
        "status": "active",
        "metadata": {},
        "gap_size": 5,
        "progress_pct": 0.0,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_targets(self):
        from app.api.skills import list_targets

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_targets(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillAssessmentFunctions(_SkillsTestBase):
    """Assessments: list."""

    SAMPLE = {
        "assessment_id": "a-1",
        "user_skill_id": "us-1",
        "user_id": _TEST_USER_ID,
        "assessment_type": "quiz",
        "score": 8,
        "level_achieved": None,
        "confidence": None,
        "status": "completed",
        "duration_seconds": None,
        "result_data": {},
        "started_at": None,
        "completed_at": None,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_assessments(self):
        from app.api.skills import list_assessments

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_assessments(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillRecommendationFunctions(_SkillsTestBase):
    """Recommendations: list, accept."""

    SAMPLE = {
        "recommendation_id": "rec-1",
        "user_id": _TEST_USER_ID,
        "recommendation_type": "course",
        "skill_id": "skill-1",
        "reasoning": "Good fit",
        "priority": 0,
        "source": "ai",
        "metadata": {},
        "expires_at": None,
        "accepted": False,
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_recommendations(self):
        from app.api.skills import list_recommendations

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_recommendations(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillMarketDataFunctions(_SkillsTestBase):
    """Market data: list, create."""

    SAMPLE = {
        "id": "md-1",
        "skill_id": "skill-1",
        "demand_score": 85,
        "growth_score": 0.5,
        "salary_median": None,
        "salary_p10": None,
        "salary_p25": None,
        "salary_p75": None,
        "salary_p90": None,
        "competition_score": None,
        "future_relevance": None,
        "job_postings_count": None,
        "source_data": {},
        "data_freshness": "current",
        "skill_health": None,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_market_data(self):
        from app.api.skills import list_market_data

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_market_data(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillCertificationFunctions(_SkillsTestBase):
    """Certifications: list."""

    SAMPLE = {
        "certification_id": "cert-1",
        "skill_id": "skill-1",
        "category_id": None,
        "name": "PCEP",
        "provider": "Python Institute",
        "level_mapped": 1,
        "quality_weight": 0.5,
        "is_verified": False,
        "verification_url": None,
        "expiration_months": None,
        "metadata": {},
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_certifications(self):
        from app.api.skills import list_certifications

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_certifications(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillActivityFunctions(_SkillsTestBase):
    """Activity: list."""

    SAMPLE = {
        "activity_id": "act-1",
        "user_id": _TEST_USER_ID,
        "activity_type": "skill_added",
        "skill_id": None,
        "metadata": {},
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_activity(self):
        from app.api.skills import list_activity

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_activity(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1


@pytest.mark.api
class TestSkillEventFunctions(_SkillsTestBase):
    """Events: publish, list, get."""

    SAMPLE = {
        "event_id": "evt-1",
        "event_type": "skill.created",
        "event_version": "1.0",
        "aggregate_type": "skill",
        "aggregate_id": "skill-1",
        "user_id": _TEST_USER_ID,
        "data": {"skill_id": "skill-1"},
        "metadata": {},
        "correlation_id": None,
        "causation_id": None,
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_events(self):
        from app.api.skills import list_events

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_events(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_event(self):
        from app.api.skills import get_event

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_event(event_id="evt-1", current_user=_make_auth_mock_user())
        assert result["event_id"] == "evt-1"

    @pytest.mark.asyncio
    async def test_get_event_not_found(self):
        from app.api.skills import get_event
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_event(event_id="nonexistent", current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404


@pytest.mark.api
class TestSkillRoadmapDefinitionFunctions(_SkillsTestBase):
    """Roadmap definitions: list, get, create, update, delete."""

    SAMPLE = {
        "roadmap_id": "rd-1",
        "name": "Python Beginner Roadmap",
        "description": "Step-by-step guide",
        "target_skill_id": None,
        "difficulty": "intermediate",
        "estimated_duration": None,
        "steps": [],
        "is_ai_generated": False,
        "metadata": {},
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_roadmap_definitions(self):
        from app.api.skills import list_roadmap_definitions

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_roadmap_definitions(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_roadmap_definition(self):
        from app.api.skills import get_roadmap_definition

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_roadmap_definition(roadmap_id="rd-1", current_user=_make_auth_mock_user())
        assert result["roadmap_id"] == "rd-1"

    @pytest.mark.asyncio
    async def test_create_roadmap_definition(self):
        from app.api.skills import create_roadmap_definition
        from database.schemas.skill import SkillRoadmapDefinitionCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await create_roadmap_definition(
            defn=SkillRoadmapDefinitionCreate(name="New Roadmap", description="Desc"),
            current_user=_make_auth_mock_user(),
        )
        assert result["roadmap_id"] == "rd-1"

    @pytest.mark.asyncio
    async def test_delete_roadmap_definition(self):
        from app.api.skills import delete_roadmap_definition

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_roadmap_definition(roadmap_id="rd-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillJunctionLinkFunctions(_SkillsTestBase):
    """Junction links: create, delete."""

    @pytest.mark.asyncio
    async def test_create_project_skill_link(self):
        from app.api.skills import create_project_skill_link
        from database.schemas.skill import SkillProjectLinkCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "link-1"}])
        result = await create_project_skill_link(
            link=SkillProjectLinkCreate(project_id="proj-1", skill_id="skill-1"),
            current_user=_make_auth_mock_user(),
        )
        assert result["id"] == "link-1"

    @pytest.mark.asyncio
    async def test_delete_project_skill_link(self):
        from app.api.skills import delete_project_skill_link

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_project_skill_link(
            project_id="proj-1", skill_id="skill-1", current_user=_make_auth_mock_user()
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_create_roadmap_skill_link(self):
        from app.api.skills import create_roadmap_skill_link
        from database.schemas.skill import SkillRoadmapLinkCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "link-2"}])
        result = await create_roadmap_skill_link(
            link=SkillRoadmapLinkCreate(roadmap_id="rm-1", skill_id="skill-1", phase="beginner", target_level=3),
            current_user=_make_auth_mock_user(),
        )
        assert result["id"] == "link-2"

    @pytest.mark.asyncio
    async def test_delete_roadmap_skill_link(self):
        from app.api.skills import delete_roadmap_skill_link

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_roadmap_skill_link(
            roadmap_id="rm-1", skill_id="skill-1", current_user=_make_auth_mock_user()
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_create_opportunity_skill_link(self):
        from app.api.skills import create_opportunity_skill_link
        from database.schemas.skill import SkillOpportunityLinkCreate

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "link-3"}])
        result = await create_opportunity_skill_link(
            link=SkillOpportunityLinkCreate(opportunity_id="opp-1", skill_id="skill-1"),
            current_user=_make_auth_mock_user(),
        )
        assert result["id"] == "link-3"

    @pytest.mark.asyncio
    async def test_delete_opportunity_skill_link(self):
        from app.api.skills import delete_opportunity_skill_link

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_opportunity_skill_link(
            opportunity_id="opp-1", skill_id="skill-1", current_user=_make_auth_mock_user()
        )
        assert result is None


@pytest.mark.api
class TestSkillAuditLogFunctions(_SkillsTestBase):
    """Audit log: list, get."""

    SAMPLE = {
        "audit_id": "aud-1",
        "table_name": "skills",
        "record_id": "skill-1",
        "action": "UPDATE",
        "old_values": None,
        "new_values": None,
        "changed_by": _TEST_USER_ID,
        "changed_at": 1717200000,
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_audit_log(self):
        from app.api.skills import list_audit_log

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_audit_log(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_audit_entry(self):
        from app.api.skills import get_audit_entry

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_audit_entry(audit_id="aud-1", current_user=_make_auth_mock_user())
        assert result["audit_id"] == "aud-1"

    @pytest.mark.asyncio
    async def test_get_audit_entry_not_found(self):
        from app.api.skills import get_audit_entry
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_audit_entry(audit_id="nonexistent", current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_audit_for_record(self):
        from app.api.skills import get_audit_for_record

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_audit_for_record(
            table_name="skills", record_id="skill-1", current_user=_make_auth_mock_user()
        )
        assert len(result) == 1


@pytest.mark.api
class TestSkillEventSubscriptionFunctions(_SkillsTestBase):
    """Event subscriptions: list, create, get, update, delete."""

    SAMPLE = {
        "subscription_id": "sub-1",
        "name": "Skill Change Listener",
        "url": "https://hooks.example.com/webhook",
        "event_types": ["skill.updated"],
        "headers": {},
        "is_active": True,
        "retry_policy": {"max_retries": 5, "backoff": "exponential", "initial_delay_ms": 1000},
        "last_delivered_at": None,
        "last_error_at": None,
        "delivery_count": 0,
        "failure_count": 0,
        "created_at": 1717200000,
        "updated_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_event_subscriptions(self):
        from app.api.skills import list_event_subscriptions

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_event_subscriptions(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_event_subscription(self):
        from app.api.skills import get_event_subscription

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_event_subscription(subscription_id="sub-1", current_user=_make_auth_mock_user())
        assert result["subscription_id"] == "sub-1"

    @pytest.mark.asyncio
    async def test_get_event_subscription_not_found(self):
        from app.api.skills import get_event_subscription
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_event_subscription(subscription_id="nonexistent", current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_event_subscription(self):
        from app.api.skills import delete_event_subscription

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{}])
        result = await delete_event_subscription(subscription_id="sub-1", current_user=_make_auth_mock_user())
        assert result is None


@pytest.mark.api
class TestSkillAnalyticsFunctions(_SkillsTestBase):
    """Analytics snapshots: list, get_latest, trigger."""

    SAMPLE = {
        "snapshot_id": "ss-1",
        "user_id": _TEST_USER_ID,
        "snapshot_date": "2026-07-01",
        "snapshot_type": "manual",
        "data": {},
        "total_skills": 5,
        "created_at": 1717200000,
    }

    @pytest.mark.asyncio
    async def test_list_analytics_snapshots(self):
        from app.api.skills import list_analytics_snapshots

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await list_analytics_snapshots(current_user=_make_auth_mock_user(), limit=100, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_latest_analytics_snapshot(self):
        from app.api.skills import get_latest_analytics_snapshot

        self._sb.from_.return_value = MockQueryBuilder(return_data=[self.SAMPLE])
        result = await get_latest_analytics_snapshot(current_user=_make_auth_mock_user())
        assert result["snapshot_id"] == "ss-1"

    @pytest.mark.asyncio
    async def test_get_latest_analytics_snapshot_not_found(self):
        from app.api.skills import get_latest_analytics_snapshot
        from fastapi import HTTPException

        self._sb.from_.return_value = MockQueryBuilder(return_data=[])
        with pytest.raises(HTTPException) as exc:
            await get_latest_analytics_snapshot(current_user=_make_auth_mock_user())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_trigger_analytics_refresh(self):
        from app.api.skills import trigger_analytics_refresh

        result = await trigger_analytics_refresh(current_user=_make_auth_mock_user())
        assert result["status"] == "queued"


@pytest.mark.api
class TestSkillHistoryAndViewFunctions(_SkillsTestBase):
    """Webhook queue, history, and materialized views."""

    @pytest.mark.asyncio
    async def test_list_webhook_queue(self):
        from app.api.skills import list_webhook_queue

        self._sb.from_.return_value = MockQueryBuilder(
            return_data=[{"id": "wh-1", "url": "https://hooks.example.com", "status": "pending"}]
        )
        result = await list_webhook_queue(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_taxonomy_history(self):
        from app.api.skills import list_taxonomy_history

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "th-1", "entity_type": "skill", "entity_id": "skill-1"}])
        result = await list_taxonomy_history(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_user_skill_history(self):
        from app.api.skills import list_user_skill_history

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "ush-1", "user_id": _TEST_USER_ID, "skill_id": "skill-1"}])
        result = await list_user_skill_history(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_market_history(self):
        from app.api.skills import list_market_history

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"id": "mh-1", "skill_id": "skill-1"}])
        result = await list_market_history(current_user=_make_auth_mock_user(), limit=50, offset=0)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_refresh_all_views(self):
        from app.api.skills import refresh_all_views

        result = await refresh_all_views(current_user=_make_auth_mock_user())
        assert result["status"] == "queued"

    @pytest.mark.asyncio
    async def test_get_user_proficiency(self):
        from app.api.skills import get_user_proficiency

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"skill_id": "skill-1", "proficiency": 4}])
        result = await get_user_proficiency(current_user=_make_auth_mock_user())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_market_intelligence(self):
        from app.api.skills import get_market_intelligence

        self._sb.from_.return_value = MockQueryBuilder(return_data=[{"skill_id": "skill-1", "skill_health": 85}])
        result = await get_market_intelligence(current_user=_make_auth_mock_user())
        assert len(result) == 1
