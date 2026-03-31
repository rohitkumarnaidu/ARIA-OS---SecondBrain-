from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", current_user.user.id)
        .execute()
    )
    return response.data


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = task.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "pending"
    response = supabase.from_("tasks").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("id", task_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data[0]


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str, task_update: TaskUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("tasks")
        .update(update_data)
        .eq("id", task_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data[0]


@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .delete()
        .eq("id", task_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Task deleted"}


@router.post("/{task_id}/complete", response_model=TaskResponse)
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


from datetime import datetime
