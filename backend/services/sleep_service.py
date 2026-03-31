from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def log_sleep(user_id: str, bedtime: str, wake_time: str, quality: int = 70) -> dict:
    supabase = get_supabase_client()

    bedtime_dt = datetime.fromisoformat(bedtime)
    wake_dt = datetime.fromisoformat(wake_time)
    duration_hours = (wake_dt - bedtime_dt).total_seconds() / 3600

    sleep_data = {
        "user_id": user_id,
        "bedtime": bedtime,
        "wake_time": wake_time,
        "duration_hours": round(duration_hours, 2),
        "quality": quality,
        "date": wake_dt.date().isoformat(),
    }

    response = supabase.from_("sleep_entries").insert(sleep_data).execute()
    return response.data[0] if response.data else None


def get_sleep_entries(user_id: str, days: int = 7) -> List[dict]:
    supabase = get_supabase_client()
    cutoff = (datetime.now() - timedelta(days=days)).date().isoformat()

    response = (
        supabase.from_("sleep_entries")
        .select("*")
        .eq("user_id", user_id)
        .gte("date", cutoff)
        .order("date", ascending=False)
        .execute()
    )
    return response.data or []


def calculate_sleep_score(entry: dict) -> int:
    duration = entry.get("duration_hours", 0)
    quality = entry.get("quality", 70)

    if duration >= 7 and duration <= 9:
        duration_score = 50
    elif duration >= 6:
        duration_score = 40
    elif duration >= 5:
        duration_score = 25
    else:
        duration_score = 10

    quality_score = (quality / 100) * 50

    return min(100, int(duration_score + quality_score))


def get_average_sleep_quality(user_id: str, days: int = 7) -> float:
    entries = get_sleep_entries(user_id, days)
    if not entries:
        return 0

    total = sum(calculate_sleep_score(e) for e in entries)
    return round(total / len(entries), 1)


def calculate_sleep_debt(user_id: str) -> dict:
    entries = get_sleep_entries(user_id, 30)

    if not entries:
        return {"debt_hours": 0, "status": "healthy"}

    ideal_hours = 8 * len(entries)
    actual_hours = sum(e.get("duration_hours", 0) for e in entries)
    debt = ideal_hours - actual_hours

    status = "healthy" if debt <= 0 else "moderate" if debt <= 5 else "severe"

    return {"debt_hours": round(debt, 1), "status": status}
