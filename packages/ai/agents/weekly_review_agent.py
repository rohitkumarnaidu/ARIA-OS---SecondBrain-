from datetime import datetime, timedelta
from typing import Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm
from ai.prompt_loader import prompts


async def generate_weekly_review(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    week_end = datetime.now().date()
    week_start = week_end - timedelta(days=7)

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    habits_resp = supabase.from_("habits").select("*").eq("user_id", user_id).execute()
    goals_resp = supabase.from_("goals").select("*").eq("user_id", user_id).execute()

    tasks = tasks_resp.data or []
    courses = courses_resp.data or []
    habits = habits_resp.data or []
    goals = goals_resp.data or []

    week_tasks = [t for t in tasks if t.get("created_at", "")[:10] >= week_start.isoformat()]
    completed = len([t for t in week_tasks if t.get("status") == "completed"])
    total = len(week_tasks)

    course_status = {}
    for c in courses:
        cs = c.get("status", "not_started")
        course_status[cs] = course_status.get(cs, 0) + 1

    active_habits = len([h for h in habits if h.get("is_active")])

    review_prompt = prompts.get_agent("weekly_review_agent")
    if review_prompt:
        system = review_prompt.system_prompt
        user = (
            f"Weekly review data ({week_start} to {week_end}):\n"
            f"Tasks: {completed}/{total} completed\n"
            f"Courses: {course_status}\n"
            f"Active habits: {active_habits}\n"
            f"Active goals: {len(goals)}\n"
            f"Return JSON with: week_summary, achievements (array), "
            f"challenges (array), next_week_intention, morale."
        )
    else:
        system = "You are ARIA's weekly review analyst. Be honest and forward-looking."
        user = (
            f"Weekly stats: {completed}/{total} tasks done, "
            f"{course_status}, {active_habits} habits, {len(goals)} goals. "
            f"Return JSON with summary, achievements, challenges, next_week_intention."
        )

    ai_response = await llm.generate_json(user, system=system)

    review = {
        "user_id": user_id,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "tasks_completed": completed,
        "tasks_total": total,
        "completion_rate": round(completed / total * 100, 1) if total else 0,
        "course_status": course_status,
        "active_habits": active_habits,
        "summary": ai_response.get("week_summary", f"Completed {completed}/{total} tasks"),
        "achievements": ai_response.get("achievements", []),
        "challenges": ai_response.get("challenges", []),
        "next_week_intention": ai_response.get("next_week_intention", "Keep consistent"),
        "morale": ai_response.get("morale", "neutral"),
    }

    supabase.from_("weekly_reviews").insert(review).execute()
    return review
