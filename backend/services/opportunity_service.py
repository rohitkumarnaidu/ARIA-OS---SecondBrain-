from typing import Optional, List
from datetime import datetime
from app.core.supabase import get_supabase_client


def get_opportunities(user_id: str, category: Optional[str] = None) -> List[dict]:
    supabase = get_supabase_client()
    query = supabase.from_("opportunities").select("*").eq("user_id", user_id)

    if category:
        query = query.eq("category", category)

    response = query.order("match_score", ascending=False).execute()
    return response.data or []


def get_upcoming_opportunities(user_id: str, days: int = 7) -> List[dict]:
    supabase = get_supabase_client()
    cutoff = datetime.now().isoformat()

    response = (
        supabase.from_("opportunities")
        .select("*")
        .eq("user_id", user_id)
        .gt("deadline", cutoff)
        .order("deadline", ascending=True)
        .limit(20)
        .execute()
    )
    return response.data or []


def get_critical_opportunities(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    now = datetime.now()
    two_days_later = (now + datetime.timedelta(days=2)).isoformat()

    response = (
        supabase.from_("opportunities")
        .select("*")
        .eq("user_id", user_id)
        .lt("deadline", two_days_later)
        .order("match_score", ascending=False)
        .execute()
    )
    return response.data or []


def save_opportunity(user_id: str, opportunity_data: dict) -> dict:
    supabase = get_supabase_client()
    opportunity_data["user_id"] = user_id
    opportunity_data["discovered_at"] = datetime.now().isoformat()

    response = supabase.from_("opportunities").insert(opportunity_data).execute()
    return response.data[0] if response.data else None


def mark_opportunity_actioned(opportunity_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("opportunities")
        .update({"actioned": True, "actioned_at": datetime.now().isoformat()})
        .eq("id", opportunity_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_opportunities_by_category(user_id: str) -> dict:
    opportunities = get_opportunities(user_id)
    categories = {}

    for opp in opportunities:
        cat = opp.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    return categories
