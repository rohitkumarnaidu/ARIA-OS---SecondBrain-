from typing import Dict, Any, List
from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger

NUDGE_TYPES = ["course_behind", "habit_miss_2day", "habit_miss_5day", "multiple_courses_behind", "streak_at_risk"]
NUDGE_ESCALATION_KEY = "nudge_escalation"


async def get_escalation_level(user_id: str, nudge_type: str) -> int:
    try:
        supabase = get_supabase_client()
        cutoff = (datetime.now() - timedelta(days=14)).isoformat()
        resp = supabase.from_("notifications").select("created_at").eq("user_id", user_id).eq("type", f"nudge_{nudge_type}").gte("created_at", cutoff).order("created_at", ascending=False).execute()
        recent = resp.data or []
        if len(recent) >= 5:
            return 3
        elif len(recent) >= 3:
            return 2
        elif len(recent) >= 1:
            return 1
        return 1
    except Exception as e:
        logger.error("get_escalation_level failed", user_id=user_id, nudge_type=nudge_type, error=str(e))
        return 1


async def combine_course_habit_digest(user_id: str) -> dict:
    try:
        supabase = get_supabase_client()
        courses_resp = supabase.from_("courses").select("title, progress, status").eq("user_id", user_id).execute()
        habits_resp = supabase.from_("habits").select("name, current_streak, missed_days, is_active").eq("user_id", user_id).execute()
        courses = courses_resp.data or []
        habits = habits_resp.data or []

        behind_courses = [c for c in courses if c.get("progress", 0) < 30 and c.get("status") == "in_progress"]
        active_habits = [h for h in habits if h.get("is_active")]
        at_risk_habits = [h for h in active_habits if h.get("missed_days", 0) >= 2]

        return {
            "total_courses": len(courses),
            "behind_courses": len(behind_courses),
            "behind_course_names": [c.get("title", "Untitled") for c in behind_courses[:5]],
            "total_habits": len(habits),
            "active_habits": len(active_habits),
            "at_risk_habits": len(at_risk_habits),
            "at_risk_habit_names": [h.get("name", "Untitled") for h in at_risk_habits[:5]],
            "average_streak": int(sum(h.get("current_streak", 0) for h in active_habits) / len(active_habits)) if active_habits else 0,
        }
    except Exception as e:
        logger.error("combine_course_habit_digest failed", user_id=user_id, error=str(e))
        return {"total_courses": 0, "behind_courses": 0, "total_habits": 0, "active_habits": 0, "at_risk_habits": 0}


async def check_notification_preferences(user_id: str, nudge_type: str) -> bool:
    try:
        supabase = get_supabase_client()
        resp = supabase.from_("users").select("notification_preferences").eq("id", user_id).execute()
        if not resp.data:
            return True
        prefs = resp.data[0].get("notification_preferences", {})
        if isinstance(prefs, str):
            import json
            try:
                prefs = json.loads(prefs)
            except (json.JSONDecodeError, TypeError):
                prefs = {}
        nudge_prefs = prefs.get("nudges", prefs.get(nudge_type, {}))
        if isinstance(nudge_prefs, dict):
            return nudge_prefs.get("enabled", True)
        return True
    except Exception as e:
        logger.warn("check_notification_preferences failed", user_id=user_id, error=str(e))
        return True


async def generate_positive_reinforcement(user_id: str) -> str:
    try:
        supabase = get_supabase_client()
        habits_resp = supabase.from_("habits").select("name, current_streak, best_streak").eq("user_id", user_id).execute()
        habits = habits_resp.data or []
        courses_resp = supabase.from_("courses").select("title, progress").eq("user_id", user_id).execute()
        courses = courses_resp.data or []

        messages: List[str] = []

        for h in habits:
            streak = h.get("current_streak", 0)
            best = h.get("best_streak", 0)
            if streak >= 30:
                messages.append(f"Incredible! You've maintained '{h.get('name')}' for {streak} days!")
            elif streak >= 14:
                messages.append(f"Awesome two-week streak on '{h.get('name')}'! Keep it going!")
            elif streak >= 7:
                messages.append(f"One week strong on '{h.get('name')}'! You're building a great habit.")
            elif streak > 0 and streak == best:
                messages.append(f"New personal best on '{h.get('name')}'! {streak} days and counting!")

        for c in courses:
            progress = c.get("progress", 0)
            if progress >= 90:
                messages.append(f"Almost done with '{c.get('title')}'! Just {100 - progress}% to go.")
            elif progress >= 50:
                messages.append(f"Halfway through '{c.get('title')}'! Great progress.")

        if not messages:
            return "You're doing great! Every small step counts toward your goals."

        return " ".join(messages[:2])
    except Exception as e:
        logger.error("generate_positive_reinforcement failed", user_id=user_id, error=str(e))
        return "You're doing great! Keep up the good work."


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

    escalation_level = await get_escalation_level(user_id, nudge_type)
    opt_out = await check_notification_preferences(user_id, nudge_type)

    return {
        "nudge_type": nudge_type,
        "generated_at": datetime.now().isoformat(),
        "nudge_text": result.get("nudge_text", "Time to check in on your progress!"),
        "smallest_action": result.get("smallest_action", "Spend 5 minutes on this today"),
        "escalation": result.get("escalation", False),
        "escalation_level": escalation_level,
        "notifications_allowed": opt_out,
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
    digest = await combine_course_habit_digest(user_id)
    reinforcement = await generate_positive_reinforcement(user_id)
    return {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "total_nudges": len(course_nudges) + len(habit_nudges),
        "course_nudges": course_nudges,
        "habit_nudges": habit_nudges,
        "combined_digest": digest,
        "positive_reinforcement": reinforcement,
    }
