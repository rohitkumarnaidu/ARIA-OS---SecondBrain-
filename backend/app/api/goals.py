from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    roadmap_type: str = "career_skills"
    target_date: Optional[str] = None
    hours_per_day: float = 2.0
    days_per_week: float = 5.0
    intensity: str = "medium"


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    roadmap_type: Optional[str] = None
    target_date: Optional[str] = None
    hours_per_day: Optional[float] = None
    days_per_week: Optional[float] = None
    intensity: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None


class GoalResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    roadmap_type: str
    target_date: Optional[str]
    hours_per_day: float
    days_per_week: float
    intensity: str
    status: str
    progress: int
    created_at: str


@router.get("/", response_model=List[GoalResponse])
async def get_goals(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("goals")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=GoalResponse)
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
            data["target_date"] = datetime.fromisoformat(
                data["target_date"].replace("Z", "+00:00")
            ).isoformat()
        except:
            pass
    response = supabase.from_("goals").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str, goal_update: GoalUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in goal_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("goals")
        .update(update_data)
        .eq("id", goal_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return response.data[0]


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("goals")
        .delete()
        .eq("id", goal_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Goal deleted"}
