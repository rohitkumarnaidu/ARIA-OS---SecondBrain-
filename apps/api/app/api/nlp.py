import re
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.nlp import NLPParseRequest, NLPParseResponse

router = APIRouter()

DAY_NAMES = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}

ROUTE_ALIASES = {
    "dashboard": "/dashboard",
    "tasks": "/dashboard/tasks",
    "habits": "/dashboard/habits",
    "sleep": "/dashboard/sleep",
    "courses": "/dashboard/courses",
    "goals": "/dashboard/goals",
    "chat": "/dashboard/chat",
    "projects": "/dashboard/projects",
    "ideas": "/dashboard/ideas",
    "time": "/dashboard/time",
    "income": "/dashboard/income",
    "resources": "/dashboard/resources",
    "opportunities": "/dashboard/opportunities",
    "memory": "/dashboard/memory",
    "knowledge": "/dashboard/knowledge",
    "roadmap": "/dashboard/roadmap",
    "settings": "/dashboard/settings",
    "analytics": "/dashboard/analytics",
    "youtube vault": "/dashboard/youtube-vault",
    "focus": "/dashboard/focus",
    "automation": "/dashboard/automation",
    "review": "/dashboard/review",
    "briefing": "/dashboard/briefing",
    "academics": "/dashboard/academics",
}


def extract_date(text: str) -> str | None:
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    lower = text.lower()

    if "today" in lower:
        return today
    if "tomorrow" in lower:
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")

    for name, idx in DAY_NAMES.items():
        if name in lower:
            target = now + timedelta(days=(idx - now.weekday() + 7) % 7)
            return target.strftime("%Y-%m-%d")

    match = re.search(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", text)
    if match:
        m, d, y = match.groups()
        year = y if y else str(now.year)
        if len(year) == 2:
            year = f"20{year}"
        return f"{year}-{m.zfill(2)}-{d.zfill(2)}"

    rel = re.search(r"in\s+(\d+)\s+(day|days|week|weeks)", lower)
    if rel:
        num = int(rel.group(1))
        unit = rel.group(2).lower()
        target = now + timedelta(days=num * 7) if unit.startswith("week") else now + timedelta(days=num)
        return target.strftime("%Y-%m-%d")

    return None


def extract_priority(text: str) -> str | None:
    lower = text.lower()
    if re.search(r"\b(urgent|critical|asap|high priority|important)\b", lower):
        return "high"
    if re.search(r"\b(low priority|whenever|someday|optional)\b", lower):
        return "low"
    return None


def extract_minutes(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(mins|min|minute|minutes|hour|hours|hr|hrs)\b", text.lower())
    if not match:
        return None
    num = int(match.group(1))
    unit = match.group(2).lower()
    return num * 60 if unit.startswith("hour") or unit.startswith("hr") else num


def resolve_route(nav: str) -> str | None:
    key = nav.strip().lower()
    if key in ROUTE_ALIASES:
        return ROUTE_ALIASES[key]
    for alias, route in ROUTE_ALIASES.items():
        if key in alias or alias in key:
            return route
    return None


@router.post("/parse", summary="Parse natural language input", response_model=NLPParseResponse)
async def parse_natural_language(req: NLPParseRequest, current_user=Depends(get_current_user)):
    text = req.text.strip()
    lower = text.lower()

    # Slash command: /new task ...
    if lower.startswith("/new task "):
        title = re.sub(r"^/new task\s+", "", text, flags=re.IGNORECASE).strip()
        if title:
            return NLPParseResponse(
                type="create_task",
                confidence=0.9,
                task={
                    "title": title,
                    "due_date": extract_date(title),
                    "priority": extract_priority(title),
                    "estimated_minutes": extract_minutes(title),
                },
                raw=text,
            )

    if lower.startswith("/go ") or lower.startswith("/navigate "):
        dest = re.sub(r"^/(go|navigate)\s+", "", text, flags=re.IGNORECASE).strip()
        route = resolve_route(dest)
        if route:
            return NLPParseResponse(type="navigate", confidence=0.95, navigation=route, raw=text)

    # Natural language patterns
    patterns = [
        (r"^(create|add|make)\s+(a\s+)?(task|todo)\s+(?:to\s+)?(.+)", "create_task"),
        (r"^remind\s+me\s+(?:to\s+)?(.+)", "create_task"),
        (r"^(i\s+)?need\s+to\s+(.+)", "create_task"),
        (r"^(schedule|plan)\s+(.+)", "create_task"),
    ]

    for pattern, cmd_type in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(match.lastindex).strip()
            if len(title) >= 2:
                return NLPParseResponse(
                    type=cmd_type,
                    confidence=0.85,
                    task={
                        "title": title,
                        "due_date": extract_date(text),
                        "priority": extract_priority(text),
                        "estimated_minutes": extract_minutes(text),
                    },
                    raw=text,
                )

    # Navigation
    nav_match = re.search(r"^(go\s+to|open|show|take\s+me\s+to)\s+(.+)", text, re.IGNORECASE)
    if nav_match:
        dest = nav_match.group(2).strip().lower()
        route = resolve_route(dest)
        if route:
            return NLPParseResponse(type="navigate", confidence=0.8, navigation=route, raw=text)

    return NLPParseResponse(type="unknown", confidence=0.2, raw=text)


@router.post("/execute", summary="Execute NL command", response_model=dict)
async def execute_command(req: dict, current_user=Depends(get_current_user)):
    cmd_type = req.get("type")
    task_data = req.get("task") or {}

    if cmd_type == "create_task":
        supabase = get_supabase_client()
        from uuid import uuid4

        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": str(uuid4()),
            "user_id": current_user.user.id,
            "title": task_data.get("title", "Untitled"),
            "status": "pending",
            "priority": task_data.get("priority", "medium"),
            "due_date": task_data.get("due_date"),
            "estimated_minutes": task_data.get("estimated_minutes"),
            "created_at": now,
        }
        try:
            supabase.table("tasks").insert(record).execute()
            return {"success": True, "message": f'Task "{record["title"]}" created', "data": record}
        except Exception as e:
            logger.error("Failed to create task via NL", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to create task")
    elif cmd_type == "navigate":
        return {"success": True, "redirect_url": req.get("navigation", "/dashboard")}
    elif cmd_type == "schedule":
        supabase = get_supabase_client()
        from uuid import uuid4

        now = datetime.now(timezone.utc).isoformat()
        sched = req.get("schedule") or {}
        record = {
            "id": str(uuid4()),
            "user_id": current_user.user.id,
            "start_time": sched.get("start_time", now),
            "duration_minutes": sched.get("duration_minutes", 30),
            "description": sched.get("description", "Scheduled task"),
            "category": sched.get("category", "focus"),
            "created_at": now,
        }
        try:
            supabase.table("time_entries").insert(record).execute()
            return {
                "success": True,
                "message": f'Scheduled "{record["description"]}" for {record["duration_minutes"]}min',
            }
        except Exception as e:
            logger.error("Failed to create time entry via NL", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to schedule")
    else:
        return {"success": False, "message": "Unknown command type"}
