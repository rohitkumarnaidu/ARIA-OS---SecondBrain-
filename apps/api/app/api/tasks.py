from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter()


@router.get("/", summary="List all tasks", response_model=TaskListResponse)
async def get_tasks(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    count_response = (
        supabase.from_("tasks")
        .select("*", count="exact")
        .eq("user_id", current_user.user.id)
        .execute()
    )
    total = count_response.count if hasattr(count_response, "count") and count_response.count is not None else len(count_response.data)
    data_response = (
        supabase.from_("tasks")
        .select(
            "id, user_id, title, status, priority, due_date, created_at, updated_at, completed_at, estimated_minutes, category, description, project_id, goal_id, is_recurring, recurring_frequency, dependency_id, missed_count"
        )
        .eq("user_id", current_user.user.id)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return TaskListResponse(data=data_response.data, total=total, limit=limit, offset=offset)


@router.post("/", summary="Create a new task", status_code=201, response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = task.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "pending"
    response = supabase.from_("tasks").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/{task_id}", summary="Get a task by ID", response_model=TaskResponse)
async def get_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select(
            "id, user_id, title, status, priority, due_date, created_at, updated_at, completed_at, estimated_minutes, category, description, project_id, goal_id, is_recurring, recurring_frequency, dependency_id, missed_count"
        )
        .eq("id", task_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data[0]


@router.put("/{task_id}", summary="Update a task", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("tasks").update(update_data).eq("id", task_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data[0]


@router.delete("/{task_id}", summary="Delete a task", status_code=204)
async def delete_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("tasks").delete().eq("id", task_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.post("/{task_id}/complete", summary="Mark a task as complete", status_code=201, response_model=TaskResponse)
async def complete_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .update({"status": "completed", "completed_at": datetime.now().isoformat()})
        .eq("id", task_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data[0]
