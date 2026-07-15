from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from shared.utils.logger import logger

router = APIRouter()


@router.get("/", summary="List all goals", response_model=List[GoalResponse])
async def get_goals(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("goals")
        .select("id, user_id, title, description, status, progress, target_date, category, created_at, updated_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{goal_id}", summary="Get a goal by ID", response_model=GoalResponse)
async def get_goal(goal_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("goals")
        .select("id, user_id, title, description, status, progress, target_date, category, created_at, updated_at")
        .eq("id", goal_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return response.data[0]


@router.post("/", summary="Create a new goal", status_code=201, response_model=GoalResponse)
async def create_goal(goal: GoalCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = goal.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "active"
    data["progress"] = 0
    data["nodes"] = []
    if data.get("target_date") and data["target_date"]:
        from datetime import datetime

        try:
            data["target_date"] = datetime.fromisoformat(data["target_date"].replace("Z", "+00:00")).isoformat()
        except Exception as e:
            logger.warn("Failed to parse goal target_date", error=str(e))
    response = supabase.from_("goals").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{goal_id}", summary="Update a goal", response_model=GoalResponse)
async def update_goal(goal_id: str, goal_update: GoalUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in goal_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("goals").update(update_data).eq("id", goal_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return response.data[0]


@router.delete("/{goal_id}", summary="Delete a goal", status_code=204)
async def delete_goal(goal_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("goals").delete().eq("id", goal_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
