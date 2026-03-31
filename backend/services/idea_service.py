from typing import Optional, List
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_ideas(user_id: str, status: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("ideas").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", ascending=False).execute()
    return response.data or []


def create_idea(user_id: str, idea_data: dict) -> dict:
    supabase = get_supabase_client()
    idea_data["user_id"] = user_id
    idea_data["status"] = idea_data.get("status", "raw")

    response = supabase.from_("ideas").insert(idea_data).execute()
    return response.data[0] if response.data else None


def update_idea_status(idea_id: str, user_id: str, status: str) -> Optional[dict]:
    valid_statuses = ["raw", "researching", "validating", "building", "archived"]
    if status not in valid_statuses:
        return None

    supabase = get_supabase_client()
    response = (
        supabase.from_("ideas")
        .update({"status": status})
        .eq("id", idea_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_ideas_by_status_pipeline(user_id: str) -> dict:
    ideas = get_ideas(user_id)

    pipeline = {
        "raw": [],
        "researching": [],
        "validating": [],
        "building": [],
        "archived": [],
    }

    for idea in ideas:
        status = idea.get("status", "raw")
        if status in pipeline:
            pipeline[status].append(idea)

    return pipeline


def get_idea_count_by_status(user_id: str) -> dict:
    ideas = get_ideas(user_id)
    counts = {"raw": 0, "researching": 0, "validating": 0, "building": 0, "archived": 0}

    for idea in ideas:
        status = idea.get("status", "raw")
        if status in counts:
            counts[status] += 1

    return counts
