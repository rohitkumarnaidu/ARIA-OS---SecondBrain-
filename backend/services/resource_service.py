from typing import Optional, List
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_resources(user_id: str, resource_type: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("resources").select("*").eq("user_id", user_id)

    if resource_type:
        query = query.eq("type", resource_type)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def create_resource(user_id: str, resource_data: dict) -> dict:
    supabase = get_supabase_client()
    resource_data["user_id"] = user_id

    response = supabase.from_("resources").insert(resource_data).execute()
    return response.data[0] if response.data else None


def update_resource_notes(resource_id: str, user_id: str, notes: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .update({"notes": notes})
        .eq("id", resource_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def search_resources(user_id: str, query: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .select("*")
        .eq("user_id", user_id)
        .or_(f"title.ilike.%{query}%,description.ilike.%{query}%,notes.ilike.%{query}%")
        .execute()
    )
    return response.data or []


def get_reading_queue(user_id: str, goal_id: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = (
        supabase.from_("resources")
        .select("*")
        .eq("user_id", user_id)
        .eq("in_queue", True)
    )

    if goal_id:
        query = query.eq("goal_id", goal_id)

    response = query.order("priority", ascending=True).execute()
    return response.data or []


def add_to_reading_queue(
    resource_id: str, user_id: str, priority: int = 5
) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .update({"in_queue": True, "priority": priority})
        .eq("id", resource_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_resources_by_type(user_id: str) -> dict:
    resources = get_resources(user_id)
    types = {}

    for r in resources:
        r_type = r.get("type", "other")
        types[r_type] = types.get(r_type, 0) + 1

    return types
