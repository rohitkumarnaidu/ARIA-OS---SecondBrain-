"""Tests for the SkillAgent module — all 9 sub-agents with fallback, error, and happy paths."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from ai.client import LLMProviderUnavailableError


def _mock_builder(data=None):
    b = MagicMock()
    b.execute.return_value = MagicMock(data=data or [], error=None)
    for m in ("select", "eq", "order", "limit", "range", "or_"):
        getattr(b, m).return_value = b
    b.insert.return_value = MagicMock(execute=MagicMock(return_value=MagicMock(data=[{"id": "mock-id"}], error=None)))
    b.update.return_value = b
    return b


@pytest.mark.asyncio
async def test_assess_user_skill_not_found():
    from ai.agents.skill_agent import assess_user_skill
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        mock.return_value.from_.return_value = _mock_builder([])
        result = await assess_user_skill("nonexistent", "user-1")
        assert result.get("fallback") is True


@pytest.mark.asyncio
async def test_assess_user_skill_happy_path():
    from ai.agents.skill_agent import assess_user_skill
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        client = MagicMock()
        client.from_.return_value = _mock_builder([
            {"user_skill_id": "us-1", "skill_id": "sk-1", "level": 2, "state": "practicing", "confidence_score": 0.6, "evidence_score": 0.5}
        ])
        mock.return_value = client
        result = await assess_user_skill("us-1", "user-1")
        assert result.get("user_skill_id") == "us-1"


@pytest.mark.asyncio
async def test_assess_user_skill_fallback():
    from ai.agents.skill_agent import assess_user_skill
    with patch("ai.agents.skill_agent.get_supabase_client") as mock, \
         patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("AI down")):
        client = MagicMock()
        client.from_.return_value = _mock_builder([
            {"user_skill_id": "us-1", "skill_id": "sk-1", "level": 2, "state": "practicing", "confidence_score": 0.6, "evidence_score": 0.5}
        ])
        mock.return_value = client
        result = await assess_user_skill("us-1", "user-1")
        assert "gap_analysis" in result


@pytest.mark.asyncio
async def test_recommend_skills():
    from ai.agents.skill_agent import recommend_skills
    with patch("ai.agents.skill_agent.get_supabase_client") as mock, \
         patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("AI down")):
        client = MagicMock()
        skills_data = _mock_builder([{"skill_id": "s1", "name": "Python", "category_id": "c1", "skill_health": 85}])
        user_skills_data = _mock_builder([])
        user_data = _mock_builder([{"skills": ["JavaScript"], "interests": ["Web Dev"], "career_goal": "Full Stack"}])
        def side_effect(table):
            if table == "users":
                return user_data
            elif table == "user_skills":
                return user_skills_data
            return skills_data
        client.from_.side_effect = side_effect
        mock.return_value = client
        result = await recommend_skills("user-1")
        assert "recommendations" in result


@pytest.mark.asyncio
async def test_generate_skill_roadmap():
    from ai.agents.skill_agent import generate_skill_roadmap
    with patch("ai.agents.skill_agent.get_supabase_client") as mock, \
         patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("AI down")):
        client = MagicMock()
        client.from_.return_value = _mock_builder([
            {"skill_id": "sk-1", "name": "React", "description": "UI library", "level_max": 5}
        ])
        mock.return_value = client
        result = await generate_skill_roadmap("user-1", "sk-1")
        assert "phases" in result
        assert result.get("skill_name") == "React"


@pytest.mark.asyncio
async def test_verify_evidence_not_found():
    from ai.agents.skill_agent import verify_evidence
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        mock.return_value.from_.return_value = _mock_builder([])
        result = await verify_evidence("ev-1", "user-1")
        assert result.get("fallback") is True


@pytest.mark.asyncio
async def test_verify_evidence_happy():
    from ai.agents.skill_agent import verify_evidence
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        client = MagicMock()
        client.from_.return_value = _mock_builder([
            {"evidence_id": "ev-1", "title": "GitHub PR Merged", "source_type": "github", "url": "https://github.com", "description": "Merged a PR", "state": "raw", "signed_hash": "abc123", "quality_score": 0.0, "trust_score": 0.0}
        ])
        mock.return_value = client
        result = await verify_evidence("ev-1", "user-1")
        assert "verification_decision" in result


@pytest.mark.asyncio
async def test_analyze_career_readiness():
    from ai.agents.skill_agent import analyze_career_readiness
    with patch("ai.agents.skill_agent.get_supabase_client") as mock, \
         patch("ai.agents.skill_agent.llm.generate_json", side_effect=LLMProviderUnavailableError("AI down")):
        client = MagicMock()
        user_data = _mock_builder([{"skills": ["Python", "JS"], "career_goal": "Engineer", "interests": ["AI"]}])
        us_data = _mock_builder([{"skill_id": "s1", "level": 3, "state": "active"}])
        def side_effect(table):
            if table == "users":
                return user_data
            return us_data
        client.from_.side_effect = side_effect
        mock.return_value = client
        result = await analyze_career_readiness("user-1")
        assert "readiness_score" in result


@pytest.mark.asyncio
async def test_analyze_market_trends():
    from ai.agents.skill_agent import analyze_market_trends
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        mock.return_value.from_.return_value = _mock_builder([
            {"skill_id": "s1", "demand_score": 90, "growth_score": 15, "salary_median": 120000, "skill_health": 85}
        ])
        result = await analyze_market_trends()
        assert result.get("skill_count") == 1


@pytest.mark.asyncio
async def test_explore_skill_graph():
    from ai.agents.skill_agent import explore_skill_graph
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        mock.return_value.from_.return_value = _mock_builder([
            {"relationship_id": "r1", "from_skill_id": "s1", "to_skill_id": "s2", "relationship_type": "prerequisite", "weight": 0.9}
        ])
        result = await explore_skill_graph("s1")
        assert result.get("skill_id") == "s1"
        assert result.get("relationship_count") == 1


@pytest.mark.asyncio
async def test_match_skill_opportunities():
    from ai.agents.skill_agent import match_skill_opportunities
    with patch("ai.agents.skill_agent.get_supabase_client") as mock:
        client = MagicMock()
        us_data = _mock_builder([{"skill_id": "s1", "level": 3}])
        opp_data = _mock_builder([{"id": "opp-1", "title": "Web Dev Project"}])
        skill_opp_data = _mock_builder([{"opportunity_id": "opp-1", "skill_id": "s1", "min_level": 2}])
        def side_effect(table):
            if table == "user_skills":
                return us_data
            elif table == "opportunities":
                return opp_data
            return skill_opp_data
        client.from_.side_effect = side_effect
        mock.return_value = client
        result = await match_skill_opportunities("user-1")
        assert result.get("total_opportunities") == 1
