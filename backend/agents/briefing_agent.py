from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.supabase import get_supabase_client


async def generate_daily_briefing(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    goals_resp = (
        supabase.from_("goals")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )
    courses_resp = (
        supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    )
    sleep_resp = (
        supabase.from_("sleep_entries")
        .select("*")
        .eq("user_id", user_id)
        .gte("date", today)
        .execute()
    )

    tasks = tasks_resp.data or []
    goals = goals_resp.data or []
    courses = courses_resp.data or []
    sleeps = sleep_resp.data or []

    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    pending_tasks.sort(
        key=lambda t: (
            {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(
                t.get("priority", "medium"), 2
            ),
            t.get("due_date", ""),
        )
    )
    top_3_tasks = pending_tasks[:3]

    sleep_score = 70
    if sleeps:
        avg_quality = sum(s.get("quality", 70) for s in sleeps) / len(sleeps)
        sleep_score = int(avg_quality)

    course_target = 0
    if courses:
        for course in courses:
            if course.get("status") == "in_progress" and course.get("target_date"):
                days_left = (
                    datetime.fromisoformat(course["target_date"]) - datetime.now()
                ).days
                if days_left > 0:
                    remaining = course.get("progress", 0)
                    course_target += max(0, remaining / days_left)
        course_target = int(course_target)

    productivity_score = calculate_productivity_score(tasks, sleep_score)

    brief = {
        "generated_at": datetime.now().isoformat(),
        "top_3_tasks": [
            {
                "title": t.get("title"),
                "priority": t.get("priority"),
                "estimated_minutes": t.get("estimated_minutes"),
            }
            for t in top_3_tasks
        ],
        "sleep_score": sleep_score,
        "productivity_score": productivity_score,
        "course_target_minutes": course_target,
        "active_goals": [
            {"title": g.get("title"), "progress": g.get("progress", 0)}
            for g in goals[:3]
        ],
        "aria_pick": generate_aria_pick(top_3_tasks, goals, courses, sleep_score),
    }

    supabase.from_("daily_briefings").insert(
        {
            "user_id": user_id,
            "date": today,
            "data": brief,
        }
    ).execute()

    return brief


def calculate_productivity_score(tasks: List[Dict], sleep_score: int) -> int:
    if not tasks:
        return 50

    completed = len([t for t in tasks if t.get("status") == "completed"])
    total = len(tasks)
    task_score = (completed / total) * 50 if total > 0 else 0

    sleep_factor = (sleep_score / 100) * 30

    pending = len([t for t in tasks if t.get("status") == "pending"])
    streak_factor = max(0, 20 - (pending * 2))

    score = int(task_score + sleep_factor + streak_factor)
    return min(100, max(0, score))


def generate_aria_pick(
    tasks: List[Dict], goals: List[Dict], courses: List[Dict], sleep_score: int
) -> Dict[str, str]:
    if not tasks:
        return {
            "title": "Add your first task",
            "reason": "Start building your productivity system",
        }

    top_task = tasks[0]

    if sleep_score < 60:
        reason = "Your sleep score is low. Focus on lighter tasks today."
    elif top_task.get("priority") == "urgent":
        reason = "This is urgent and needs your immediate attention."
    else:
        reason = f"Completing this will move you closer to your goals."

    return {"title": top_task.get("title"), "reason": reason}
