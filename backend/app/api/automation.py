from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from crons.daily_briefing import run_daily_briefing
from crons.opportunity_radar import run_radar
from crons.weekly_review import run_weekly_review
import asyncio

router = APIRouter()


@router.post("/trigger/briefing")
async def trigger_briefing(current_user=Depends(get_current_user)):
    try:
        result = await generate_daily_briefing(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/radar")
async def trigger_radar(current_user=Depends(get_current_user)):
    try:
        opportunities = await run_opportunity_radar(current_user.user.id)
        return {"status": "success", "count": len(opportunities)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/weekly-review")
async def trigger_weekly_review(current_user=Depends(get_current_user)):
    try:
        review = await generate_weekly_review(current_user.user.id)
        return {"status": "success", "data": review}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def generate_daily_briefing(user_id: str):
    from app.core.supabase import get_supabase_client
    from datetime import datetime, timedelta

    supabase = get_supabase_client()
    today = datetime.now().date().isoformat()

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    goals_resp = (
        supabase.from_("goals")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )
    courses_resp = (
        supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    )

    tasks = tasks_resp.data or []
    goals = goals_resp.data or []
    courses = courses_resp.data or []

    pending = [t for t in tasks if t.get("status") == "pending"]
    pending.sort(
        key=lambda t: {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(
            t.get("priority", "medium"), 2
        )
    )
    top_3 = pending[:3]

    completed = len([t for t in tasks if t.get("status") == "completed"])
    score = int((completed / len(tasks) * 100)) if tasks else 50

    return {
        "date": today,
        "top_3_tasks": [
            {"title": t.get("title"), "priority": t.get("priority")} for t in top_3
        ],
        "productivity_score": score,
        "active_goals": len(goals),
        "active_courses": len([c for c in courses if c.get("status") == "in_progress"]),
    }


async def generate_weekly_review(user_id: str):
    from app.core.supabase import get_supabase_client
    from datetime import datetime, timedelta

    supabase = get_supabase_client()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()

    tasks_resp = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .gte("created_at", week_ago)
        .execute()
    )
    completed_resp = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "completed")
        .gte("completed_at", week_ago)
        .execute()
    )
    goals_resp = (
        supabase.from_("goals")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )

    tasks = tasks_resp.data or []
    completed = completed_resp.data or []
    goals = goals_resp.data or []

    return {
        "tasks_created": len(tasks),
        "tasks_completed": len(completed),
        "completion_rate": round((len(completed) / len(tasks) * 100), 1)
        if tasks
        else 0,
        "active_goals": len(goals),
        "avg_progress": sum(g.get("progress", 0) for g in goals) / len(goals)
        if goals
        else 0,
    }
