from datetime import datetime
from typing import Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger
from shared.utils.upsert import upsert

DAY_PROFILES = {
    0: {"name": "Focus", "theme": "deep_work", "emphasis": "Most important task", "energy": "high"},
    1: {"name": "DeepWork", "theme": "deep_work", "emphasis": "Complex problem-solving", "energy": "high"},
    2: {"name": "Collaboration", "theme": "collaboration", "emphasis": "Meetings and teamwork", "energy": "medium"},
    3: {"name": "Review", "theme": "review", "emphasis": "Progress and reflection", "energy": "medium"},
    4: {"name": "Wrap-up", "theme": "completion", "emphasis": "Finish outstanding tasks", "energy": "medium"},
    5: {"name": "Explore", "theme": "learning", "emphasis": "New skills and ideas", "energy": "low"},
    6: {"name": "Plan", "theme": "planning", "emphasis": "Week ahead preparation", "energy": "low"},
}


def generate_day_profile(day_of_week: int) -> dict:
    profile = DAY_PROFILES.get(day_of_week, DAY_PROFILES[0])
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {
        "day_index": day_of_week,
        "day_name": day_names[day_of_week] if 0 <= day_of_week < 7 else "Unknown",
        "profile_name": profile["name"],
        "theme": profile["theme"],
        "emphasis": profile["emphasis"],
        "energy": profile["energy"],
    }


async def include_opportunity_data(briefing: dict, user_id: str) -> dict:
    try:
        supabase = get_supabase_client()
        now = datetime.now().isoformat()
        opps_resp = supabase.from_("opportunities").select("title, url, match_score, deadline, category").eq("user_id", user_id).gte("match_score", 70).limit(3).execute()
        opportunities = opps_resp.data or []
        briefing["top_opportunities"] = [
            {
                "title": o.get("title"),
                "score": o.get("match_score"),
                "category": o.get("category"),
                "deadline": o.get("deadline"),
            }
            for o in opportunities
        ]
    except Exception as e:
        logger.warn("include_opportunity_data failed", user_id=user_id, error=str(e))
        briefing["top_opportunities"] = []
    return briefing


async def include_habit_data(briefing: dict, user_id: str) -> dict:
    try:
        supabase = get_supabase_client()
        habits_resp = supabase.from_("habits").select("name, current_streak, best_streak, is_active").eq("user_id", user_id).execute()
        habits = habits_resp.data or []
        active = [h for h in habits if h.get("is_active")]
        briefing["habits"] = {
            "active_count": len(active),
            "total": len(habits),
            "streaks": [
                {"name": h.get("name"), "current_streak": h.get("current_streak", 0), "best_streak": h.get("best_streak", 0)}
                for h in active[:5]
            ],
            "longest_streak": max((h.get("current_streak", 0) for h in active), default=0),
        }
    except Exception as e:
        logger.warn("include_habit_data failed", user_id=user_id, error=str(e))
        briefing["habits"] = {"active_count": 0, "total": 0, "streaks": [], "longest_streak": 0}
    return briefing


async def deduplicate_briefing(user_id: str, date: str) -> bool:
    try:
        supabase = get_supabase_client()
        existing = supabase.from_("daily_briefings").select("id").eq("user_id", user_id).eq("date", date).execute()
        return bool(existing.data)
    except Exception as e:
        logger.error("deduplicate_briefing check failed", user_id=user_id, date=date, error=str(e))
        return False


async def generate_daily_briefing(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    today = datetime.now().date().isoformat()
    day_of_week = datetime.now().weekday()
    day_profile = generate_day_profile(day_of_week)

    if await deduplicate_briefing(user_id, today):
        logger.info("Briefing already exists for today", user_id=user_id, date=today)
        existing = supabase.from_("daily_briefings").select("data").eq("user_id", user_id).eq("date", today).execute()
        if existing.data:
            return existing.data[0].get("data", existing.data[0])

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    goals_resp = supabase.from_("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    sleep_resp = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).gte("date", today).execute()

    tasks = tasks_resp.data or []
    goals = goals_resp.data or []
    courses = courses_resp.data or []
    sleeps = sleep_resp.data or []

    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    pending_tasks.sort(
        key=lambda t: (
            {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(t.get("priority", "medium"), 2),
            t.get("due_date", ""),
        )
    )
    top_3_tasks = pending_tasks[:3]

    sleep_score = 70
    if sleeps:
        avg_quality = sum(t.get("quality", 70) for t in sleeps) / len(sleeps)
        sleep_score = int(avg_quality)

    completed = len([t for t in tasks if t.get("status") == "completed"])
    total_tasks = len(tasks)
    productivity_score = int((completed / total_tasks * 50 if total_tasks else 0) + (sleep_score / 100 * 30))

    briefing_prompt = prompts.get_agent("briefing_agent")
    if briefing_prompt:
        system_prompt = briefing_prompt.system_prompt
        user_prompt = (
            f"Generate a daily briefing with this context:\n"
            f"- Day: {day_profile['day_name']} ({day_profile['profile_name']} profile)\n"
            f"- {len(pending_tasks)} pending tasks, {len(goals)} active goals\n"
            f"- Sleep score: {sleep_score}/100\n"
            f"- {len(courses)} courses\n"
            f"- Top tasks: {[t['title'] for t in top_3_tasks[:3]]}\n"
            f"- Goals: {[g['title'] for g in goals[:3]]}\n"
            f"- Day theme: {day_profile['theme']}, emphasis: {day_profile['emphasis']}\n"
            f"Return JSON with: greeting, focus_today, task_reminder, tone, timestamp."
        )
    else:
        system_prompt = "You are ARIA, a personal AI productivity assistant. Be concise and motivating."
        user_prompt = (
            f"User has {len(pending_tasks)} pending tasks, {len(goals)} active goals, "
            f"sleep score {sleep_score}/100, {len(courses)} courses. "
            f"Top tasks: {[t['title'] for t in top_3_tasks[:3]]}. "
            f"Day: {day_profile['day_name']} - theme: {day_profile['theme']}. "
            f"Generate a brief JSON response with: aria_pick (title and reason), "
            f"productivity_tip, and focus_area."
        )

    try:
        ai_response = await llm.generate_json(user_prompt, system=system_prompt)
    except LLMProviderUnavailableError:
        ai_response = {}

    brief = {
        "generated_at": datetime.now().isoformat(),
        "day_profile": day_profile,
        "top_3_tasks": [
            {"title": t.get("title"), "priority": t.get("priority"), "estimated_minutes": t.get("estimated_minutes")}
            for t in top_3_tasks
        ],
        "sleep_score": sleep_score,
        "productivity_score": productivity_score,
        "active_goals": [{"title": g.get("title"), "progress": g.get("progress", 0)} for g in goals[:3]],
        "aria_pick": ai_response.get(
            "aria_pick",
            {
                "title": top_3_tasks[0]["title"] if top_3_tasks else "Start your day",
                "reason": "Focus on what matters most",
            },
        ),
        "productivity_tip": ai_response.get("productivity_tip", "Break big tasks into smaller chunks"),
        "focus_area": ai_response.get("focus_area", "Clear your pending tasks first"),
    }

    brief = await include_opportunity_data(brief, user_id)
    brief = await include_habit_data(brief, user_id)

    upsert("daily_briefings", {"user_id": user_id, "date": today, "data": brief}, ["user_id", "date"])
    return brief
