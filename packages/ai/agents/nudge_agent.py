from typing import Dict, Any, List
from datetime import datetime
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts

NUDGE_TYPES = ["course_behind", "habit_miss_2day", "habit_miss_5day", "multiple_courses_behind", "streak_at_risk"]


async def generate_nudge(user_id: str, nudge_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if nudge_type not in NUDGE_TYPES:
        return {"error": f"Unknown nudge type: {nudge_type}"}

    nudge_prompt = prompts.get_agent("nudge_agent")
    if nudge_prompt:
        system = nudge_prompt.system_prompt
        user = (
            f"Generate a nudge of type '{nudge_type}' with this context:\n"
            f"{context}\n"
            f"Return JSON with: nudge_text (2-3 sentences, empathetic and actionable), "
            f"smallest_action (one specific step), escalation (true if this is a repeat nudge)."
        )
    else:
        system = "You are a gentle accountability partner. Be empathetic and specific."
        user = f"Nudge type: {nudge_type}. Context: {context}. " f"Return JSON with nudge_text and smallest_action."

    try:
        result = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        result = {}
    return {
        "nudge_type": nudge_type,
        "generated_at": datetime.now().isoformat(),
        "nudge_text": result.get("nudge_text", "Time to check in on your progress!"),
        "smallest_action": result.get("smallest_action", "Spend 5 minutes on this today"),
        "escalation": result.get("escalation", False),
    }


async def check_course_nudges(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    courses = courses_resp.data or []

    nudges = []
    for course in courses:
        if course.get("progress", 0) < 30 and course.get("status") == "in_progress":
            nudge = await generate_nudge(
                user_id,
                "course_behind",
                {
                    "title": course.get("title"),
                    "progress_pct": course.get("progress", 0),
                    "days_since_last_activity": 3,
                },
            )
            nudges.append(nudge)
    return nudges


async def check_habit_streaks(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    habits_resp = supabase.from_("habits").select("*").eq("user_id", user_id).execute()
    habits = habits_resp.data or []

    nudges = []
    for habit in habits:
        if not habit.get("is_active"):
            continue
        streak = habit.get("current_streak", 0)
        if streak >= 7:
            nudge = await generate_nudge(
                user_id,
                "streak_at_risk",
                {
                    "name": habit.get("name"),
                    "current_streak": streak,
                    "best_streak": habit.get("best_streak", streak),
                },
            )
            nudges.append(nudge)
        elif habit.get("missed_days", 0) >= 5:
            nudge = await generate_nudge(
                user_id,
                "habit_miss_5day",
                {
                    "name": habit.get("name"),
                    "missed_days": habit.get("missed_days", 0),
                },
            )
            nudges.append(nudge)
        elif habit.get("missed_days", 0) >= 2:
            nudge = await generate_nudge(
                user_id,
                "habit_miss_2day",
                {
                    "name": habit.get("name"),
                    "missed_days": habit.get("missed_days", 0),
                },
            )
            nudges.append(nudge)
    return nudges


async def run_all_nudges(user_id: str) -> Dict[str, Any]:
    course_nudges = await check_course_nudges(user_id)
    habit_nudges = await check_habit_streaks(user_id)
    return {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "total_nudges": len(course_nudges) + len(habit_nudges),
        "course_nudges": course_nudges,
        "habit_nudges": habit_nudges,
    }
