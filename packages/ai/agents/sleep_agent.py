from datetime import datetime
from typing import Dict, Any, Optional
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


async def analyze_sleep(user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
    supabase = get_supabase_client()
    target_date = date or datetime.now().date().isoformat()

    resp = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).eq("date", target_date).execute()
    logs = resp.data or []
    latest = logs[0] if logs else None

    week_resp = (
        supabase.from_("sleep_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(7)
        .execute()
    )
    week_logs = week_resp.data or []

    if not latest:
        return {
            "date": target_date,
            "has_data": False,
            "message": "No sleep data for this date.",
        }

    avg_quality = sum(log.get("quality", 0) for log in week_logs) / len(week_logs) if week_logs else 0

    sleep_prompt = prompts.get_agent("sleep_agent")
    if sleep_prompt:
        system = sleep_prompt.system_prompt
        user = (
            f"Analyze sleep data for {target_date}:\n"
            f"Score: {latest.get('quality')}\n"
            f"Duration: {latest.get('duration_hours')}h\n"
            f"Debt: {latest.get('sleep_debt_hours', 0)}h\n"
            f"7-day avg quality: {avg_quality:.0f}\n"
            f"Return JSON with: sleep_analysis, wind_down_routine (array of steps), "
            f"recommendations (array)."
        )
    else:
        system = "You are a sleep quality analyst. Provide concise, actionable insights."
        user = (
            f"Sleep score: {latest.get('quality')}/100, "
            f"duration: {latest.get('duration_hours')}h, "
            f"debt: {latest.get('sleep_debt_hours', 0)}h. "
            f"Return JSON with wind_down_routine and recommendations."
        )

    try:
        ai_response = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        ai_response = {}

    return {
        "date": target_date,
        "has_data": True,
        "score": latest.get("quality"),
        "duration_hours": latest.get("duration_hours"),
        "sleep_debt_hours": latest.get("sleep_debt_hours", 0),
        "seven_day_avg_quality": round(avg_quality, 1),
        "wind_down_routine": ai_response.get(
            "wind_down_routine",
            [
                "Dim lights 30 min before bed",
                "Put away phone 20 min before bed",
            ],
        ),
        "sleep_analysis": ai_response.get("sleep_analysis", "No analysis available"),
        "recommendations": ai_response.get(
            "recommendations",
            [
                "Maintain consistent sleep schedule",
            ],
        ),
    }


async def suggest_bedtime(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    resp = (
        supabase.from_("sleep_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(3)
        .execute()
    )
    recent = resp.data or []
    scores = [log.get("quality", 0) for log in recent]
    avg = sum(scores) / len(scores) if scores else 70

    if avg < 60:
        suggested_bedtime = "21:30"
    elif avg < 75:
        suggested_bedtime = "22:00"
    else:
        suggested_bedtime = "22:30"

    return {
        "suggested_bedtime": suggested_bedtime,
        "based_on_avg_quality": round(avg, 1),
        "message": f"Aim for bed by {suggested_bedtime} to maintain or improve your sleep quality.",
    }
