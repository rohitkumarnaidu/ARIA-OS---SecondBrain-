"""Tests for the Skill Pydantic schemas — validation, defaults, and enums."""

from database.schemas.skill import (
    SkillCreate,
    SkillCategoryCreate,
    SkillRelationshipCreate,
    TagCreate,
    UserSkillCreate,
    UserSkillEvidenceCreate,
    UserSkillTargetCreate,
    SkillMarketDataCreate,
    SkillCertificationCreate,
    SkillTopicCreate,
    SkillResourceCreate,
    SkillLearningPathCreate,
    SkillAIRecommendationCreate,
    SkillActivityLogCreate,
    SkillEventCreate,
    SkillForecastCreate,
    UserSkillState,
    EvidenceSourceType,
    RelationshipType,
    TargetPriority,
    Difficulty,
)


def test_skill_category_create():
    c = SkillCategoryCreate(name="Web Development", slug="web-dev")
    assert c.name == "Web Development"
    assert c.slug == "web-dev"
    assert c.is_active is True


def test_skill_create():
    s = SkillCreate(category_id="cat-1", name="React", slug="react")
    assert s.name == "React"
    assert s.level_min == 0
    assert s.level_max == 5
    assert s.aliases == []


def test_skill_relationship_create():
    r = SkillRelationshipCreate(from_skill_id="s1", to_skill_id="s2", relationship_type=RelationshipType.prerequisite)
    assert r.relationship_type == "prerequisite"
    assert r.weight == 1.0
    assert r.is_directed is True


def test_tag_create():
    t = TagCreate(name="Frontend", slug="frontend")
    assert t.name == "Frontend"


def test_user_skill_create():
    us = UserSkillCreate(user_id="u1", skill_id="s1")
    assert us.user_id == "u1"
    assert us.level == 0
    assert us.state == UserSkillState.learning


def test_user_skill_evidence_create():
    ev = UserSkillEvidenceCreate(
        user_skill_id="us-1",
        user_id="u1",
        source_type=EvidenceSourceType.github,
        title="PR Merged",
        signed_hash="abc123",
        collected_at=0,
    )
    assert ev.source_type == "github"
    assert ev.signed_hash == "abc123"


def test_user_skill_target_create():
    t = UserSkillTargetCreate(user_skill_id="us-1", user_id="u1", target_level=3)
    assert t.target_level == 3
    assert t.priority == TargetPriority.medium
    assert t.status.value == "active"


def test_skill_market_data_create():
    md = SkillMarketDataCreate(skill_id="s1", demand_score=85, growth_score=12.5)
    assert md.demand_score == 85
    assert md.growth_score == 12.5


def test_skill_certification_create():
    cert = SkillCertificationCreate(skill_id="s1", name="AWS Certified", provider="Amazon", level_mapped=3)
    assert cert.name == "AWS Certified"
    assert cert.quality_weight == 0.5


def test_skill_topic_create():
    t = SkillTopicCreate(skill_id="s1", name="React Hooks")
    assert t.name == "React Hooks"


def test_skill_resource_create():
    r = SkillResourceCreate(skill_id="s1", title="React Docs", resource_type="documentation")
    assert r.is_free is False
    assert r.difficulty == Difficulty.intermediate


def test_skill_learning_path_create():
    lp = SkillLearningPathCreate(target_skill_id="s1", name="React Mastery")
    assert lp.is_ai_generated is False
    assert lp.steps == []


def test_skill_ai_recommendation_create():
    rec = SkillAIRecommendationCreate(user_id="u1", recommendation_type="learn", skill_id="s1", reasoning="High demand")
    assert rec.priority == 0
    assert rec.source == "ai"


def test_skill_activity_log_create():
    act = SkillActivityLogCreate(user_id="u1", activity_type="skill_tree_viewed")
    assert act.activity_type.value == "skill_tree_viewed"


def test_event_create():
    ev = SkillEventCreate(event_type="skill.created", aggregate_type="skill", aggregate_id="s1", data={"name": "React"})
    assert ev.event_version == "1.0"


def test_forecast_create():
    f = SkillForecastCreate(skill_id="s1", metric="demand", forecast_date="2026-12-31", predicted_value=85.0)
    assert f.metric == "demand"
    assert f.model_version == "1.0"
