from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def get_income_sources(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("income")
        .select("*")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .execute()
    )
    return response.data or []


def add_income(user_id: str, income_data: dict) -> dict:
    supabase = get_supabase_client()
    income_data["user_id"] = user_id

    response = supabase.from_("income").insert(income_data).execute()
    return response.data[0] if response.data else None


def calculate_total_income(user_id: str, days: Optional[int] = None) -> float:
    sources = get_income_sources(user_id)

    if days:
        cutoff = (datetime.now() - timedelta(days=days)).date().isoformat()
        sources = [s for s in sources if s.get("date", "") >= cutoff]

    return sum(s.get("amount", 0) for s in sources)


def calculate_hourly_rate(income_entry: dict) -> float:
    hours = income_entry.get("hours_spent", 0)
    amount = income_entry.get("amount", 0)

    if hours <= 0:
        return 0

    return round(amount / hours, 2)


def get_income_by_source(user_id: str, source: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("income")
        .select("*")
        .eq("user_id", user_id)
        .eq("source", source)
        .order("date", ascending=False)
        .execute()
    )
    return response.data or []


def get_income_milestones(user_id: str) -> dict:
    total = calculate_total_income(user_id)

    milestones = [
        {"target": 1000, "achieved": total >= 1000},
        {"target": 5000, "achieved": total >= 5000},
        {"target": 10000, "achieved": total >= 10000},
        {"target": 50000, "achieved": total >= 50000},
    ]

    current = None
    for m in milestones:
        if not m["achieved"]:
            current = m["target"]
            break

    return {"total": total, "milestones": milestones, "next_milestone": current}


def get_weekly_income_stats(user_id: str) -> dict:
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    sources = get_income_sources(user_id)
    weekly = [s for s in sources if s.get("date", "") >= week_ago]

    by_source = {}
    for s in weekly:
        source = s.get("source", "other")
        by_source[source] = by_source.get(source, 0) + s.get("amount", 0)

    return {
        "total": sum(s.get("amount", 0) for s in weekly),
        "by_source": by_source,
        "entries_count": len(weekly),
    }
