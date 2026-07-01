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
    result = await list_categories(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_skills(mock_supabase):
    from apps.api.app.api.skills import list_skills
    result = await list_skills(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_skill_not_found(mock_supabase):
    from apps.api.app.api.skills import get_skill
    from fastapi import HTTPException
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[])
    with pytest.raises(HTTPException) as exc:
        await get_skill("nonexistent", current_user=_make_auth_mock())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_user_skills(mock_supabase):
    from apps.api.app.api.skills import list_user_skills
    result = await list_user_skills(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_certifications(mock_supabase):
    from apps.api.app.api.skills import list_certifications
    result = await list_certifications(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_recommendations(mock_supabase):
    from apps.api.app.api.skills import list_recommendations
    result = await list_recommendations(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_log_activity(mock_supabase):
    from apps.api.app.api.skills import log_activity
    from database.schemas.skill import SkillActivityLogCreate
    act = SkillActivityLogCreate(user_id=_TEST_USER_ID, activity_type="skill_tree_viewed")
    result = await log_activity(act, current_user=_make_auth_mock())
    assert result is not None


# === Income ===


@pytest.mark.asyncio
async def test_list_income(mock_supabase):
    from apps.api.app.api.skills import list_income_data
    result = await list_income_data(current_user=_make_auth_mock(), limit=50, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_income(mock_supabase):
    from apps.api.app.api.skills import create_income_data
    from database.schemas.skill import SkillIncomeDataCreate, IncomeSource
    data = SkillIncomeDataCreate(skill_id="skill-1", source=IncomeSource.freelance, level=3, p50=500, currency="USD")
    result = await create_income_data(data, current_user=_make_auth_mock())
    assert result is not None


# === Market Data ===


@pytest.mark.asyncio
async def test_create_market_data(mock_supabase):
    from apps.api.app.api.skills import create_market_data
    from database.schemas.skill import SkillMarketDataCreate
    data = SkillMarketDataCreate(skill_id="skill-1", demand_score=80, growth_score=0.15)
    result = await create_market_data(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_market_data_not_found(mock_supabase):
    from apps.api.app.api.skills import update_market_data
    from database.schemas.skill import SkillMarketDataCreate
    from fastapi import HTTPException
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[])
    with pytest.raises(HTTPException) as exc:
        data = SkillMarketDataCreate(skill_id="nonexistent", demand_score=50, growth_score=0.1)
        await update_market_data("nonexistent", data, current_user=_make_auth_mock())
    assert exc.value.status_code == 404


# === Certificate CRUD ===


@pytest.mark.asyncio
async def test_create_certification(mock_supabase):
    from apps.api.app.api.skills import create_certification
    from database.schemas.skill import SkillCertificationCreate
    data = SkillCertificationCreate(skill_id="skill-1", name="AWS CSA", provider="Amazon", level_mapped=4, is_verified=False)
    result = await create_certification(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_certification(mock_supabase):
    from apps.api.app.api.skills import update_certification
    from database.schemas.skill import SkillCertificationCreate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"certification_id": "cert-1"}])
    data = SkillCertificationCreate(skill_id="skill-1", name="Updated", provider="Amazon", level_mapped=5, is_verified=True)
    result = await update_certification("cert-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_certification(mock_supabase):
    from apps.api.app.api.skills import delete_certification
    result = await delete_certification("cert-1", current_user=_make_auth_mock())
    assert result is None


# === Topics CRUD ===


@pytest.mark.asyncio
async def test_list_topics(mock_supabase):
    from apps.api.app.api.skills import list_topics
    result = await list_topics(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_topic(mock_supabase):
    from apps.api.app.api.skills import create_topic
    from database.schemas.skill import SkillTopicCreate
    data = SkillTopicCreate(skill_id="skill-1", name="React Hooks")
    result = await create_topic(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_topic(mock_supabase):
    from apps.api.app.api.skills import update_topic
    from database.schemas.skill import SkillTopicCreate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"topic_id": "topic-1"}])
    data = SkillTopicCreate(skill_id="skill-1", name="Updated Topic")
    result = await update_topic("topic-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_topic(mock_supabase):
    from apps.api.app.api.skills import delete_topic
    result = await delete_topic("topic-1", current_user=_make_auth_mock())
    assert result is None


# === Resources CRUD ===


@pytest.mark.asyncio
async def test_create_resource(mock_supabase):
    from apps.api.app.api.skills import create_skill_resource
    from database.schemas.skill import SkillResourceCreate
    data = SkillResourceCreate(skill_id="skill-1", title="React Docs", resource_type="article")
    result = await create_skill_resource(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_resource(mock_supabase):
    from apps.api.app.api.skills import update_skill_resource
    from database.schemas.skill import SkillResourceCreate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"resource_id": "res-1"}])
    data = SkillResourceCreate(skill_id="skill-1", title="Updated", resource_type="course")
    result = await update_skill_resource("res-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_resource(mock_supabase):
    from apps.api.app.api.skills import delete_skill_resource
    result = await delete_skill_resource("res-1", current_user=_make_auth_mock())
    assert result is None


# === Learning Paths CRUD ===


@pytest.mark.asyncio
async def test_create_learning_path(mock_supabase):
    from apps.api.app.api.skills import create_learning_path
    from database.schemas.skill import SkillLearningPathCreate
    data = SkillLearningPathCreate(target_skill_id="skill-1", name="React Mastery", steps=[])
    result = await create_learning_path(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_learning_path(mock_supabase):
    from apps.api.app.api.skills import update_learning_path
    from database.schemas.skill import SkillLearningPathCreate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"path_id": "path-1"}])
    data = SkillLearningPathCreate(target_skill_id="skill-1", name="Updated", steps=[])
    result = await update_learning_path("path-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_learning_path(mock_supabase):
    from apps.api.app.api.skills import delete_learning_path
    result = await delete_learning_path("path-1", current_user=_make_auth_mock())
    assert result is None


# === Junction Links ===


@pytest.mark.asyncio
async def test_create_project_skill_link(mock_supabase):
    from apps.api.app.api.skills import create_project_skill_link
    from database.schemas.skill import SkillProjectLinkCreate
    data = SkillProjectLinkCreate(project_id="proj-1", skill_id="skill-1")
    result = await create_project_skill_link(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_create_roadmap_skill_link(mock_supabase):
    from apps.api.app.api.skills import create_roadmap_skill_link
    from database.schemas.skill import SkillRoadmapLinkCreate
    data = SkillRoadmapLinkCreate(roadmap_id="rm-1", skill_id="skill-1", phase="foundation", target_level=3)
    result = await create_roadmap_skill_link(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_create_opportunity_skill_link(mock_supabase):
    from apps.api.app.api.skills import create_opportunity_skill_link
    from database.schemas.skill import SkillOpportunityLinkCreate
    data = SkillOpportunityLinkCreate(opportunity_id="opp-1", skill_id="skill-1")
    result = await create_opportunity_skill_link(data, current_user=_make_auth_mock())
    assert result is not None


# === External Mappings CRUD ===


@pytest.mark.asyncio
async def test_list_external_mappings(mock_supabase):
    from apps.api.app.api.skills import list_external_mappings
    result = await list_external_mappings(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_external_mapping(mock_supabase):
    from apps.api.app.api.skills import create_external_mapping
    from database.schemas.skill import SkillExternalMappingCreate
    data = SkillExternalMappingCreate(skill_id="skill-1", external_system="linkedin", external_id="123", external_name="React", confidence=0.9)
    result = await create_external_mapping(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_update_external_mapping(mock_supabase):
    from apps.api.app.api.skills import update_external_mapping
    from database.schemas.skill import SkillExternalMappingUpdate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"mapping_id": "map-1"}])
    data = SkillExternalMappingUpdate(external_name="Updated Name", confidence=0.95)
    result = await update_external_mapping("map-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_external_mapping(mock_supabase):
    from apps.api.app.api.skills import delete_external_mapping
    result = await delete_external_mapping("map-1", current_user=_make_auth_mock())
    assert result is None


# === Roadmap Definitions Update/Delete ===


@pytest.mark.asyncio
async def test_update_roadmap_definition(mock_supabase):
    from apps.api.app.api.skills import update_roadmap_definition
    from database.schemas.skill import SkillRoadmapDefinitionCreate
    mock_supabase.return_value.from_.return_value = MockQueryBuilder(return_data=[{"roadmap_id": "rm-1"}])
    data = SkillRoadmapDefinitionCreate(name="Updated Roadmap", stages=[])
    result = await update_roadmap_definition("rm-1", data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_delete_roadmap_definition(mock_supabase):
    from apps.api.app.api.skills import delete_roadmap_definition
    result = await delete_roadmap_definition("rm-1", current_user=_make_auth_mock())
    assert result is None


# === Forecasts ===


@pytest.mark.asyncio
async def test_list_forecasts(mock_supabase):
    from apps.api.app.api.skills import list_forecasts
    result = await list_forecasts(current_user=_make_auth_mock(), limit=50, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_forecast(mock_supabase):
    from apps.api.app.api.skills import create_forecast
    from database.schemas.skill import SkillForecastCreate
    data = SkillForecastCreate(skill_id="skill-1", forecast_date="2026-07-01", metric="demand", predicted_value=85.0)
    result = await create_forecast(data, current_user=_make_auth_mock())
    assert result is not None


# === Evidence & Targets & Assessments ===


@pytest.mark.asyncio
async def test_list_evidence(mock_supabase):
    from apps.api.app.api.skills import list_evidence
    result = await list_evidence(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_evidence(mock_supabase):
    from apps.api.app.api.skills import create_evidence
    from database.schemas.skill import UserSkillEvidenceCreate
    data = UserSkillEvidenceCreate(
        user_skill_id="us-1", user_id=_TEST_USER_ID,
        title="Built an app",
        description="", source_type="project",
        signed_hash="abc123", collected_at=1719400000,
    )
    result = await create_evidence(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_list_targets(mock_supabase):
    from apps.api.app.api.skills import list_targets
    result = await list_targets(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_target(mock_supabase):
    from apps.api.app.api.skills import create_target
    from database.schemas.skill import UserSkillTargetCreate
    data = UserSkillTargetCreate(user_skill_id="us-1", user_id=_TEST_USER_ID, target_level=4, target_date=None)
    result = await create_target(data, current_user=_make_auth_mock())
    assert result is not None


@pytest.mark.asyncio
async def test_list_assessments(mock_supabase):
    from apps.api.app.api.skills import list_assessments
    result = await list_assessments(current_user=_make_auth_mock(), limit=100, offset=0)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_assessment(mock_supabase):
    from apps.api.app.api.skills import create_assessment
    from database.schemas.skill import UserSkillAssessmentCreate
    data = UserSkillAssessmentCreate(user_skill_id="us-1", user_id=_TEST_USER_ID, assessment_type="self")
    result = await create_assessment(data, current_user=_make_auth_mock())
    assert result is not None
