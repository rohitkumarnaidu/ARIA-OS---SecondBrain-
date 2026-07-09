from ai.context_assembly import ContextSection
from config.core.supabase import get_supabase_client
from ai.agents.memory_agent import get_memory_summary


async def _fetch_tasks(user_id: str):
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("tasks")
            .select("title, status, priority, due_date")
            .eq("user_id", user_id)
            .eq("status", "pending")
            .order("priority")
            .limit(10)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


async def _fetch_goals(user_id: str):
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("goals")
            .select("title, status, progress")
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(5)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


async def _fetch_courses(user_id: str):
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("courses")
            .select("title, status, progress_percent")
            .eq("user_id", user_id)
            .limit(5)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


async def _fetch_habits(user_id: str):
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("habits")
            .select("name, current_streak, is_active")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .limit(5)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


async def _fetch_sleep(user_id: str):
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("sleep_logs")
            .select("sleep_score, duration_hours, date")
            .eq("user_id", user_id)
            .order("date", ascending=False)
            .limit(3)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


async def _fetch_memory(user_id: str):
    try:
        return await get_memory_summary(user_id)
    except Exception:
        return {}


def _fmt_tasks(data):
    if not data:
        return "No pending tasks."
    return "\n".join(f"- {t['title']} (priority: {t.get('priority', 'med')})" for t in data)


def _fmt_goals(data):
    if not data:
        return "No active goals."
    return "\n".join(f"- {g['title']} ({g.get('progress', 0)}%)" for g in data)


def _fmt_courses(data):
    active = [c for c in data if c.get("status") == "in_progress"]
    if not active:
        return "No courses in progress."
    return "\n".join(f"- {c['title']} ({c.get('progress_percent', 0)}%)" for c in active)


def _fmt_habits(data):
    if not data:
        return "No active habits."
    return "\n".join(f"- {h['name']} (streak: {h.get('current_streak', 0)}d)" for h in data)


def _fmt_sleep(data):
    if not data:
        return "No sleep data yet."
    latest = data[0]
    return f"Last sleep: score {latest.get('sleep_score', 'N/A')}/100, {latest.get('duration_hours', 0)}h"


def _fmt_memory(data):
    if isinstance(data, dict):
        summary = data.get("summary", "No memory summary.")
        return f"Memory: {summary}"
    return "No memory data."


def register_default_sections():
    import ai.context_assembly as ca

    ca.SECTIONS.clear()
    ca.SECTIONS.extend(
        [
            ContextSection("tasks", 800, 1, _fetch_tasks, _fmt_tasks, "No pending tasks."),
            ContextSection("goals", 500, 2, _fetch_goals, _fmt_goals, "No active goals."),
            ContextSection("courses", 500, 3, _fetch_courses, _fmt_courses, "No courses in progress."),
            ContextSection("habits", 400, 4, _fetch_habits, _fmt_habits, "No active habits."),
            ContextSection("sleep", 300, 5, _fetch_sleep, _fmt_sleep, "No sleep data."),
            ContextSection("memory", 400, 6, _fetch_memory, _fmt_memory, "No memory data."),
        ]
    )
