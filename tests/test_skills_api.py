"""Tests for skills.py API router — calls route functions directly."""

import pytest
from unittest.mock import MagicMock, patch
from apps.api.app.api.skills import (
    list_categories, create_category, get_category, update_category, delete_category,
    list_skills, create_skill, get_skill, update_skill, delete_skill,
    list_relationships, create_relationship, delete_relationship,
    list_tags, create_tag, link_skill_tag, delete_tag,
    list_external_mappings, create_external_mapping, update_external_mapping, delete_external_mapping,
    list_user_skills, create_user_skill, update_user_skill, delete_user_skill,
    list_evidence, create_evidence,
    list_targets, create_target,
    list_assessments, create_assessment,
    list_market_data, create_market_data, update_market_data,
    list_certifications, create_certification, update_certification, delete_certification,
    list_learning_paths, create_learning_path, update_learning_path, delete_learning_path,
    list_skill_resources, create_skill_resource, update_skill_resource, delete_skill_resource,
    list_recommendations, accept_recommendation,
    list_activity, log_activity,
    publish_event, list_events, get_event,
    list_roadmap_definitions, create_roadmap_definition, update_roadmap_definition,
    delete_roadmap_definition, get_roadmap_definition,
    create_topic, list_topics, update_topic, delete_topic,
    create_income_data, list_income_data,
    create_forecast, list_forecasts,
    list_audit_log, get_audit_entry, get_audit_for_record,
    list_event_subscriptions, create_event_subscription, get_event_subscription,
    update_event_subscription, delete_event_subscription,
    list_analytics_snapshots, get_latest_analytics_snapshot,
    trigger_analytics_refresh,
    list_webhook_queue,
    list_taxonomy_history, list_user_skill_history, list_market_history,
    refresh_all_views, get_user_proficiency, get_market_intelligence,
    create_project_skill_link, delete_project_skill_link,
    create_roadmap_skill_link, delete_roadmap_skill_link,
    create_opportunity_skill_link, delete_opportunity_skill_link,
)

_TEST_USER_ID = "user-1"


class MockUser:
    class Inner:
        id = _TEST_USER_ID
    user = Inner()


class MockQueryBuilder:
    def __init__(self, return_data=None, error_message=None):
        self._return_data = return_data if return_data is not None else []
        self._error_message = error_message
    def select(self, *a, **kw): return self
    def eq(self, *a, **kw): return self
    def neq(self, *a, **kw): return self
    def or_(self, *a, **kw): return self
    def order(self, *a, **kw): return self
    def limit(self, *a, **kw): return self
    def range(self, *a, **kw): return self
    def gte(self, *a, **kw): return self
    def lte(self, *a, **kw): return self
    def text_search(self, *a, **kw): return self
    def in_(self, *a, **kw): return self
    def not_(self, *a, **kw): return self
    def is_(self, *a, **kw): return self
    def from_(self, *a, **kw): return self
    def insert(self, d): return MockQueryBuilder(self._return_data, self._error_message)
    def update(self, d): return MockQueryBuilder(self._return_data, self._error_message)
    def delete(self): return MockQueryBuilder(self._return_data, self._error_message)
    def execute(self):
        r = MagicMock()
        r.data = self._return_data
        if self._error_message:
            r.error = MagicMock(message=self._error_message)
        else:
            r.error = None
        return r


@pytest.fixture
def ms():
    with patch("apps.api.app.api.skills._get_supabase") as m:
        m.return_value = MagicMock()
        yield m


def _cfg(ms, data, error=None):
    ms.return_value.from_.return_value = MockQueryBuilder(data, error)


L = 50  # explicit limit for functions with Query(default)s
OFF = 0

@pytest.mark.asyncio
async def test_list_categories(ms):
    _cfg(ms, [{"category_id": "1", "name": "P"}])
    r = await list_categories(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_category(ms):
    _cfg(ms, [{"category_id": "1", "name": "P"}])
    from database.schemas.skill import SkillCategoryCreate
    r = await create_category(SkillCategoryCreate(name="P", slug="p"), MockUser())
    assert r["category_id"] == "1"

@pytest.mark.asyncio
async def test_create_category_error(ms):
    _cfg(ms, [], "Duplicate")
    from database.schemas.skill import SkillCategoryCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_category(SkillCategoryCreate(name="P", slug="p"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_get_category(ms):
    _cfg(ms, [{"category_id": "1"}])
    r = await get_category("1", MockUser())
    assert r["category_id"] == "1"

@pytest.mark.asyncio
async def test_get_category_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_category("x", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_category(ms):
    _cfg(ms, [{"category_id": "1"}])
    from database.schemas.skill import SkillCategoryUpdate
    r = await update_category("1", SkillCategoryUpdate(name="U"), MockUser())
    assert r["category_id"] == "1"

@pytest.mark.asyncio
async def test_update_category_400(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillCategoryUpdate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_category("1", SkillCategoryUpdate(name="U"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_delete_category(ms):
    _cfg(ms, [])
    r = await delete_category("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_skills(ms):
    _cfg(ms, [{"skill_id": "1"}])
    r = await list_skills(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_skills_with_category(ms):
    _cfg(ms, [{"skill_id": "1"}])
    r = await list_skills(MockUser(), category_id="c1", limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_skill(ms):
    _cfg(ms, [{"skill_id": "1"}])
    from database.schemas.skill import SkillCreate
    r = await create_skill(SkillCreate(name="Py", slug="py", category_id="c1"), MockUser())
    assert r["skill_id"] == "1"

@pytest.mark.asyncio
async def test_create_skill_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_skill(SkillCreate(name="Py", slug="py", category_id="c1"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_get_skill(ms):
    _cfg(ms, [{"skill_id": "1"}])
    r = await get_skill("1", MockUser())
    assert r["skill_id"] == "1"

@pytest.mark.asyncio
async def test_get_skill_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_skill("x", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_skill(ms):
    _cfg(ms, [{"skill_id": "1"}])
    from database.schemas.skill import SkillUpdate
    r = await update_skill("1", SkillUpdate(name="U"), MockUser())
    assert r["skill_id"] == "1"

@pytest.mark.asyncio
async def test_update_skill_400(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillUpdate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_skill("1", SkillUpdate(name="U"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_delete_skill(ms):
    _cfg(ms, [])
    r = await delete_skill("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_relationships(ms):
    _cfg(ms, [{"relationship_id": "1"}])
    r = await list_relationships(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_relationships_filtered(ms):
    _cfg(ms, [{"relationship_id": "1"}])
    r = await list_relationships(MockUser(), skill_id="s1", relationship_type="related", limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_relationship(ms):
    _cfg(ms, [{"relationship_id": "1"}])
    from database.schemas.skill import SkillRelationshipCreate
    r = await create_relationship(SkillRelationshipCreate(from_skill_id="s1", to_skill_id="s2", relationship_type="related_to"), MockUser())
    assert r["relationship_id"] == "1"

@pytest.mark.asyncio
async def test_delete_relationship(ms):
    _cfg(ms, [])
    r = await delete_relationship("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_tags(ms):
    _cfg(ms, [{"tag_id": "1"}])
    r = await list_tags(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_tag(ms):
    _cfg(ms, [{"tag_id": "1"}])
    from database.schemas.skill import TagCreate
    r = await create_tag(TagCreate(name="b", slug="b"), MockUser())
    assert r["tag_id"] == "1"

@pytest.mark.asyncio
async def test_link_skill_tag(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillTagCreate
    r = await link_skill_tag(SkillTagCreate(skill_id="s1", tag_id="t1"), MockUser())
    assert r["status"] == "linked"

@pytest.mark.asyncio
async def test_delete_tag(ms):
    _cfg(ms, [])
    r = await delete_tag("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_external_mappings(ms):
    _cfg(ms, [{"mapping_id": "1"}])
    r = await list_external_mappings(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_external_mapping(ms):
    _cfg(ms, [{"mapping_id": "1"}])
    from database.schemas.skill import SkillExternalMappingCreate
    r = await create_external_mapping(SkillExternalMappingCreate(skill_id="s1", external_system="linkedin", external_id="123", external_name="n"), MockUser())
    assert r["mapping_id"] == "1"

@pytest.mark.asyncio
async def test_update_external_mapping(ms):
    _cfg(ms, [{"mapping_id": "1"}])
    from database.schemas.skill import SkillExternalMappingUpdate
    r = await update_external_mapping("1", SkillExternalMappingUpdate(external_name="U"), MockUser())
    assert r["mapping_id"] == "1"

@pytest.mark.asyncio
async def test_update_external_mapping_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillExternalMappingUpdate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_external_mapping("1", SkillExternalMappingUpdate(external_name="U"), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_external_mapping(ms):
    _cfg(ms, [])
    r = await delete_external_mapping("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_user_skills(ms):
    _cfg(ms, [{"user_skill_id": "1"}])
    r = await list_user_skills(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_user_skill(ms):
    _cfg(ms, [{"user_skill_id": "1"}])
    from database.schemas.skill import UserSkillCreate
    r = await create_user_skill(UserSkillCreate(skill_id="s1", user_id="u", state="learning"), MockUser())
    assert r["user_skill_id"] == "1"

@pytest.mark.asyncio
async def test_create_user_skill_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import UserSkillCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_user_skill(UserSkillCreate(skill_id="s1", user_id="u", state="learning"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_update_user_skill(ms):
    _cfg(ms, [{"user_skill_id": "1"}])
    from database.schemas.skill import UserSkillUpdate
    r = await update_user_skill("1", UserSkillUpdate(state="learning"), MockUser())
    assert r["user_skill_id"] == "1"

@pytest.mark.asyncio
async def test_update_user_skill_400(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import UserSkillUpdate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_user_skill("1", UserSkillUpdate(state="learning"), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_delete_user_skill(ms):
    _cfg(ms, [])
    r = await delete_user_skill("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_evidence(ms):
    _cfg(ms, [{"evidence_id": "1"}])
    r = await list_evidence(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_evidence(ms):
    _cfg(ms, [{"evidence_id": "1"}])
    from database.schemas.skill import UserSkillEvidenceCreate
    r = await create_evidence(UserSkillEvidenceCreate(user_skill_id="u1", user_id="u", title="x", source_type="project", description="x", url="", signed_hash="h", collected_at=0), MockUser())
    assert r["evidence_id"] == "1"

@pytest.mark.asyncio
async def test_create_evidence_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import UserSkillEvidenceCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_evidence(UserSkillEvidenceCreate(user_skill_id="u1", user_id="u", title="x", source_type="project", description="x", url="", signed_hash="h", collected_at=0), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_list_targets(ms):
    _cfg(ms, [{"target_id": "1"}])
    r = await list_targets(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_target(ms):
    _cfg(ms, [{"target_id": "1"}])
    from database.schemas.skill import UserSkillTargetCreate
    r = await create_target(UserSkillTargetCreate(user_skill_id="u1", user_id="u", target_level=3), MockUser())
    assert r["target_id"] == "1"

@pytest.mark.asyncio
async def test_create_target_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import UserSkillTargetCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_target(UserSkillTargetCreate(user_skill_id="u1", user_id="u", target_level=3), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_list_assessments(ms):
    _cfg(ms, [{"assessment_id": "1"}])
    r = await list_assessments(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_assessment(ms):
    _cfg(ms, [{"assessment_id": "1"}])
    from database.schemas.skill import UserSkillAssessmentCreate
    r = await create_assessment(UserSkillAssessmentCreate(user_skill_id="u1", user_id="u", score=75, assessment_type="self"), MockUser())
    assert r["assessment_id"] == "1"

@pytest.mark.asyncio
async def test_list_market_data(ms):
    _cfg(ms, [{"market_id": "1"}])
    r = await list_market_data(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_market_data(ms):
    _cfg(ms, [{"market_id": "1"}])
    from database.schemas.skill import SkillMarketDataCreate
    r = await create_market_data(SkillMarketDataCreate(skill_id="s1", demand_score=85, growth_score=10.0), MockUser())
    assert r["market_id"] == "1"

@pytest.mark.asyncio
async def test_create_market_data_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillMarketDataCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_market_data(SkillMarketDataCreate(skill_id="s1", demand_score=85, growth_score=10.0), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_update_market_data(ms):
    _cfg(ms, [{"market_id": "1"}])
    from database.schemas.skill import SkillMarketDataCreate
    r = await update_market_data("1", SkillMarketDataCreate(skill_id="s1", demand_score=90, growth_score=10.0), MockUser())
    assert r["market_id"] == "1"

@pytest.mark.asyncio
async def test_update_market_data_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillMarketDataCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_market_data("1", SkillMarketDataCreate(skill_id="s1", demand_score=90, growth_score=10.0), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_list_certifications(ms):
    _cfg(ms, [{"certification_id": "1"}])
    r = await list_certifications(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_certification(ms):
    _cfg(ms, [{"certification_id": "1"}])
    from database.schemas.skill import SkillCertificationCreate
    r = await create_certification(SkillCertificationCreate(skill_id="s1", name="P", provider="I", level_mapped=3), MockUser())
    assert r["certification_id"] == "1"

@pytest.mark.asyncio
async def test_update_certification(ms):
    _cfg(ms, [{"certification_id": "1"}])
    from database.schemas.skill import SkillCertificationCreate
    r = await update_certification("1", SkillCertificationCreate(skill_id="s1", name="U", provider="I", level_mapped=3), MockUser())
    assert r["certification_id"] == "1"

@pytest.mark.asyncio
async def test_update_certification_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillCertificationCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_certification("1", SkillCertificationCreate(skill_id="s1", name="U", provider="I", level_mapped=3), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_certification(ms):
    _cfg(ms, [])
    r = await delete_certification("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_learning_paths(ms):
    _cfg(ms, [{"path_id": "1"}])
    r = await list_learning_paths(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_learning_path(ms):
    _cfg(ms, [{"path_id": "1"}])
    from database.schemas.skill import SkillLearningPathCreate
    r = await create_learning_path(SkillLearningPathCreate(name="P", target_skill_id="s1"), MockUser())
    assert r["path_id"] == "1"

@pytest.mark.asyncio
async def test_update_learning_path(ms):
    _cfg(ms, [{"path_id": "1"}])
    from database.schemas.skill import SkillLearningPathCreate
    r = await update_learning_path("1", SkillLearningPathCreate(name="U", target_skill_id="s1"), MockUser())
    assert r["path_id"] == "1"

@pytest.mark.asyncio
async def test_delete_learning_path(ms):
    _cfg(ms, [])
    r = await delete_learning_path("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_skill_resources(ms):
    _cfg(ms, [{"resource_id": "1"}])
    r = await list_skill_resources(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_skill_resource(ms):
    _cfg(ms, [{"resource_id": "1"}])
    from database.schemas.skill import SkillResourceCreate
    r = await create_skill_resource(SkillResourceCreate(skill_id="s1", title="T", resource_type="video"), MockUser())
    assert r["resource_id"] == "1"

@pytest.mark.asyncio
async def test_update_skill_resource(ms):
    _cfg(ms, [{"resource_id": "1"}])
    from database.schemas.skill import SkillResourceCreate
    r = await update_skill_resource("1", SkillResourceCreate(skill_id="s1", title="U", resource_type="video"), MockUser())
    assert r["resource_id"] == "1"

@pytest.mark.asyncio
async def test_delete_skill_resource(ms):
    _cfg(ms, [])
    r = await delete_skill_resource("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_recommendations(ms):
    _cfg(ms, [{"recommendation_id": "1"}])
    r = await list_recommendations(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_accept_recommendation(ms):
    _cfg(ms, [{"recommendation_id": "1"}])
    r = await accept_recommendation("1", MockUser())
    assert r["recommendation_id"] == "1"

@pytest.mark.asyncio
async def test_accept_recommendation_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await accept_recommendation("1", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_list_activity(ms):
    _cfg(ms, [{"activity_id": "1"}])
    r = await list_activity(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_log_activity(ms):
    _cfg(ms, [{"activity_id": "1"}])
    from database.schemas.skill import SkillActivityLogCreate
    r = await log_activity(SkillActivityLogCreate(user_id="u", activity_type="skill_added"), MockUser())
    assert r["activity_id"] == "1"

@pytest.mark.asyncio
async def test_publish_event(ms):
    _cfg(ms, [{"event_id": "1"}])
    from database.schemas.skill import SkillEventCreate
    r = await publish_event(SkillEventCreate(event_type="sk.created", aggregate_type="skill", aggregate_id="s1", data={}), MockUser())
    assert r["event_id"] == "1"

@pytest.mark.asyncio
async def test_publish_event_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillEventCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await publish_event(SkillEventCreate(event_type="sk.created", aggregate_type="skill", aggregate_id="s1", data={}), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_list_events(ms):
    _cfg(ms, [{"event_id": "1"}])
    r = await list_events(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_get_event(ms):
    _cfg(ms, [{"event_id": "1"}])
    r = await get_event("1", MockUser())
    assert r["event_id"] == "1"

@pytest.mark.asyncio
async def test_get_event_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_event("1", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_list_roadmap_definitions(ms):
    _cfg(ms, [{"roadmap_id": "1"}])
    r = await list_roadmap_definitions(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_roadmap_definition(ms):
    _cfg(ms, [{"roadmap_id": "1"}])
    from database.schemas.skill import SkillRoadmapDefinitionCreate
    r = await create_roadmap_definition(SkillRoadmapDefinitionCreate(name="R"), MockUser())
    assert r["roadmap_id"] == "1"

@pytest.mark.asyncio
async def test_update_roadmap_definition(ms):
    _cfg(ms, [{"roadmap_id": "1"}])
    from database.schemas.skill import SkillRoadmapDefinitionCreate
    r = await update_roadmap_definition("1", SkillRoadmapDefinitionCreate(name="U"), MockUser())
    assert r["roadmap_id"] == "1"

@pytest.mark.asyncio
async def test_update_roadmap_definition_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillRoadmapDefinitionCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_roadmap_definition("1", SkillRoadmapDefinitionCreate(name="U"), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_roadmap_definition(ms):
    _cfg(ms, [])
    r = await delete_roadmap_definition("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_get_roadmap_definition(ms):
    _cfg(ms, [{"roadmap_id": "1"}])
    r = await get_roadmap_definition("1", MockUser())
    assert r["roadmap_id"] == "1"

@pytest.mark.asyncio
async def test_get_roadmap_definition_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_roadmap_definition("1", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_create_topic(ms):
    _cfg(ms, [{"topic_id": "1"}])
    from database.schemas.skill import SkillTopicCreate
    r = await create_topic(SkillTopicCreate(skill_id="s1", name="GA"), MockUser())
    assert r["topic_id"] == "1"

@pytest.mark.asyncio
async def test_list_topics(ms):
    _cfg(ms, [{"topic_id": "1"}])
    r = await list_topics(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_update_topic(ms):
    _cfg(ms, [{"topic_id": "1"}])
    from database.schemas.skill import SkillTopicCreate
    r = await update_topic("1", SkillTopicCreate(skill_id="s1", name="U"), MockUser())
    assert r["topic_id"] == "1"

@pytest.mark.asyncio
async def test_update_topic_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillTopicCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_topic("1", SkillTopicCreate(skill_id="s1", name="U"), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_topic(ms):
    _cfg(ms, [])
    r = await delete_topic("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_create_income_data(ms):
    _cfg(ms, [{"income_id": "1"}])
    from database.schemas.skill import SkillIncomeDataCreate
    r = await create_income_data(SkillIncomeDataCreate(skill_id="s1", source="employment", level=3), MockUser())
    assert r["income_id"] == "1"

@pytest.mark.asyncio
async def test_list_income_data(ms):
    _cfg(ms, [{"income_id": "1"}])
    r = await list_income_data(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_forecast(ms):
    _cfg(ms, [{"forecast_id": "1"}])
    from database.schemas.skill import SkillForecastCreate
    r = await create_forecast(SkillForecastCreate(skill_id="s1", metric="demand", forecast_date="2027-01-01", predicted_value=90.0), MockUser())
    assert r["forecast_id"] == "1"

@pytest.mark.asyncio
async def test_create_forecast_error(ms):
    _cfg(ms, [], "Error")
    from database.schemas.skill import SkillForecastCreate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await create_forecast(SkillForecastCreate(skill_id="s1", metric="demand", forecast_date="2027-01-01", predicted_value=90.0), MockUser())
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_list_forecasts(ms):
    _cfg(ms, [{"forecast_id": "1"}])
    r = await list_forecasts(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_audit_log(ms):
    _cfg(ms, [{"audit_id": "1"}])
    r = await list_audit_log(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_get_audit_entry(ms):
    _cfg(ms, [{"audit_id": "1"}])
    r = await get_audit_entry("1", MockUser())
    assert r["audit_id"] == "1"

@pytest.mark.asyncio
async def test_get_audit_entry_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_audit_entry("1", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_audit_for_record(ms):
    _cfg(ms, [{"audit_id": "1"}])
    r = await get_audit_for_record("skills", "1", MockUser())
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_event_subscriptions(ms):
    _cfg(ms, [{"subscription_id": "1"}])
    r = await list_event_subscriptions(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_event_subscription(ms):
    _cfg(ms, [{"subscription_id": "1"}])
    from database.schemas.skill import SkillEventSubscriptionCreate
    r = await create_event_subscription(SkillEventSubscriptionCreate(name="W", url="https://example.com/hook"), MockUser())
    assert r["subscription_id"] == "1"

@pytest.mark.asyncio
async def test_get_event_subscription(ms):
    _cfg(ms, [{"subscription_id": "1"}])
    r = await get_event_subscription("1", MockUser())
    assert r["subscription_id"] == "1"

@pytest.mark.asyncio
async def test_get_event_subscription_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_event_subscription("1", MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_event_subscription(ms):
    _cfg(ms, [{"subscription_id": "1"}])
    from database.schemas.skill import SkillEventSubscriptionUpdate
    r = await update_event_subscription("1", SkillEventSubscriptionUpdate(is_active=False), MockUser())
    assert r["subscription_id"] == "1"

@pytest.mark.asyncio
async def test_update_event_subscription_404(ms):
    _cfg(ms, [])
    from database.schemas.skill import SkillEventSubscriptionUpdate
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_event_subscription("1", SkillEventSubscriptionUpdate(is_active=False), MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_event_subscription(ms):
    _cfg(ms, [])
    r = await delete_event_subscription("1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_list_analytics_snapshots(ms):
    _cfg(ms, [{"snapshot_id": "1"}])
    r = await list_analytics_snapshots(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_get_latest_analytics_snapshot(ms):
    _cfg(ms, [{"snapshot_id": "1"}])
    r = await get_latest_analytics_snapshot(MockUser())
    assert r["snapshot_id"] == "1"

@pytest.mark.asyncio
async def test_get_latest_analytics_snapshot_404(ms):
    _cfg(ms, [])
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_latest_analytics_snapshot(MockUser())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_trigger_analytics_refresh(ms):
    r = await trigger_analytics_refresh(MockUser())
    assert r["status"] == "queued"

@pytest.mark.asyncio
async def test_list_webhook_queue(ms):
    _cfg(ms, [{"webhook_id": "1"}])
    r = await list_webhook_queue(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_taxonomy_history(ms):
    _cfg(ms, [{"history_id": "1"}])
    r = await list_taxonomy_history(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_user_skill_history(ms):
    _cfg(ms, [{"history_id": "1"}])
    r = await list_user_skill_history(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_list_market_history(ms):
    _cfg(ms, [{"history_id": "1"}])
    r = await list_market_history(MockUser(), limit=L, offset=OFF)
    assert len(r) == 1

@pytest.mark.asyncio
async def test_refresh_all_views(ms):
    r = await refresh_all_views(MockUser())
    assert r["status"] == "queued"

@pytest.mark.asyncio
async def test_get_user_proficiency(ms):
    _cfg(ms, [{"skill_id": "1", "proficiency": 75}])
    r = await get_user_proficiency(MockUser())
    assert len(r) == 1

@pytest.mark.asyncio
async def test_get_market_intelligence(ms):
    _cfg(ms, [{"skill_id": "1", "skill_health": 85}])
    r = await get_market_intelligence(MockUser())
    assert len(r) == 1

@pytest.mark.asyncio
async def test_create_project_skill_link(ms):
    _cfg(ms, [{"project_id": "p1", "skill_id": "s1"}])
    from database.schemas.skill import SkillProjectLinkCreate
    r = await create_project_skill_link(SkillProjectLinkCreate(project_id="p1", skill_id="s1"), MockUser())
    assert r["project_id"] == "p1"

@pytest.mark.asyncio
async def test_delete_project_skill_link(ms):
    _cfg(ms, [])
    r = await delete_project_skill_link("p1", "s1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_create_roadmap_skill_link(ms):
    _cfg(ms, [{"roadmap_id": "r1", "skill_id": "s1"}])
    from database.schemas.skill import SkillRoadmapLinkCreate
    r = await create_roadmap_skill_link(SkillRoadmapLinkCreate(roadmap_id="r1", skill_id="s1", phase="learning", target_level=3), MockUser())
    assert r["roadmap_id"] == "r1"

@pytest.mark.asyncio
async def test_delete_roadmap_skill_link(ms):
    _cfg(ms, [])
    r = await delete_roadmap_skill_link("r1", "s1", MockUser())
    assert r is None

@pytest.mark.asyncio
async def test_create_opportunity_skill_link(ms):
    _cfg(ms, [{"opportunity_id": "o1", "skill_id": "s1"}])
    from database.schemas.skill import SkillOpportunityLinkCreate
    r = await create_opportunity_skill_link(SkillOpportunityLinkCreate(opportunity_id="o1", skill_id="s1"), MockUser())
    assert r["opportunity_id"] == "o1"

@pytest.mark.asyncio
async def test_delete_opportunity_skill_link(ms):
    _cfg(ms, [])
    r = await delete_opportunity_skill_link("o1", "s1", MockUser())
    assert r is None


# ─── Parametrized 400 error tests (38 endpoints) ─────────────────────


def _build_400_cases():
    """Build parametrize tuples for all 400-error branches."""
    from database.schemas.skill import (
        SkillRelationshipCreate, TagCreate, SkillTagCreate,
        UserSkillAssessmentCreate, SkillActivityLogCreate,
        SkillRoadmapDefinitionCreate, SkillIncomeDataCreate,
        SkillCertificationCreate, SkillTopicCreate,
        SkillResourceCreate, SkillLearningPathCreate,
        SkillProjectLinkCreate, SkillRoadmapLinkCreate,
        SkillOpportunityLinkCreate, SkillExternalMappingCreate,
        SkillEventSubscriptionCreate,
        SkillMarketDataCreate, SkillExternalMappingUpdate,
    )
    return [
        # ── Delete with single ID ──
        (delete_category, ["1"]),
        (delete_skill, ["1"]),
        (delete_relationship, ["1"]),
        (delete_tag, ["1"]),
        (delete_user_skill, ["1"]),
        (delete_roadmap_definition, ["1"]),
        (delete_certification, ["1"]),
        (delete_topic, ["1"]),
        (delete_skill_resource, ["1"]),
        (delete_learning_path, ["1"]),
        (delete_external_mapping, ["1"]),
        # ── Create with single model ──
        (create_relationship, [SkillRelationshipCreate(from_skill_id="s1", to_skill_id="s2", relationship_type="related_to")]),
        (create_tag, [TagCreate(name="b", slug="b")]),
        (link_skill_tag, [SkillTagCreate(skill_id="s1", tag_id="t1")]),
        (create_assessment, [UserSkillAssessmentCreate(user_skill_id="u1", user_id="u", score=75, assessment_type="self")]),
        (log_activity, [SkillActivityLogCreate(user_id="u", activity_type="skill_added")]),
        (create_roadmap_definition, [SkillRoadmapDefinitionCreate(name="R")]),
        (create_income_data, [SkillIncomeDataCreate(skill_id="s1", source="employment", level=3)]),
        (create_certification, [SkillCertificationCreate(skill_id="s1", name="P", provider="I", level_mapped=3)]),
        (create_topic, [SkillTopicCreate(skill_id="s1", name="GA")]),
        (create_skill_resource, [SkillResourceCreate(skill_id="s1", title="T", resource_type="video")]),
        (create_learning_path, [SkillLearningPathCreate(name="P", target_skill_id="s1")]),
        (create_project_skill_link, [SkillProjectLinkCreate(project_id="p1", skill_id="s1")]),
        (create_roadmap_skill_link, [SkillRoadmapLinkCreate(roadmap_id="r1", skill_id="s1", phase="learning", target_level=3)]),
        (create_opportunity_skill_link, [SkillOpportunityLinkCreate(opportunity_id="o1", skill_id="s1")]),
        (create_external_mapping, [SkillExternalMappingCreate(skill_id="s1", external_system="linkedin", external_id="123", external_name="n")]),
        (create_event_subscription, [SkillEventSubscriptionCreate(name="W", url="https://example.com/hook")]),
        # ── accept_recommendation takes single ID ──
        (accept_recommendation, ["1"]),
        # ── Update with ID + model ──
        (update_roadmap_definition, ["1", SkillRoadmapDefinitionCreate(name="U")]),
        (update_market_data, ["1", SkillMarketDataCreate(skill_id="s1", demand_score=90, growth_score=10.0)]),
        (update_certification, ["1", SkillCertificationCreate(skill_id="s1", name="U", provider="I", level_mapped=3)]),
        (update_topic, ["1", SkillTopicCreate(skill_id="s1", name="U")]),
        (update_skill_resource, ["1", SkillResourceCreate(skill_id="s1", title="U", resource_type="video")]),
        (update_learning_path, ["1", SkillLearningPathCreate(name="U", target_skill_id="s1")]),
        (update_external_mapping, ["1", SkillExternalMappingUpdate(external_name="U")]),
        # ── Multi-ID delete ──
        (delete_project_skill_link, ["p1", "s1"]),
        (delete_roadmap_skill_link, ["r1", "s1"]),
        (delete_opportunity_skill_link, ["o1", "s1"]),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("func,args", _build_400_cases())
async def test_skills_400(ms, func, args):
    from fastapi import HTTPException
    _cfg(ms, [], "Error")
    with pytest.raises(HTTPException) as exc:
        await func(*args, MockUser())
    assert exc.value.status_code == 400


# ─── Parametrized 404 not-found tests (5 endpoints) ──────────────────


def _build_404_cases():
    """Build parametrize tuples for update endpoints that can 404."""
    from database.schemas.skill import (
        SkillCategoryUpdate, SkillUpdate, UserSkillUpdate,
        SkillResourceCreate, SkillLearningPathCreate,
    )
    return [
        (update_category, ["1", SkillCategoryUpdate(name="U")]),
        (update_skill, ["1", SkillUpdate(name="U")]),
        (update_user_skill, ["1", UserSkillUpdate(state="learning")]),
        (update_skill_resource, ["1", SkillResourceCreate(skill_id="s1", title="U", resource_type="video")]),
        (update_learning_path, ["1", SkillLearningPathCreate(name="U", target_skill_id="s1")]),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("func,args", _build_404_cases())
async def test_skills_404(ms, func, args):
    from fastapi import HTTPException
    _cfg(ms, [])
    with pytest.raises(HTTPException) as exc:
        await func(*args, MockUser())
    assert exc.value.status_code == 404
