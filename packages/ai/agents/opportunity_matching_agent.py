import asyncio
from datetime import datetime
from typing import List, Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger


def compute_algorithmic_score(opportunity: dict, user_skills: List[str], user_goals: List[dict]) -> float:
    score = 0.0

    opp_skills = opportunity.get("skills_needed", opportunity.get("skills", []))
    if user_skills and opp_skills:
        us = set(s.strip().lower() for s in user_skills if s)
        them = set(s.strip().lower() for s in opp_skills if s)
        if us and them:
            overlap = len(us & them) / len(them)
            score += overlap * 40

    if user_goals:
        opp_categories = {
            opportunity.get("category", "").lower(),
            opportunity.get("title", "").lower(),
            opportunity.get("description", "").lower(),
        }
        max_alignment = 0.0
        for goal in user_goals:
            goal_text = (goal.get("title", "") + " " + goal.get("description", "")).lower()
            match_count = sum(1 for word in goal_text.split() if word in opp_categories and len(word) > 3)
            alignment = min(match_count / 5, 1.0)
            max_alignment = max(max_alignment, alignment)
        score += max_alignment * 30

    exp_level = (opportunity.get("experience_level") or "").lower()
    user_exp = (opportunity.get("user_experience") or "beginner").lower()
    exp_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
    exp_diff = abs(exp_map.get(user_exp, 0) - exp_map.get(exp_level, 0))
    if exp_diff == 0:
        score += 20
    elif exp_diff == 1:
        score += 10
    else:
        score += 5

    score += 10

    return round(min(score, 100), 1)


def identify_skill_gaps(opportunity: dict, user_skills: List[str]) -> List[str]:
    opp_skills = opportunity.get("skills_needed", opportunity.get("skills", []))
    if not opp_skills:
        return []
    us = set(s.strip().lower() for s in user_skills if s)
    gaps = []
    for skill in opp_skills:
        if skill.strip().lower() not in us:
            gaps.append(skill.strip())
    return gaps


def calculate_goal_alignment(opportunity: dict, goals: List[dict]) -> float:
    if not goals:
        return 0.0
    opp_text = (
        (opportunity.get("title") or "") + " " +
        (opportunity.get("description") or "") + " " +
        (opportunity.get("category") or "")
    ).lower()
    match_count = 0
    for goal in goals:
        goal_text = ((goal.get("title") or "") + " " + (goal.get("description") or "")).lower()
        goal_words = set(w for w in goal_text.split() if len(w) > 3)
        opp_words = set(w for w in opp_text.split() if len(w) > 3)
        overlap = len(goal_words & opp_words)
        if overlap >= 2:
            match_count += 1
    return round(min(match_count / len(goals), 1.0), 2) if match_count > 0 else 0.0


async def match_opportunities(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()

    user_resp = supabase.from_("users").select("skills, interests, experience_level, goals").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    user_skills = user_data.get("skills", [])
    user_goals_data = user_data.get("goals", [])
    if isinstance(user_goals_data, list):
        user_goals = [{"title": g, "description": g} for g in user_goals_data if isinstance(g, str)]
    else:
        user_goals = []

    goals_resp = supabase.from_("goals").select("title, description").eq("user_id", user_id).eq("status", "active").execute()
    if goals_resp.data:
        user_goals.extend(goals_resp.data)

    opps_resp = supabase.from_("opportunities").select("*").eq("user_id", user_id).execute()
    existing_opps = opps_resp.data or []

    match_prompt = prompts.get_agent("opportunity_matching_agent")
    if match_prompt:
        system_prompt = match_prompt.system_prompt
        user_prompt = (
            f"Score and rank opportunities for:\n"
            f"Skills: {user_skills}\n"
            f"Experience: {user_data.get('experience_level', 'beginner')}\n"
            f"Opportunities to rank: {len(existing_opps)}\n"
            f"Return JSON: recommendations (array of {{opportunity_id, match_score, reasoning, action_tip}})"
        )
    else:
        system_prompt = "You are an AI career matching assistant. Return only valid JSON."
        user_prompt = (
            f"User skills: {user_skills}. "
            f"Score these opportunities by match quality: {existing_opps}. "
            f"Return JSON: recommendations array with opportunity_id, match_score, reasoning, action_tip."
        )

    try:
        llm_task = asyncio.wait_for(
            llm.generate_json(user_prompt, system=system_prompt),
            timeout=8,
        )
        ranked = await llm_task
    except (LLMProviderUnavailableError, asyncio.TimeoutError):
        logger.warn("LLM unavailable or timed out for opportunity matching, using algorithmic scoring")
        ranked = {"recommendations": []}
        if existing_opps:
            for opp in existing_opps:
                alg_score = compute_algorithmic_score(opp, user_skills, user_goals)
                gaps = identify_skill_gaps(opp, user_skills)
                goal_align = calculate_goal_alignment(opp, user_goals)
                ranked["recommendations"].append({
                    "opportunity_id": opp.get("id"),
                    "match_score": alg_score,
                    "reasoning": f"Algorithmic score: {alg_score}/100. Skill gaps: {gaps[:3]}",
                    "action_tip": "Review and apply" if alg_score > 60 else "Consider upskilling",
                    "skill_gaps": gaps,
                    "goal_alignment": goal_align,
                })

    recommendations = ranked.get("recommendations", [])

    for rec in recommendations:
        opp_id = rec.get("opportunity_id")
        if opp_id:
            supabase.from_("opportunities").update(
                {
                    "match_score": rec.get("match_score", 50),
                    "match_reasoning": rec.get("reasoning", ""),
                    "action_tip": rec.get("action_tip", ""),
                    "skill_gaps": rec.get("skill_gaps", []),
                    "goal_alignment": rec.get("goal_alignment", 0),
                    "last_matched": datetime.now().isoformat(),
                }
            ).eq("id", opp_id).execute()

    return recommendations
