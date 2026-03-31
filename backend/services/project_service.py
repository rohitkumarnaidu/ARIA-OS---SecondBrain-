from typing import Optional, List
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_projects(user_id: str, phase: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("projects").select("*").eq("user_id", user_id)

    if phase:
        query = query.eq("phase", phase)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def create_project(user_id: str, project_data: dict) -> dict:
    supabase = get_supabase_client()
    project_data["user_id"] = user_id
    project_data["phase"] = project_data.get("phase", "planning")

    response = supabase.from_("projects").insert(project_data).execute()
    return response.data[0] if response.data else None


def update_project_phase(project_id: str, user_id: str, phase: str) -> Optional[dict]:
    valid_phases = ["planning", "design", "build", "test", "launch", "maintain"]
    if phase not in valid_phases:
        return None

    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .update({"phase": phase})
        .eq("id", project_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def add_blocker(project_id: str, user_id: str, blocker: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .update({"blocker": blocker})
        .eq("id", project_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def resolve_blocker(project_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .update({"blocker": None})
        .eq("id", project_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_blocked_projects(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .select("*")
        .eq("user_id", user_id)
        .neq("blocker", None)
        .execute()
    )
    return response.data or []


def get_project_stats(user_id: str) -> dict:
    projects = get_projects(user_id)
    phases = {}

    for p in projects:
        phase = p.get("phase", "planning")
        phases[phase] = phases.get(phase, 0) + 1

    return {
        "total": len(projects),
        "by_phase": phases,
        "blocked": len([p for p in projects if p.get("blocker")]),
    }
