from fastapi import APIRouter, Depends, HTTPException
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.notification import NotificationResponse
from datetime import datetime

router = APIRouter()


@router.get("/", summary="List notifications", response_model=list[NotificationResponse])
async def list_notifications(limit: int = 50, offset: int = 0, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = supabase.from_("notifications")\
            .select("id, user_id, title, message, category, priority, read, action_url, icon, created_at")\
            .eq("user_id", current_user.user.id)\
            .order("created_at", ascending=False)\
            .range(offset, offset + limit - 1)\
            .execute()
        return resp.data or []
    except Exception as e:
        logger.error("Failed to fetch notifications", error=str(e))
        return []


@router.patch("/{notification_id}/read", summary="Mark notification as read", response_model=dict)
async def mark_read(notification_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = supabase.from_("notifications")\
            .update({"read": True})\
            .eq("id", notification_id)\
            .eq("user_id", current_user.user.id)\
            .execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to mark notification read", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mark as read")


@router.post("/read-all", summary="Mark all notifications as read", response_model=dict)
async def mark_all_read(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        supabase.from_("notifications")\
            .update({"read": True})\
            .eq("user_id", current_user.user.id)\
            .eq("read", False)\
            .execute()
        return {"status": "ok", "message": "All notifications marked as read"}
    except Exception as e:
        logger.error("Failed to mark all notifications read", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mark all as read")


@router.post("/generate", summary="Generate proactive nudges", response_model=list[NotificationResponse])
async def generate_proactive_nudges(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    created = []

    try:
        tasks_resp = supabase.from_("tasks").select("id, title, status, priority, due_date")\
            .eq("user_id", current_user.user.id)\
            .eq("status", "pending")\
            .execute()
        tasks = tasks_resp.data or []
    except Exception as e:
        logger.error("Failed to fetch tasks for nudges", error=str(e))
        tasks = []

    try:
        habits_resp = supabase.from_("habits").select("id, name, current_streak, consistency_percent, is_active")\
            .eq("user_id", current_user.user.id)\
            .eq("is_active", True)\
            .execute()
        habits = habits_resp.data or []
    except Exception as e:
        logger.error("Failed to fetch habits for nudges", error=str(e))
        habits = []

    try:
        sleep_resp = supabase.from_("sleep_logs").select("sleep_score, date")\
            .eq("user_id", current_user.user.id)\
            .order("date", ascending=False)\
            .limit(14)\
            .execute()
        sleep_logs = sleep_resp.data or []
    except Exception as e:
        logger.error("Failed to fetch sleep for nudges", error=str(e))
        sleep_logs = []

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    # Overdue tasks
    overdue = [t for t in tasks if t.get("due_date") and t["due_date"] < now.isoformat()]
    if overdue:
        from uuid import uuid4
        nid = str(uuid4())
        nudge = {
            "id": nid,
            "user_id": current_user.user.id,
            "title": f"{len(overdue)} overdue task{'s' if len(overdue) > 1 else ''}",
            "message": f"Task{'s' if len(overdue) > 1 else ''} past deadline: {', '.join(t['title'][:30] for t in overdue[:3])}",
            "category": "task",
            "priority": "high",
            "read": False,
            "action_url": "/dashboard/tasks",
            "icon": "alert-circle",
            "created_at": now.isoformat(),
        }
        try:
            supabase.from_("notifications").insert(nudge).execute()
            created.append(nudge)
        except Exception as e:
            logger.error("Failed to insert overdue nudge", error=str(e))

    # At-risk habits
    at_risk_habits = [h for h in habits if (h.get("current_streak", 0) or 0) < 3 and (h.get("consistency_percent", 50) or 50) < 40]
    if at_risk_habits:
        from uuid import uuid4
        nid = str(uuid4())
        nudge = {
            "id": nid,
            "user_id": current_user.user.id,
            "title": f"{len(at_risk_habits)} habit{'s' if len(at_risk_habits) > 1 else ''} at risk",
            "message": f"Streak{'s' if len(at_risk_habits) > 1 else ''} slipping: {', '.join(h['name'][:25] for h in at_risk_habits[:3])}",
            "category": "habit",
            "priority": "medium",
            "read": False,
            "action_url": "/dashboard/habits",
            "icon": "flame",
            "created_at": now.isoformat(),
        }
        try:
            supabase.from_("notifications").insert(nudge).execute()
            created.append(nudge)
        except Exception as e:
            logger.error("Failed to insert habit nudge", error=str(e))

    # Sleep trend
    scores = [sl.get("sleep_score", 0) or 0 for sl in sleep_logs]
    if len(scores) >= 7:
        recent = sum(scores[:7]) / 7
        if len(scores) >= 14:
            older = sum(scores[7:14]) / 7
            if recent < older - 5:
                from uuid import uuid4
                nid = str(uuid4())
                nudge = {
                    "id": nid,
                    "user_id": current_user.user.id,
                    "title": "Sleep quality declining",
                    "message": f"Your sleep score dropped from {older:.0f} to {recent:.0f} over the past week.",
                    "category": "system",
                    "priority": "medium",
                    "read": False,
                    "action_url": "/dashboard/sleep",
                    "icon": "moon",
                    "created_at": now.isoformat(),
                }
                try:
                    supabase.from_("notifications").insert(nudge).execute()
                    created.append(nudge)
                except Exception as e:
                    logger.error("Failed to insert sleep nudge", error=str(e))

    return [NotificationResponse(**n) for n in created]


@router.get("/deadline-alerts", summary="Get deadline alerts", response_model=list)
async def deadline_alerts(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    from datetime import timezone
    now = datetime.now(timezone.utc)

    try:
        tasks_resp = supabase.from_("tasks").select("id, title, due_date, priority, status").eq("user_id", current_user.user.id).eq("status", "pending").neq("due_date", None).execute()
        tasks = tasks_resp.data or []
    except Exception as e:
        logger.error("Failed to check deadline alerts", error=str(e))
        tasks = []

    alerts = []
    for t in tasks:
        due = t.get("due_date")
        if not due:
            continue
        try:
            due_dt = datetime.fromisoformat(due)
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        remaining = (due_dt - now).total_seconds() / 3600
        if 0 < remaining <= 48:
            alerts.append({
                "id": t["id"],
                "title": t["title"],
                "due_date": due,
                "hours_remaining": round(remaining, 1),
                "priority": t.get("priority", "medium"),
                "urgent": remaining <= 24,
            })

    alerts.sort(key=lambda a: a["hours_remaining"])
    return alerts[:20]
