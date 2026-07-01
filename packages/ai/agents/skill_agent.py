"""SkillAgent domain controller with 9 sub-agents for the skills system.

Sub-agents:
  SK-01: AssessmentAgent  - Skill level assessment & gap analysis
  SK-02: RecommendationAgent - Skill recommendation engine
  SK-03: IntelligenceAgent - Market intelligence & skill health
  SK-04: RoadmapAgent - Learning path generation
  SK-05: EvidenceAgent - Evidence verification & scoring
  SK-06: CareerAgent - Career readiness & path optimization
  SK-07: MarketAgent - Market demand & income analysis
  SK-08: GraphAgent - Skill graph traversal & pathfinding
  SK-09: OpportunityAgent - Opportunity-to-skill matching
"""

from datetime import datetime
from typing import Dict, Any, Optional
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


# ---- SK-01: Assessment Agent ----


async def assess_user_skill(user_skill_id: str, user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    us_resp = supabase.from_("user_skills").select("*").eq("user_skill_id", user_skill_id).eq("user_id", user_id).execute()
    if not us_resp.data:
        return {"error": "User skill not found", "fallback": True}

    us = us_resp.data[0]
    skill_resp = supabase.from_("skills").select("name, description, level_min, level_max").eq("skill_id", us["skill_id"]).execute()
    skill = skill_resp.data[0] if skill_resp.data else {}

    evidence_resp = supabase.from_("user_skill_evidence").select("*").eq("user_skill_id", user_skill_id).eq("user_id", user_id).execute()
    evidence = evidence_resp.data or []

    assessment_prompt = prompts.get_agent("skill_assessment_agent")
    if assessment_prompt:
        system = assessment_prompt.system_prompt
        user = (
            f"Assess skill level for user:\n"
            f"Skill: {skill.get('name', 'Unknown')}\n"
            f"Current Level: {us.get('level', 0)}/5\n"
            f"State: {us.get('state', 'unknown')}\n"
            f"Confidence Score: {us.get('confidence_score', 0)}\n"
            f"Evidence Items: {len(evidence)}\n"
            f"Evidence Summary: {[(e.get('source_type') or 'unknown') + ': ' + (e.get('title') or '')[:50] for e in evidence[:5]]}\n"
            f"Return JSON with: recommended_level, confidence_adjustment, gap_analysis, next_milestones."
        )
    else:
        system = "You are a skill assessment AI. Return only valid JSON."
        user = f"Assess skill '{skill.get('name', 'Unknown')}' at level {us.get('level', 0)} with {len(evidence)} evidence items."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_assessment(us, evidence)

    return {
        "user_skill_id": user_skill_id,
        "skill_name": skill.get("name"),
        "current_level": us.get("level"),
        "recommended_level": result.get("recommended_level", us.get("level")),
        "confidence_adjustment": result.get("confidence_adjustment", 0),
        "gap_analysis": result.get("gap_analysis", []),
        "next_milestones": result.get("next_milestones", []),
        "evidence_count": len(evidence),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_assessment(us: dict, evidence: list) -> dict:
    level = us.get("level", 0)
    evidence_count = len(evidence)
    confidence = us.get("confidence_score", 0.5)
    if evidence_count >= 3 and confidence < 0.8:
        confidence = min(1.0, confidence + 0.1)
    return {
        "recommended_level": level,
        "confidence_adjustment": round(confidence - us.get("confidence_score", 0.5), 2),
        "gap_analysis": ["Complete more assessments for accurate gap analysis"],
        "next_milestones": [f"Gather evidence to progress from level {level} to {min(5, level + 1)}"],
    }


# ---- SK-02: Recommendation Agent ----


async def recommend_skills(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    user_resp = supabase.from_("users").select("skills, interests, career_goal").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    us_resp = supabase.from_("user_skills").select("skill_id, level, state").eq("user_id", user_id).execute()
    current_skills = us_resp.data or []
    current_skill_ids = [s["skill_id"] for s in current_skills]

    all_skills_resp = supabase.from_("skills").select("skill_id, name, category_id, skill_health").limit(200).execute()
    all_skills = all_skills_resp.data or []

    candidates = [s for s in all_skills if s["skill_id"] not in current_skill_ids]

    recommendation_prompt = prompts.get_agent("skill_recommendation_agent")
    if recommendation_prompt:
        system = recommendation_prompt.system_prompt
        user = (
            f"Recommend skills for user:\n"
            f"Existing Skills: {user_data.get('skills', [])}\n"
            f"Interests: {user_data.get('interests', [])}\n"
            f"Career Goal: {user_data.get('career_goal', 'Not specified')}\n"
            f"Current Skill Count: {len(current_skills)}\n"
            f"Available to Learn: {len(candidates)} skills\n"
            f"Top Candidate Names: {[s['name'] for s in candidates[:20]]}\n"
            "Return JSON with: recommendations (array of {skill_id, name, reason, priority}), focus_area, estimated_time."
        )
    else:
        system = "You are a skill recommendation AI. Return only valid JSON."
        user = f"User has skills: {user_data.get('skills', [])}. Career goal: {user_data.get('career_goal', 'N/A')}."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_recommendation(candidates, user_data)

    return {
        "user_id": user_id,
        "recommendations": result.get("recommendations", []),
        "focus_area": result.get("focus_area", "General"),
        "estimated_time": result.get("estimated_time", "3 months"),
        "candidate_count": len(candidates),
        "current_skill_count": len(current_skills),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_recommendation(candidates: list, user_data: dict) -> dict:
    top = candidates[:5] if candidates else []
    return {
        "recommendations": [
            {"skill_id": s.get("skill_id"), "name": s.get("name"), "reason": "Recommended based on market demand", "priority": i + 1}
            for i, s in enumerate(top)
        ],
        "focus_area": user_data.get("career_goal", "General"),
        "estimated_time": "3 months",
    }


# ---- SK-03: Intelligence Agent ----


async def refresh_skill_intelligence(skill_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    market_resp = supabase.from_("skill_market_data").select("*").eq("skill_id", skill_id).execute()
    market_data = market_resp.data[0] if market_resp.data else {}

    intelligence_prompt = prompts.get_agent("skill_intelligence_agent")
    if intelligence_prompt:
        system = intelligence_prompt.system_prompt
        user = (
            f"Analyze intelligence for skill:\n"
            f"Skill ID: {skill_id}\n"
            f"Demand Score: {market_data.get('demand_score', 'N/A')}\n"
            f"Growth Score: {market_data.get('growth_score', 'N/A')}\n"
            f"Salary Median: {market_data.get('salary_median', 'N/A')}\n"
            f"Competition: {market_data.get('competition_score', 'N/A')}\n"
            f"Future Relevance: {market_data.get('future_relevance', 'N/A')}\n"
            f"Return JSON with: health_score, trends, recommendations."
        )
    else:
        system = "You are a skill intelligence analyst. Return only valid JSON."
        user = f"Analyze skill {skill_id} market intelligence data."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = {"health_score": market_data.get("skill_health"), "trends": [], "recommendations": []}

    return {
        "skill_id": skill_id,
        "health_score": result.get("health_score", market_data.get("skill_health")),
        "trends": result.get("trends", []),
        "recommendations": result.get("recommendations", []),
        "data_freshness": market_data.get("data_freshness", "unknown"),
        "generated_at": datetime.now().isoformat(),
    }


# ---- SK-04: Roadmap Agent ----


async def generate_skill_roadmap(user_id: str, target_skill_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    skill_resp = supabase.from_("skills").select("name, description, level_max").eq("skill_id", target_skill_id).execute()
    skill = skill_resp.data[0] if skill_resp.data else {}

    us_resp = supabase.from_("user_skills").select("level, state").eq("user_id", user_id).eq("skill_id", target_skill_id).execute()
    user_skill = us_resp.data[0] if us_resp.data else {"level": 0}

    roadmap_prompt = prompts.get_agent("skill_roadmap_agent")
    if roadmap_prompt:
        system = roadmap_prompt.system_prompt
        user = (
            f"Generate learning roadmap:\n"
            f"Skill: {skill.get('name', 'Unknown')}\n"
            f"Description: {skill.get('description', '')}\n"
            f"Current Level: {user_skill.get('level', 0)}/5\n"
            f"Target Level: {skill.get('level_max', 5)}/5\n"
            "Return JSON with: phases (array of {phase_name, skills_to_learn, resources, estimated_hours, milestones}), total_estimated_hours, difficulty."
        )
    else:
        system = "You are a learning roadmap generator. Return only valid JSON."
        user = f"Generate roadmap for {skill.get('name', 'skill')} from level {user_skill.get('level', 0)} to {skill.get('level_max', 5)}."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_roadmap(skill, user_skill)

    return {
        "user_id": user_id,
        "skill_name": skill.get("name"),
        "current_level": user_skill.get("level"),
        "phases": result.get("phases", []),
        "total_estimated_hours": result.get("total_estimated_hours", 0),
        "difficulty": result.get("difficulty", "intermediate"),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_roadmap(skill: dict, user_skill: dict) -> dict:
    current = user_skill.get("level", 0)
    phases = []
    phase_names = ["Foundation", "Core", "Intermediate", "Advanced", "Expert"]
    for i in range(current, min(5, skill.get("level_max", 5))):
        if i < len(phase_names):
            phases.append({
                "phase_name": phase_names[i],
                "skills_to_learn": [f"{skill.get('name', 'Skill')} - {phase_names[i]}"],
                "estimated_hours": (i + 1) * 20,
                "milestones": [f"Complete {phase_names[i]} level"],
            })
    return {"phases": phases, "total_estimated_hours": sum(p.get("estimated_hours", 0) for p in phases), "difficulty": "intermediate"}


# ---- SK-05: Evidence Agent ----


async def verify_evidence(evidence_id: str, user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    ev_resp = supabase.from_("user_skill_evidence").select("*").eq("evidence_id", evidence_id).eq("user_id", user_id).execute()
    if not ev_resp.data:
        return {"error": "Evidence not found", "fallback": True}
    evidence = ev_resp.data[0]

    evidence_prompt = prompts.get_agent("skill_evidence_agent")
    if evidence_prompt:
        system = evidence_prompt.system_prompt
        user = (
            f"Verify evidence item:\n"
            f"Title: {evidence.get('title')}\n"
            f"Source Type: {evidence.get('source_type')}\n"
            f"URL: {evidence.get('url', 'None')}\n"
            f"Description: {evidence.get('description', '')[:200]}\n"
            f"Current State: {evidence.get('state')}\n"
            f"Signed Hash: {evidence.get('signed_hash')}\n"
            f"Return JSON with: verification_decision, confidence_score, trust_score, quality_score, reasoning."
        )
    else:
        system = "You are an evidence verification AI. Return only valid JSON."
        user = f"Verify evidence: {evidence.get('title')} (type: {evidence.get('source_type')})"

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_evidence(evidence)

    return {
        "evidence_id": evidence_id,
        "title": evidence.get("title"),
        "verification_decision": result.get("verification_decision", "pending"),
        "confidence_score": result.get("confidence_score", evidence.get("quality_score")),
        "trust_score": result.get("trust_score", evidence.get("trust_score")),
        "quality_score": result.get("quality_score", evidence.get("quality_score")),
        "reasoning": result.get("reasoning", "Algorithmic verification"),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_evidence(evidence: dict) -> dict:
    source_type = evidence.get("source_type", "")
    auto_verify_sources = {"github", "certification", "opensource", "assessment"}
    decision = "verified_auto" if source_type in auto_verify_sources else "pending_verification"
    return {
        "verification_decision": decision,
        "confidence_score": 0.7 if decision == "verified_auto" else 0.3,
        "trust_score": 0.8 if decision == "verified_auto" else 0.4,
        "quality_score": 0.6,
        "reasoning": f"Auto-verified based on source type '{source_type}'",
    }


# ---- SK-06: Career Agent ----


async def analyze_career_readiness(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    user_resp = supabase.from_("users").select("skills, career_goal, interests").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    us_resp = supabase.from_("user_skills").select("skill_id, level, state").eq("user_id", user_id).execute()
    user_skills = us_resp.data or []

    career_prompt = prompts.get_agent("skill_career_agent")
    if career_prompt:
        system = career_prompt.system_prompt
        user = (
            f"Analyze career readiness:\n"
            f"Career Goal: {user_data.get('career_goal', 'Not specified')}\n"
            f"Skills: {user_data.get('skills', [])}\n"
            f"Interests: {user_data.get('interests', [])}\n"
            f"Tracked Skills: {len(user_skills)}\n"
            f"Avg Level: {sum(s.get('level', 0) for s in user_skills) / max(len(user_skills), 1):.1f}\n"
            f"Return JSON with: readiness_score, strengths, gaps, recommended_career_paths, action_items."
        )
    else:
        system = "You are a career readiness analyst. Return only valid JSON."
        user = f"Analyze readiness for: {user_data.get('career_goal', 'N/A')}"

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_career(user_data, user_skills)

    return {
        "user_id": user_id,
        "career_goal": user_data.get("career_goal"),
        "readiness_score": result.get("readiness_score", 0),
        "strengths": result.get("strengths", []),
        "gaps": result.get("gaps", []),
        "recommended_paths": result.get("recommended_career_paths", []),
        "action_items": result.get("action_items", []),
        "skill_count": len(user_skills),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_career(user_data: dict, user_skills: list) -> dict:
    avg_level = sum(s.get("level", 0) for s in user_skills) / max(len(user_skills), 1) if user_skills else 0
    return {
        "readiness_score": round(avg_level / 5 * 100, 1),
        "strengths": [s["skill_id"] for s in user_skills if s.get("level", 0) >= 3][:5],
        "gaps": ["Define career goal for detailed gap analysis"],
        "recommended_career_paths": [user_data.get("career_goal", "General")],
        "action_items": ["Add more skills to your profile", "Complete skill assessments"],
    }


# ---- SK-07: Market Agent ----


async def analyze_market_trends(skill_id: Optional[str] = None) -> Dict[str, Any]:
    supabase = get_supabase_client()
    if skill_id:
        market_resp = supabase.from_("skill_market_data").select("*").eq("skill_id", skill_id).execute()
    else:
        market_resp = supabase.from_("skill_market_data").select("*").order("skill_health", desc=True).limit(20).execute()
    market_data = market_resp.data or []

    market_prompt = prompts.get_agent("skill_market_agent")
    if market_prompt:
        system = market_prompt.system_prompt
        user = (
            f"Analyze market trends:\n"
            f"Skills Analyzed: {len(market_data)}\n"
            f"Top Skills: {[m.get('skill_id') for m in market_data[:5]]}\n"
            f"Return JSON with: market_overview, top_demand_skills, growth_opportunities, salary_insights, recommendations."
        )
    else:
        system = "You are a market intelligence analyst. Return only valid JSON."
        user = f"Analyze trends for {len(market_data)} skills."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = algorithmic_fallback_market(market_data)

    return {
        "skill_count": len(market_data),
        "market_overview": result.get("market_overview", {}),
        "top_demand_skills": result.get("top_demand_skills", []),
        "growth_opportunities": result.get("growth_opportunities", []),
        "salary_insights": result.get("salary_insights", []),
        "recommendations": result.get("recommendations", []),
        "generated_at": datetime.now().isoformat(),
    }


def algorithmic_fallback_market(market_data: list) -> dict:
    return {
        "market_overview": {"total_tracked": len(market_data)},
        "top_demand_skills": [m.get("skill_id") for m in sorted(market_data, key=lambda x: x.get("demand_score", 0), reverse=True)[:5]],
        "growth_opportunities": [m.get("skill_id") for m in sorted(market_data, key=lambda x: x.get("growth_score", 0), reverse=True)[:3]],
        "salary_insights": {"median_range": "Market data available for tracked skills"},
        "recommendations": ["Focus on high-demand skills with low competition"],
    }


# ---- SK-08: Graph Agent ----


async def explore_skill_graph(skill_id: str, max_depth: int = 2) -> Dict[str, Any]:
    supabase = get_supabase_client()
    skill_resp = supabase.from_("skills").select("name, category_id").eq("skill_id", skill_id).execute()
    skill = skill_resp.data[0] if skill_resp.data else {}

    rel_resp = supabase.from_("skill_relationships").select("*").or_(f"from_skill_id.eq.{skill_id},to_skill_id.eq.{skill_id}").execute()
    relationships = rel_resp.data or []

    prerequisites = [r for r in relationships if r.get("relationship_type") == "prerequisite"]
    related = [r for r in relationships if r.get("relationship_type") in ("related_to", "similar_to", "complementary")]

    return {
        "skill_id": skill_id,
        "skill_name": skill.get("name"),
        "prerequisites": len(prerequisites),
        "related_skills": len(related),
        "relationship_count": len(relationships),
        "relationships": [
            {
                "from": r.get("from_skill_id"),
                "to": r.get("to_skill_id"),
                "type": r.get("relationship_type"),
                "weight": r.get("weight"),
            }
            for r in relationships
        ],
        "generated_at": datetime.now().isoformat(),
    }


# ---- SK-09: Opportunity Agent ----


async def match_skill_opportunities(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    us_resp = supabase.from_("user_skills").select("skill_id, level").eq("user_id", user_id).execute()
    user_skills = us_resp.data or []
    user_skill_ids = [s["skill_id"] for s in user_skills]

    opp_resp = supabase.from_("opportunities").select("*").eq("user_id", user_id).execute()
    opportunities = opp_resp.data or []

    skill_opp_resp = supabase.from_("skill_opportunities").select("*").execute()
    skill_opps = skill_opp_resp.data or []

    matches = []
    for opp in opportunities:
        required_skills = [so for so in skill_opps if so["opportunity_id"] == opp.get("id")]
        matched = 0
        for rs in required_skills:
            if rs["skill_id"] in user_skill_ids:
                us = next((s for s in user_skills if s["skill_id"] == rs["skill_id"]), None)
                if us and us["level"] >= rs.get("min_level", 1):
                    matched += 1
        match_pct = round(matched / max(len(required_skills), 1) * 100, 1) if required_skills else 0
        matches.append({"opportunity_id": opp.get("id"), "title": opp.get("title"), "match_pct": match_pct, "matched_skills": matched, "required_skills": len(required_skills)})

    return {
        "user_id": user_id,
        "total_opportunities": len(opportunities),
        "matches": sorted(matches, key=lambda x: x["match_pct"], reverse=True),
        "generated_at": datetime.now().isoformat(),
    }
