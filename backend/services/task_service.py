from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def get_tasks_by_user(user_id: str, status: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("tasks").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def get_task_by_id(task_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("id", task_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def create_task(user_id: str, task_data: dict) -> dict:
    supabase = get_supabase_client()
    task_data["user_id"] = user_id
    task_data["status"] = "pending"
    task_data["missed_count"] = 0

    response = supabase.from_("tasks").insert(task_data).execute()
    return response.data[0] if response.data else None


def update_task(task_id: str, user_id: str, updates: dict) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .update(updates)
        .eq("id", task_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def complete_task(task_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .update({"status": "completed", "completed_at": datetime.now().isoformat()})
        .eq("id", task_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_overdue_tasks(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    now = datetime.now().isoformat()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .lt("due_date", now)
        .execute()
    )
    return response.data or []


def get_tasks_due_today(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()

    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .gte("due_date", today)
        .lt("due_date", tomorrow)
        .execute()
    )
    return response.data or []


def get_tasks_by_goal(user_id: str, goal_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("goal_id", goal_id)
        .execute()
    )
    return response.data or []


def get_tasks_by_project(user_id: str, project_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("project_id", project_id)
        .execute()
    )
    return response.data or []


def get_tasks_with_dependencies(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .neq("dependency_id", None)
        .execute()
    )
    return response.data or []


def get_dependent_tasks(dependency_task_id: str, user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("dependency_id", dependency_task_id)
        .execute()
    )
    return response.data or []
