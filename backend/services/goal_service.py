from typing import Optional, List
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_goals_by_user(user_id: str, status: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("goals").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def get_active_goals(user_id: str) -> List[dict]:
    return get_goals_by_user(user_id, "active")


def create_goal(user_id: str, goal_data: dict) -> dict:
    supabase = get_supabase_client()
    goal_data["user_id"] = user_id
    goal_data["status"] = goal_data.get("status", "active")
    goal_data["progress"] = 0

    response = supabase.from_("goals").insert(goal_data).execute()
    return response.data[0] if response.data else None


def update_goal_progress(goal_id: str, user_id: str, progress: int) -> Optional[dict]:
    supabase = get_supabase_client()
    progress = min(100, max(0, progress))

    response = (
        supabase.from_("goals")
        .update({"progress": progress})
        .eq("id", goal_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def calculate_completion_date(goal_data: dict) -> Optional[datetime]:
    if not goal_data.get("target_date"):
        return None

    hours_per_day = goal_data.get("hours_per_day", 2)
    days_per_week = goal_data.get("days_per_week", 5)

    return datetime.fromisoformat(goal_data["target_date"])


def get_goals_with_upcoming_deadlines(user_id: str, days: int = 7) -> List[dict]:
    goals = get_active_goals(user_id)
    upcoming = []
    cutoff = datetime.now() + timedelta(days=days)

    for goal in goals:
        if goal.get("target_date"):
            target = datetime.fromisoformat(goal["target_date"])
            if target <= cutoff:
                upcoming.append(goal)

    return upcoming


def get_roadmap_types() -> List[str]:
    return [
        "career_skills",
        "business_launch",
        "exam_prep",
        "study_learning",
        "project",
        "health",
        "financial",
        "custom",
    ]


from datetime import timedelta
