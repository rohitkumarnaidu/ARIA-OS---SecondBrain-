from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def get_time_entries(user_id: str, limit: int = 50) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("time_entries")
        .select("*")
        .eq("user_id", user_id)
        .order("start_time", ascending=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


def start_timer(
    user_id: str,
    description: str = "",
    task_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> dict:
    supabase = get_supabase_client()

    entry_data = {
        "user_id": user_id,
        "description": description or "Working...",
        "start_time": datetime.now().isoformat(),
        "is_deep_work": False,
    }

    if task_id:
        entry_data["task_id"] = task_id
    if project_id:
        entry_data["project_id"] = project_id

    response = supabase.from_("time_entries").insert(entry_data).execute()
    return response.data[0] if response.data else None


def stop_timer(entry_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()

    entry_resp = supabase.from_("time_entries").select("*").eq("id", entry_id).execute()
    if not entry_resp.data:
        return None

    entry = entry_resp.data[0]
    end_time = datetime.now()
    start_time = datetime.fromisoformat(entry["start_time"])

    duration_minutes = int((end_time - start_time).total_seconds() / 60)
    is_deep_work = duration_minutes >= 90

    response = (
        supabase.from_("time_entries")
        .update(
            {
                "end_time": end_time.isoformat(),
                "duration_minutes": duration_minutes,
                "is_deep_work": is_deep_work,
            }
        )
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_active_timer(user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("time_entries")
        .select("*")
        .eq("user_id", user_id)
        .is_("end_time", None)
        .execute()
    )
    return response.data[0] if response.data else None


def get_today_total(user_id: str) -> int:
    today = datetime.now().date().isoformat()
    entries = get_time_entries(user_id, 100)
    today_entries = [e for e in entries if e.get("start_time", "").startswith(today)]
    return sum(e.get("duration_minutes", 0) for e in today_entries)


def get_deep_work_today(user_id: str) -> int:
    today = datetime.now().date().isoformat()
    entries = get_time_entries(user_id, 100)
    deep_work = [
        e
        for e in entries
        if e.get("start_time", "").startswith(today) and e.get("is_deep_work")
    ]
    return sum(e.get("duration_minutes", 0) for e in deep_work)


def get_focus_hours(user_id: str, days: int = 30) -> List[dict]:
    entries = get_time_entries(user_id, 500)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    deep_work_entries = [
        e
        for e in entries
        if e.get("is_deep_work") and e.get("start_time", "") >= cutoff
    ]

    hour_counts = {}
    for entry in deep_work_entries:
        hour = datetime.fromisoformat(entry["start_time"]).hour
        hour_counts[hour] = hour_counts.get(hour, 0) + entry.get("duration_minutes", 0)

    return [
        {"hour": h, "minutes": m}
        for h, m in sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
    ]


def get_daily_breakdown(user_id: str, date: Optional[str] = None) -> dict:
    target_date = date or datetime.now().date().isoformat()
    entries = get_time_entries(user_id, 100)

    day_entries = [
        e for e in entries if e.get("start_time", "").startswith(target_date)
    ]

    by_category = {}
    for entry in day_entries:
        cat = entry.get("category", "work")
        by_category[cat] = by_category.get(cat, 0) + entry.get("duration_minutes", 0)

    return {
        "date": target_date,
        "total_minutes": sum(e.get("duration_minutes", 0) for e in day_entries),
        "by_category": by_category,
        "sessions": len(day_entries),
    }
