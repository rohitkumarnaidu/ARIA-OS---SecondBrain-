from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.sleep import SleepCreate, SleepUpdate, SleepResponse

router = APIRouter()


@router.get("/", summary="List sleep logs", response_model=List[SleepResponse])
async def get_sleep(
    current_user=Depends(get_current_user),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("sleep_logs")
        .select(
            "id, user_id, date, bedtime, wake_time, duration_hours, sleep_score, sleep_debt, quality_rating, created_at"
        )
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{sleep_id}", summary="Get a sleep log by ID", response_model=SleepResponse)
async def get_sleep_entry(sleep_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("sleep_logs")
        .select(
            "id, user_id, date, bedtime, wake_time, duration_hours, sleep_score, sleep_debt, quality_rating, created_at"
        )
        .eq("id", sleep_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return response.data[0]


@router.put("/{sleep_id}", summary="Update a sleep log", response_model=SleepResponse)
async def update_sleep(sleep_id: str, sleep_update: SleepUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in sleep_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("sleep_logs")
        .update(update_data)
        .eq("id", sleep_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return response.data[0]


@router.post("/", summary="Create a sleep log", status_code=201, response_model=SleepResponse)
async def create_sleep(sleep: SleepCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()

    b_h, b_m = map(int, sleep.bedtime.split(":"))
    w_h, w_m = map(int, sleep.wake_time.split(":"))
    duration = w_h - b_h + (w_m - b_m) / 60
    if duration < 0:
        duration += 24

    duration = round(duration, 1)
    score = min(100, int(duration * 12.5 + sleep.quality_rating * 20))
    debt = max(0, 8 - duration)

    from datetime import datetime, timedelta

    now = datetime.now()
    bt = datetime(now.year, now.month, now.day, b_h, b_m)
    if sleep.bedtime > sleep.wake_time:
        bt -= timedelta(days=1)
    wt = datetime(now.year, now.month, now.day, w_h, w_m)

    data = sleep.model_dump()
    data["user_id"] = current_user.user.id
    data["bedtime"] = bt.isoformat()
    data["wake_time"] = wt.isoformat()
    data["duration_hours"] = duration
    data["sleep_score"] = score
    data["sleep_debt"] = round(debt, 1)

    response = supabase.from_("sleep_logs").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/{sleep_id}", summary="Delete a sleep log", status_code=204)
async def delete_sleep(sleep_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("sleep_logs").delete().eq("id", sleep_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
