from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class SleepCreate(BaseModel):
    bedtime: str
    wake_time: str
    quality_rating: int


class SleepUpdate(BaseModel):
    bedtime: Optional[str] = None
    wake_time: Optional[str] = None
    quality_rating: Optional[int] = None


class SleepResponse(BaseModel):
    id: str
    user_id: str
    bedtime: str
    wake_time: str
    quality_rating: int
    duration_hours: float
    sleep_score: int
    sleep_debt: float
    created_at: str


@router.get("/", response_model=List[SleepResponse])
async def get_sleep(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("sleep_logs")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .limit(30)
        .execute()
    )
    return response.data


@router.post("/", response_model=SleepResponse)
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

    data = {
        "user_id": current_user.user.id,
        "bedtime": bt.isoformat(),
        "wake_time": wt.isoformat(),
        "quality_rating": sleep.quality_rating,
        "duration_hours": duration,
        "sleep_score": score,
        "sleep_debt": round(debt, 1),
    }

    response = supabase.from_("sleep_logs").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/{sleep_id}")
async def delete_sleep(sleep_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("sleep_logs")
        .delete()
        .eq("id", sleep_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Sleep log deleted"}
