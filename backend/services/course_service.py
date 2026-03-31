from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def get_courses_by_user(user_id: str, status: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("courses").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def create_course(user_id: str, course_data: dict) -> dict:
    supabase = get_supabase_client()
    course_data["user_id"] = user_id
    course_data["completed_videos"] = 0
    course_data["status"] = course_data.get("status", "not_started")

    response = supabase.from_("courses").insert(course_data).execute()
    return response.data[0] if response.data else None


def update_course_progress(
    course_id: str, user_id: str, completed_videos: int
) -> Optional[dict]:
    supabase = get_supabase_client()

    course_resp = (
        supabase.from_("courses").select("total_videos").eq("id", course_id).execute()
    )
    if not course_resp.data:
        return None

    total = course_resp.data[0].get("total_videos", 0)
    progress = (completed_videos / total * 100) if total > 0 else 0
    status = "completed" if completed_videos >= total else "in_progress"

    response = (
        supabase.from_("courses")
        .update(
            {
                "completed_videos": completed_videos,
                "progress": progress,
                "status": status,
            }
        )
        .eq("id", course_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def calculate_daily_minutes(course: dict) -> int:
    if not course.get("deadline") or course.get("completed_videos", 0) >= course.get(
        "total_videos", 0
    ):
        return 0

    days_left = max(
        1, (datetime.fromisoformat(course["deadline"]) - datetime.now()).days
    )
    remaining = course.get("total_videos", 0) - course.get("completed_videos", 0)
    return int((remaining * 15) / days_left)


def get_behind_schedule_courses(user_id: str) -> List[dict]:
    courses = get_courses_by_user(user_id, "in_progress")
    behind = []

    for course in courses:
        daily_minutes = calculate_daily_minutes(course)
        if daily_minutes > 60:
            behind.append({**course, "daily_minutes_needed": daily_minutes})

    return behind


def get_courses_by_platform(user_id: str, platform: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("courses")
        .select("*")
        .eq("user_id", user_id)
        .eq("platform", platform)
        .execute()
    )
    return response.data or []
