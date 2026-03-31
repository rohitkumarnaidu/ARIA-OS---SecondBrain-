from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class HabitCreate(BaseModel):
    name: str
    frequency: str = "daily"
    custom_days: Optional[List[int]] = None
    time_target_minutes: Optional[int] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    frequency: Optional[str] = None
    time_target_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class HabitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    frequency: str
    time_target_minutes: Optional[int]
    is_active: bool
    current_streak: int
    best_streak: int
    consistency_percentage: float


@router.get("/", response_model=List[HabitResponse])
async def get_habits(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("habits")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=HabitResponse)
async def create_habit(habit: HabitCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = habit.model_dump()
    data["user_id"] = current_user.user.id
    data["is_active"] = True
    data["current_streak"] = 0
    data["best_streak"] = 0
    data["consistency_percentage"] = 0
    response = supabase.from_("habits").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str, habit_update: HabitUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in habit_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("habits")
        .update(update_data)
        .eq("id", habit_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Habit not found")
    return response.data[0]


@router.delete("/{habit_id}")
async def delete_habit(habit_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("habits")
        .delete()
        .eq("id", habit_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Habit deleted"}
