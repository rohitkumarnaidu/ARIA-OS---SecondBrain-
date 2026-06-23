from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.habit import HabitCreate, HabitUpdate, HabitResponse

router = APIRouter()


@router.get("/", summary="List all habits", response_model=List[HabitResponse])
async def get_habits(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("habits")
        .select("id, user_id, name, frequency, is_active, current_streak, best_streak, consistency_percentage, created_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{habit_id}", summary="Get a habit by ID", response_model=HabitResponse)
async def get_habit(habit_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("habits").select("id, user_id, name, frequency, is_active, current_streak, best_streak, consistency_percentage, created_at").eq("id", habit_id).eq("user_id", current_user.user.id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Habit not found")
    return response.data[0]


@router.post("/", summary="Create a new habit", status_code=201, response_model=HabitResponse)
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


@router.put("/{habit_id}", summary="Update a habit", response_model=HabitResponse)
async def update_habit(habit_id: str, habit_update: HabitUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in habit_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("habits").update(update_data).eq("id", habit_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Habit not found")
    return response.data[0]


@router.delete("/{habit_id}", summary="Delete a habit", status_code=204)
async def delete_habit(habit_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("habits").delete().eq("id", habit_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
