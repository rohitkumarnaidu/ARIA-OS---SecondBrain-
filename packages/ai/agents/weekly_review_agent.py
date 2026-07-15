from datetime import datetime, timedelta
from typing import Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger
from shared.utils.upsert import upsert

REVIEW_PROFILES = {
    "balanced": {"name": "Balanced", "emphasis": "overall", "task_weight": 1.0, "course_weight": 1.0, "habit_weight": 1.0, "goal_weight": 1.0},
    "deep-focus": {"name": "Deep Focus", "emphasis": "deep_work", "task_weight": 1.5, "course_weight": 1.2, "habit_weight": 0.8, "goal_weight": 0.8},
    "backlog-buster": {"name": "Backlog Buster", "emphasis": "tasks", "task_weight": 2.0, "course_weight": 0.5, "habit_weight": 1.0, "goal_weight": 0.7},
    "skill-growth": {"name": "Skill Growth", "emphasis": "learning", "task_weight": 0.7, "course_weight": 2.0, "habit_weight": 0.8, "goal_weight": 1.3},
    "quick-check": {"name": "Quick Check", "emphasis": "morale", "task_weight": 0.5, "course_weight": 0.5, "habit_weight": 0.5, "goal_weight": 0.5},
}


async def apply_review_profile(user_id: str, profile_type: str = "balanced") -> dict:
    profile = REVIEW_PROFILES.get(profile_type, REVIEW_PROFILES["balanced"])
    return {
        "profile": profile,
        "profile_type": profile_type,
        "user_id": user_id,
        "applied_at": datetime.now().isoformat(),
    }


async def include_income_data(review: dict, user_id: str) -> dict:
    try:
        supabase = get_supabase_client()
        week_end = review.get("week_end", datetime.now().date().isoformat())
        week_start = review.get("week_start", (datetime.now().date() - timedelta(days=7)).isoformat())
        resp = supabase.from_("income_entries").select("amount, date, source").eq("user_id", user_id).gte("date", week_start).lte("date", week_end).execute()
        entries = resp.data or []
        total = sum(e.get("amount", 0) or 0 for e in entries)
        review["income"] = {
            "weekly_total": round(total, 2),
            "entry_count": len(entries),
            "entries": entries[:10],
        }
    except Exception as e:
        logger.warn("include_income_data failed", user_id=user_id, error=str(e))
        review["income"] = {"weekly_total": 0, "entry_count": 0, "entries": []}
    return review


async def include_sleep_data(review: dict, user_id: str) -> dict:
    try:
        supabase = get_supabase_client()
        week_end = review.get("week_end", datetime.now().date().isoformat())
        week_start = review.get("week_start", (datetime.now().date() - timedelta(days=7)).isoformat())
        resp = supabase.from_("sleep_logs").select("date, quality, duration_hours, sleep_debt_hours").eq("user_id", user_id).gte("date", week_start).lte("date", week_end).order("date", ascending=True).execute()
        logs = resp.data or []
        if logs:
            qualities = [l.get("quality", 0) for l in logs]
            avg_quality = sum(qualities) / len(qualities)
            total_debt = sum(l.get("sleep_debt_hours", 0) or 0 for l in logs)
            review["sleep"] = {
                "avg_quality": round(avg_quality, 1),
                "total_debt_hours": round(total_debt, 1),
                "logs_count": len(logs),
                "logs": logs,
            }
        else:
            review["sleep"] = {"avg_quality": 0, "total_debt_hours": 0, "logs_count": 0, "logs": []}
    except Exception as e:
        logger.warn("include_sleep_data failed", user_id=user_id, error=str(e))
        review["sleep"] = {"avg_quality": 0, "total_debt_hours": 0, "logs_count": 0, "logs": []}
    return review


async def deduplicate_review(user_id: str, week_start: str) -> bool:
    try:
        supabase = get_supabase_client()
        existing = supabase.from_("weekly_reviews").select("id").eq("user_id", user_id).eq("week_start", week_start).execute()
        return bool(existing.data)
    except Exception as e:
        logger.error("deduplicate_review check failed", user_id=user_id, week_start=week_start, error=str(e))
        return False


async def generate_weekly_review(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    week_end = datetime.now().date()
    week_start = week_end - timedelta(days=7)

    if await deduplicate_review(user_id, week_start.isoformat()):
        logger.info("Weekly review already exists", user_id=user_id, week_start=week_start.isoformat())
        existing = supabase.from_("weekly_reviews").select("*").eq("user_id", user_id).eq("week_start", week_start.isoformat()).execute()
        if existing.data:
            return existing.data[0]

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
    average_streak = 0
    if active_habits:
        streaks = [h.get("current_streak", 0) for h in habits if h.get("is_active")]
        if streaks:
            average_streak = int(sum(streaks) / len(streaks))

    completion_rate = round(completed / total * 100, 1) if total else 0

    review_prompt = prompts.get_agent("weekly_review_agent")
    if review_prompt:
        system = review_prompt.system_prompt
        user = (
            f"Weekly review data ({week_start} to {week_end}):\n"
            f"Tasks: {completed}/{total} completed ({completion_rate}%)\n"
            f"Courses: {course_status}\n"
            f"Active habits: {active_habits}, avg streak: {average_streak}\n"
            f"Active goals: {len(goals)}\n"
            f"Return JSON with: week_summary, achievements (array), "
            f"challenges (array), next_week_intention, morale."
        )
    else:
        system = "You are ARIA's weekly review analyst. Be honest and forward-looking."
        user = (
            f"Weekly stats: {completed}/{total} tasks done ({completion_rate}%), "
            f"{course_status}, {active_habits} habits (avg streak {average_streak}), {len(goals)} goals. "
            f"Return JSON with summary, achievements, challenges, next_week_intention."
        )

    try:
        ai_response = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        ai_response = {}

    review = {
        "user_id": user_id,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "tasks_completed": completed,
        "tasks_total": total,
        "completion_rate": completion_rate,
        "course_status": course_status,
        "active_habits": active_habits,
        "average_streak": average_streak,
        "summary": ai_response.get("week_summary", f"Completed {completed}/{total} tasks"),
        "achievements": ai_response.get("achievements", []),
        "challenges": ai_response.get("challenges", []),
        "next_week_intention": ai_response.get("next_week_intention", "Keep consistent"),
        "morale": ai_response.get("morale", "neutral"),
    }

    review = await include_income_data(review, user_id)
    review = await include_sleep_data(review, user_id)

    upsert("weekly_reviews", review, ["user_id", "week_start"])
    return review
