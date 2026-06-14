from typing import List
from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client
from ai.client import llm
from ai.prompt_loader import prompts


async def breakdown_task(user_id: str, task_id: str) -> List[dict]:
    supabase = get_supabase_client()
    task_resp = supabase.from_("tasks").select("*").eq("id", task_id).execute()
    if not task_resp.data:
        return []

    task = task_resp.data[0]
    task_prompt = prompts.get_agent("task_agent")
    if task_prompt:
        system_prompt = task_prompt.system_prompt
        user_prompt = (
            f"Break down this task into 3-5 actionable subtasks:\n"
            f"Title: {task.get('title')}\n"
            f"Description: {task.get('description', '')}\n"
            f"Category: {task.get('category', 'personal')}\n"
            f"Return a JSON array of objects with 'title' and 'category' fields."
        )
    else:
        system_prompt = "You are a task breakdown assistant. Return only valid JSON."
        user_prompt = (
            f"Break down this task into 3-5 actionable subtasks:\n"
            f"Title: {task.get('title')}\n"
            f"Description: {task.get('description', '')}\n"
            f"Category: {task.get('category', 'personal')}\n"
            f"Return a JSON array of objects with 'title' and 'category' fields."
        )
    subtasks = await llm.generate_json(user_prompt, system=system_prompt)

    subtask_list = subtasks if isinstance(subtasks, list) else subtasks.get("subtasks", [])
    if not subtask_list:
        subtask_list = [{"title": f"Start: {task.get('title')}", "category": task.get("category", "personal")}]

    created = []
    for st in subtask_list:
        st["user_id"] = user_id
        st["status"] = "pending"
        st["parent_task_id"] = task_id
        st["priority"] = task.get("priority", "medium")
        resp = supabase.from_("tasks").insert(st).execute()
        if resp.data:
            created.append(resp.data[0])
    return created


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
        supabase.from_("tasks").update({"missed_count": new_count}).eq("id", task["id"]).execute()
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
        supabase.from_("sleep_logs")
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
        supabase.from_("tasks").update({"due_date": new_date}).eq("id", task["id"]).execute()
    return len(missed)
