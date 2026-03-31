from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


async def track_user_progress(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    courses_resp = (
        supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    )
    habits_resp = supabase.from_("habits").select("*").eq("user_id", user_id).execute()

    tasks = tasks_resp.data or []
    courses = courses_resp.data or []
    habits = habits_resp.data or []

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_tasks = [t for t in tasks if t.get("created_at", "") >= week_ago]
    completed_tasks = [
        t
        for t in tasks
        if t.get("status") == "completed" and t.get("completed_at", "") >= week_ago
    ]

    learning_progress = {
        "tasks_created": len(recent_tasks),
        "tasks_completed": len(completed_tasks),
        "completion_rate": round(len(completed_tasks) / len(recent_tasks) * 100, 1)
        if recent_tasks
        else 0,
        "courses_enrolled": len(
            [c for c in courses if c.get("status") in ["not_started", "in_progress"]]
        ),
        "courses_completed": len(
            [c for c in courses if c.get("status") == "completed"]
        ),
        "active_habits": len([h for h in habits if h.get("is_active")]),
    }

    supabase.from_("learning_progress").insert(
        {
            "user_id": user_id,
            "date": datetime.now().date().isoformat(),
            "data": learning_progress,
        }
    ).execute()

    return learning_progress


async def detect_learning_patterns(user_id: str) -> List[str]:
    progress = await track_user_progress(user_id)
    patterns = []

    if progress["completion_rate"] >= 80:
        patterns.append("High productivity - completing most tasks started")
    elif progress["completion_rate"] < 50:
        patterns.append(
            "Task completion rate is low - consider breaking tasks into smaller steps"
        )

    if progress["courses_completed"] > 0 and progress["courses_enrolled"] > 3:
        patterns.append(
            "Enrolled in many courses - focus on completing existing ones first"
        )

    return patterns


async def suggest_learning_focus(user_id: str) -> Dict[str, Any]:
    patterns = await detect_learning_patterns(user_id)

    suggestions = {"patterns": patterns, "recommendations": []}

    if "Task completion rate is low" in patterns:
        suggestions["recommendations"].append("Start with one task at a time")
        suggestions["recommendations"].append(
            "Use the Pomodoro technique for focused work"
        )

    return suggestions
