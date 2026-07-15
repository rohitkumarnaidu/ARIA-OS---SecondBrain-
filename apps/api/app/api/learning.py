from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from typing import Dict
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from ai.agents.learning_agent import detect_learning_patterns, track_user_progress

router = APIRouter()


@router.get("/insights", summary="Get learning insights and patterns")
async def get_learning_insights(
    refresh: bool = Query(False, description="Force re-analysis of learning patterns"),
    current_user=Depends(get_current_user),
):
    user_id = current_user.user.id
    supabase = get_supabase_client()

    if refresh:
        try:
            progress = await track_user_progress(user_id)
            patterns = await detect_learning_patterns(user_id)
        except Exception as e:
            logger.error("Learning re-analysis failed", error=str(e))
            progress = {}
            patterns = []
    else:
        try:
            result = (
                supabase.from_("learning_progress")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                progress = result.data[0].get("data", {})
            else:
                progress = {}
        except Exception as e:
            logger.error("Failed to fetch learning progress", error=str(e))
            progress = {}

    now = datetime.now()
    week_ago = (now - timedelta(days=7)).isoformat()

    try:
        tasks_resp = (
            supabase.from_("tasks")
            .select("status, priority, due_date, created_at, completed_at")
            .eq("user_id", user_id)
            .execute()
        )
        courses_resp = (
            supabase.from_("courses")
            .select("title, status, progress_pct")
            .eq("user_id", user_id)
            .execute()
        )
        habits_resp = (
            supabase.from_("habits")
            .select("title, is_active, current_streak, consistency_percentage")
            .eq("user_id", user_id)
            .execute()
        )
        time_resp = (
            supabase.from_("time_entries")
            .select("duration_minutes, is_deep_work, start_time")
            .eq("user_id", user_id)
            .gte("start_time", week_ago)
            .execute()
        )
    except Exception as e:
        logger.error("Failed to fetch learning source data", error=str(e))
        tasks_resp = type("obj", (), {"data": []})()
        courses_resp = type("obj", (), {"data": []})()
        habits_resp = type("obj", (), {"data": []})()
        time_resp = type("obj", (), {"data": []})()

    tasks = tasks_resp.data or []
    courses = courses_resp.data or []
    habits = habits_resp.data or []
    time_entries = time_resp.data or []

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
    recent_completed = len([t for t in tasks if t.get("status") == "completed" and t.get("completed_at", "") >= week_ago])
    pending_tasks = len([t for t in tasks if t.get("status") in ("pending", "in_progress")])

    by_hour: Dict[int, int] = {}
    for t in time_entries:
        start = t.get("start_time", "")
        if start:
            try:
                hour = datetime.fromisoformat(start).hour
                mins = t.get("duration_minutes", 0)
                by_hour[hour] = by_hour.get(hour, 0) + mins
            except (ValueError, TypeError) as e:
                logger.warn("Failed to parse time entry start_time", error=str(e))
    peak_hours = sorted(by_hour, key=by_hour.get, reverse=True)[:3] if by_hour else []
    deep_work_minutes = sum(t.get("duration_minutes", 0) for t in time_entries if t.get("is_deep_work"))
    total_minutes_tracked = sum(t.get("duration_minutes", 0) for t in time_entries)

    active_habits = [h for h in habits if h.get("is_active")]
    course_statuses: Dict[str, int] = {}
    for c in courses:
        s = c.get("status", "unknown")
        course_statuses[s] = course_statuses.get(s, 0) + 1

    productivity_patterns = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "recent_completion_rate": round(recent_completed / max(len([t for t in tasks if t.get("created_at", "") >= week_ago]), 1) * 100, 1),
        "overall_completion_rate": round(completed_tasks / max(total_tasks, 1) * 100, 1),
        "tasks_by_priority": {
            p: len([t for t in tasks if t.get("priority") == p])
            for p in set(t.get("priority", "medium") for t in tasks)
        },
    }

    study_habits = {
        "total_courses": len(courses),
        "courses_by_status": course_statuses,
        "active_habits": len(active_habits),
        "habit_consistency": round(
            sum(h.get("consistency_percentage", 0) for h in active_habits) / max(len(active_habits), 1), 1
        ),
        "best_streak": max((h.get("current_streak", 0) for h in active_habits), default=0),
    }

    peak_times = {
        "peak_hours": [f"{h}:00" for h in peak_hours],
        "deep_work_minutes_7d": deep_work_minutes,
        "total_focus_minutes_7d": total_minutes_tracked,
        "deep_work_ratio": round(deep_work_minutes / max(total_minutes_tracked, 1) * 100, 1),
    }

    progress_data = progress or {}
    if not progress_data and tasks:
        progress_data = {
            "tasks_created": len([t for t in tasks if t.get("created_at", "") >= week_ago]),
            "tasks_completed": recent_completed,
            "completion_rate": productivity_patterns["recent_completion_rate"],
            "courses_enrolled": len([c for c in courses if c.get("status") in ("not_started", "in_progress")]),
            "courses_completed": len([c for c in courses if c.get("status") == "completed"]),
            "active_habits": len(active_habits),
        }

    try:
        if not refresh:
            patterns = await detect_learning_patterns(user_id)
    except Exception as e:
        logger.error("Learning pattern detection failed", error=str(e))
        patterns = []

    return {
        "progress": progress_data,
        "productivity_patterns": productivity_patterns,
        "study_habits": study_habits,
        "peak_times": peak_times,
        "insights": patterns if patterns else [],
        "generated_at": datetime.now().isoformat(),
    }
