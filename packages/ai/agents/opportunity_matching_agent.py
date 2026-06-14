from datetime import datetime
from typing import List, Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm
from ai.prompt_loader import prompts


async def match_opportunities(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()

    user_resp = supabase.from_("users").select("skills, interests, experience_level").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    opps_resp = supabase.from_("opportunities").select("*").eq("user_id", user_id).execute()
    existing_opps = opps_resp.data or []

    match_prompt = prompts.get_agent("opportunity_matching_agent")
    if match_prompt:
        system_prompt = match_prompt.system_prompt
        user_prompt = (
            f"Score and rank opportunities for:\n"
            f"Skills: {user_data.get('skills', [])}\n"
            f"Interests: {user_data.get('interests', [])}\n"
            f"Experience: {user_data.get('experience_level', 'beginner')}\n"
            f"Opportunities to rank: {len(existing_opps)}\n"
            f"Return JSON: recommendations (array of {opportunity_id, match_score, reasoning, action_tip})"
        )
    else:
        system_prompt = "You are an AI career matching assistant. Return only valid JSON."
        user_prompt = (
            f"User skills: {user_data.get('skills', [])}, "
            f"interests: {user_data.get('interests', [])}. "
            f"Score these opportunities by match quality: {existing_opps}. "
            f"Return JSON: recommendations array with opportunity_id, match_score, reasoning, action_tip."
        )

    ranked = await llm.generate_json(user_prompt, system=system_prompt)
    recommendations = ranked.get("recommendations", [])

    for rec in recommendations:
        supabase.from_("opportunities").update({
            "match_score": rec.get("match_score", 50),
            "match_reasoning": rec.get("reasoning", ""),
            "action_tip": rec.get("action_tip", ""),
            "last_matched": datetime.now().isoformat(),
        }).eq("id", rec.get("opportunity_id")).execute()

    return recommendations
