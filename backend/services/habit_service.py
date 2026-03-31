from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def get_habits_by_user(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("habits")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data or []


def create_habit(user_id: str, habit_data: dict) -> dict:
    supabase = get_supabase_client()
    habit_data["user_id"] = user_id
    habit_data["is_active"] = True
    habit_data["current_streak"] = 0
    habit_data["best_streak"] = 0
    habit_data["consistency_percentage"] = 0

    response = supabase.from_("habits").insert(habit_data).execute()
    return response.data[0] if response.data else None


def log_habit_completion(habit_id: str, user_id: str) -> Optional[dict]:
    supabase = get_supabase_client()

    habit_resp = supabase.from_("habits").select("*").eq("id", habit_id).execute()
    if not habit_resp.data:
        return None

    habit = habit_resp.data[0]
    today = datetime.now().date().isoformat()

    existing_log = (
        supabase.from_("habit_logs")
        .select("*")
        .eq("habit_id", habit_id)
        .eq("date", today)
        .execute()
    )
    if existing_log.data:
        return {"message": "Already logged today"}

    supabase.from_("habit_logs").insert(
        {"habit_id": habit_id, "user_id": user_id, "date": today}
    ).execute()

    new_streak = habit.get("current_streak", 0) + 1
    best_streak = max(habit.get("best_streak", 0), new_streak)

    logs_resp = (
        supabase.from_("habit_logs").select("id").eq("habit_id", habit_id).execute()
    )
    total_logs = len(logs_resp.data or [])
    last_30_days = (datetime.now() - timedelta(days=30)).date().isoformat()
    recent_logs = (
        supabase.from_("habit_logs")
        .select("id")
        .eq("habit_id", habit_id)
        .gte("date", last_30_days)
        .execute()
    )
    consistency = (len(recent_logs.data or []) / 30 * 100) if total_logs > 0 else 0

    response = (
        supabase.from_("habits")
        .update(
            {
                "current_streak": new_streak,
                "best_streak": best_streak,
                "consistency_percentage": consistency,
            }
        )
        .eq("id", habit_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def check_missed_habits(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    habits = get_habits_by_user(user_id)
    missed = []

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    for habit in habits:
        log_resp = (
            supabase.from_("habit_logs")
            .select("*")
            .eq("habit_id", habit["id"])
            .gte("date", yesterday)
            .execute()
        )
        if not log_resp.data and habit.get("is_active"):
            missed.append(habit)

    return missed


def get_habit_streaks(habit_id: str) -> dict:
    supabase = get_supabase_client()
    logs_resp = (
        supabase.from_("habit_logs")
        .select("date")
        .eq("habit_id", habit_id)
        .order("date", ascending=False)
        .execute()
    )

    if not logs_resp.data:
        return {"current_streak": 0, "best_streak": 0}

    dates = [datetime.fromisoformat(log["date"]).date() for log in logs_resp.data]
    today = datetime.now().date()

    current = 0
    check_date = today
    while check_date in dates or (check_date - timedelta(days=1)) in dates:
        if check_date in dates:
            current += 1
        check_date -= timedelta(days=1)

    return {"current_streak": current, "total_logs": len(dates)}
