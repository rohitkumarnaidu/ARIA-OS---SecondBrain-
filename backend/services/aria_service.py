from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_user_context(user_id: str) -> dict:
    supabase = get_supabase_client()

    tasks_resp = (
        supabase.from_("tasks")
        .select("id, title, status, priority")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .execute()
    )
    goals_resp = (
        supabase.from_("goals")
        .select("id, title, progress, status")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )
    courses_resp = (
        supabase.from_("courses")
        .select("id, title, progress, status")
        .eq("user_id", user_id)
        .execute()
    )

    return {
        "pending_tasks": tasks_resp.data or [],
        "active_goals": goals_resp.data or [],
        "courses": courses_resp.data or [],
        "timestamp": datetime.now().isoformat(),
    }


def generate_aria_pick(user_id: str) -> dict:
    context = get_user_context(user_id)
    tasks = context.get("pending_tasks", [])

    if not tasks:
        return {"type": "empty", "message": "No pending tasks. Great job!"}

    tasks.sort(
        key=lambda t: {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(
            t.get("priority", "medium"), 2
        )
    )
    top_task = tasks[0]

    reason = get_task_priority_reason(top_task)

    return {
        "type": "task",
        "title": top_task.get("title"),
        "priority": top_task.get("priority"),
        "reason": reason,
    }


def get_task_priority_reason(task: dict) -> str:
    priority = task.get("priority", "medium")

    if priority == "urgent":
        return "This is urgent and needs your immediate attention."
    elif priority == "high":
        return "This is a high priority task that will move you forward."
    elif priority == "medium":
        return "This task fits well in your current schedule."
    else:
        return "This can be done when you have extra time."


def generate_daily_summary(user_id: str) -> dict:
    context = get_user_context(user_id)

    pending = len(context.get("pending_tasks", []))
    goals = len(context.get("active_goals", []))
    courses_in_progress = len(
        [c for c in context.get("courses", []) if c.get("status") == "in_progress"]
    )

    return {
        "pending_tasks": pending,
        "active_goals": goals,
        "courses_in_progress": courses_in_progress,
        "generated_at": datetime.now().isoformat(),
    }


def suggest_next_action(user_id: str) -> dict:
    context = get_user_context(user_id)
    tasks = context.get("pending_tasks", [])

    if not tasks:
        return {"action": "add_task", "message": "Add a new task to get started"}

    urgent_tasks = [t for t in tasks if t.get("priority") == "urgent"]
    if urgent_tasks:
        return {
            "action": "complete_task",
            "task": urgent_tasks[0],
            "message": f"Complete '{urgent_tasks[0].get('title')}'",
        }

    return {"action": "review_tasks", "message": "Review your pending tasks"}


def calculate_productivity_score(user_id: str) -> int:
    supabase = get_supabase_client()
    tasks_resp = (
        supabase.from_("tasks").select("status").eq("user_id", user_id).execute()
    )
    sleep_resp = (
        supabase.from_("sleep_entries")
        .select("quality")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(7)
        .execute()
    )

    tasks = tasks_resp.data or []
    sleeps = sleep_resp.data or []

    if not tasks:
        return 50

    completed = len([t for t in tasks if t.get("status") == "completed"])
    task_score = (completed / len(tasks)) * 50

    sleep_score = 0
    if sleeps:
        avg_quality = sum(s.get("quality", 70) for s in sleeps) / len(sleeps)
        sleep_score = (avg_quality / 100) * 30

    pending = len([t for t in tasks if t.get("status") == "pending"])
    streak_score = max(0, 20 - (pending * 2))

    return min(100, int(task_score + sleep_score + streak_score))
