from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.supabase import get_supabase_client


async def breakdown_task(user_id: str, task_id: str) -> List[dict]:
    supabase = get_supabase_client()

    task_resp = supabase.from_("tasks").select("*").eq("id", task_id).execute()
    if not task_resp.data:
        return []

    task = task_resp.data[0]
    description = task.get("description", "")

    subtasks = []
    keywords = description.lower().split()

    if "research" in keywords:
        subtasks.append(
            {
                "title": f"Research for: {task.get('title')}",
                "category": "study",
                "priority": "medium",
            }
        )

    if "write" in keywords or "create" in keywords:
        subtasks.append(
            {
                "title": f"Create first draft for: {task.get('title')}",
                "category": "project",
                "priority": "high",
            }
        )
        subtasks.append(
            {
                "title": f"Review and finalize: {task.get('title')}",
                "category": "project",
                "priority": "medium",
            }
        )

    if "build" in keywords or "code" in keywords:
        subtasks.append(
            {
                "title": f"Set up environment for: {task.get('title')}",
                "category": "project",
                "priority": "high",
            }
        )
        subtasks.append(
            {
                "title": f"Implement core functionality: {task.get('title')}",
                "category": "project",
                "priority": "high",
            }
        )
        subtasks.append(
            {
                "title": f"Test: {task.get('title')}",
                "category": "project",
                "priority": "medium",
            }
        )

    if not subtasks:
        subtasks.append(
            {
                "title": f"Start: {task.get('title')}",
                "category": task.get("category", "personal"),
                "priority": task.get("priority"),
            }
        )
        subtasks.append(
            {
                "title": f"Complete: {task.get('title')}",
                "category": task.get("category", "personal"),
                "priority": task.get("priority"),
            }
        )

    created_subtasks = []
    for st in subtasks:
        st["user_id"] = user_id
        st["status"] = "pending"
        st["parent_task_id"] = task_id
        resp = supabase.from_("tasks").insert(st).execute()
        if resp.data:
            created_subtasks.append(resp.data[0])

    return created_subtasks


async def check_missed_tasks(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    now = datetime.now().isoformat()

    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .lt("due_date", now)
        .execute()
    )

    missed_tasks = response.data or []

    for task in missed_tasks:
        new_count = task.get("missed_count", 0) + 1
        supabase.from_("tasks").update({"missed_count": new_count}).eq(
            "id", task["id"]
        ).execute()

    return missed_tasks


async def suggest_task_prioritization(user_id: str) -> List[dict]:
    supabase = get_supabase_client()
    tasks_resp = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .execute()
    )

    tasks = tasks_resp.data or []
    sleep_resp = (
        supabase.from_("sleep_entries")
        .select("quality")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(1)
        .execute()
    )

    sleep_quality = sleep_resp.data[0].get("quality", 70) if sleep_resp.data else 70

    priority_map = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(
        key=lambda t: (
            priority_map.get(t.get("priority", "medium"), 2),
            t.get("due_date", ""),
        )
    )

    if sleep_quality < 60:
        tasks = [t for t in tasks if t.get("priority") != "urgent"]

    return tasks[:10]


async def auto_reschedule_overdue(user_id: str) -> int:
    missed = await check_missed_tasks(user_id)

    supabase = get_supabase_client()
    for task in missed:
        new_date = (datetime.now() + timedelta(days=1)).date().isoformat()
        supabase.from_("tasks").update({"due_date": new_date}).eq(
            "id", task["id"]
        ).execute()

    return len(missed)


from datetime import timedelta
