from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user

router = APIRouter()


@router.get("/daily")
async def get_daily_summary(date: str = Query(...), current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    tasks = supabase.from_("tasks").select("count").eq("user_id", current_user.user.id).gte("created_at", date + "T00:00:00").lte("created_at", date + "T23:59:59").execute()
    habits = supabase.from_("habit_logs").select("count").eq("user_id", current_user.user.id).eq("date", date).eq("completed", True).execute()
    sleep = supabase.from_("sleep_logs").select("sleep_score, duration_hours").eq("user_id", current_user.user.id).eq("date", date).limit(1).execute()
    time = supabase.from_("time_entries").select("duration_minutes, is_deep_work").eq("user_id", current_user.user.id).gte("start_time", date + "T00:00:00").lte("start_time", date + "T23:59:59").execute()
    return {
        "date": date,
        "tasks_completed": len(tasks.data or []),
        "habits_completed": len(habits.data or []),
        "sleep_score": sleep.data[0]["sleep_score"] if sleep.data else None,
        "focus_minutes": sum(t.get("duration_minutes", 0) for t in (time.data or []) if t.get("is_deep_work")),
    }


@router.get("/weekly")
async def get_weekly_trends(week_start: str = Query(...), current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    week_end = (datetime.fromisoformat(week_start) + timedelta(days=7)).strftime("%Y-%m-%d")
    tasks = supabase.from_("tasks").select("status").eq("user_id", current_user.user.id).gte("created_at", week_start).lte("created_at", week_end).execute()
    habits = supabase.from_("habit_logs").select("completed").eq("user_id", current_user.user.id).gte("date", week_start).lte("date", week_end).execute()
    sleep = supabase.from_("sleep_logs").select("sleep_score").eq("user_id", current_user.user.id).gte("date", week_start).lte("date", week_end).execute()
    time = supabase.from_("time_entries").select("duration_minutes, is_deep_work").eq("user_id", current_user.user.id).gte("start_time", week_start).lte("start_time", week_end).execute()
    task_data = tasks.data or []
    total_tasks = len(task_data)
    completed_tasks = len([t for t in task_data if t.get("status") == "completed"])
    habit_data = habits.data or []
    total_habits = len(habit_data)
    completed_habits = len([h for h in habit_data if h.get("completed")])
    sleep_scores = [s.get("sleep_score", 0) for s in (sleep.data or []) if s.get("sleep_score")]
    total_minutes = sum(t.get("duration_minutes", 0) for t in (time.data or []))
    return {
        "week_start": week_start,
        "task_completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0,
        "habit_consistency": round(completed_habits / total_habits * 100, 1) if total_habits else 0,
        "avg_sleep_score": round(sum(sleep_scores) / len(sleep_scores), 1) if sleep_scores else 0,
        "total_focus_hours": round(total_minutes / 60, 1),
    }


@router.get("/stats")
async def get_aggregated_stats(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    tasks = supabase.from_("tasks").select("status, priority").eq("user_id", current_user.user.id).execute()
    habits = supabase.from_("habits").select("is_active, current_streak, best_streak, consistency_percentage").eq("user_id", current_user.user.id).execute()
    sleep = supabase.from_("sleep_logs").select("duration_hours, sleep_score, sleep_debt").eq("user_id", current_user.user.id).execute()
    time = supabase.from_("time_entries").select("duration_minutes, is_deep_work").eq("user_id", current_user.user.id).execute()
    projects = supabase.from_("projects").select("status").eq("user_id", current_user.user.id).execute()
    ideas = supabase.from_("ideas").select("status").eq("user_id", current_user.user.id).execute()
    income = supabase.from_("income_entries").select("amount, effective_hourly_rate").eq("user_id", current_user.user.id).execute()

    task_data = tasks.data or []
    task_total = len(task_data)
    task_completed = len([t for t in task_data if t.get("status") == "completed"])
    by_priority = {}
    for t in task_data:
        p = t.get("priority", "medium")
        by_priority[p] = by_priority.get(p, 0) + 1
    habit_data = habits.data or []
    active_habits = [h for h in habit_data if h.get("is_active")]
    best_streak = max([h.get("best_streak", 0) for h in habit_data]) if habit_data else 0
    sleep_data = sleep.data or []
    sleep_scores = [s.get("sleep_score", 0) for s in sleep_data if s.get("sleep_score")]
    time_data = time.data or []
    deep_work = sum(t.get("duration_minutes", 0) for t in time_data if t.get("is_deep_work"))
    income_data = income.data or []
    rates = [i.get("effective_hourly_rate") for i in income_data if i.get("effective_hourly_rate")]
    by_stage = {}
    for i in (ideas.data or []):
        s = i.get("status", "raw")
        by_stage[s] = by_stage.get(s, 0) + 1
    return {
        "start_date": start_date,
        "end_date": end_date,
        "tasks": {
            "total": task_total,
            "completed": task_completed,
            "by_priority": by_priority,
        },
        "habits": {
            "total": len(active_habits),
            "consistency": round(sum(h.get("consistency_percentage", 0) for h in active_habits) / len(active_habits), 1) if active_habits else 0,
            "best_streak": best_streak,
        },
        "sleep": {
            "avg_duration": round(sum(s.get("duration_hours", 0) for s in sleep_data) / len(sleep_data), 1) if sleep_data else 0,
            "avg_score": round(sum(sleep_scores) / len(sleep_scores), 1) if sleep_scores else 0,
            "total_debt": round(sum(s.get("sleep_debt", 0) for s in sleep_data), 1),
        },
        "time": {
            "total_minutes": sum(t.get("duration_minutes", 0) for t in time_data),
            "deep_work_minutes": deep_work,
        },
        "projects": {
            "total": len(projects.data or []),
            "completed": len([p for p in (projects.data or []) if p.get("status") == "completed"]),
        },
        "ideas": {
            "total": len(ideas.data or []),
            "by_stage": by_stage,
        },
        "income": {
            "total": sum(i.get("amount", 0) for i in income_data),
            "hourly_rate_avg": round(sum(rates) / len(rates), 2) if rates else 0,
        },
    }
