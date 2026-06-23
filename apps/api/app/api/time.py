from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.time_entry import TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse

router = APIRouter()


@router.get("/", summary="List time entries", response_model=List[TimeEntryResponse])
async def get_time_entries(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("time_entries")
        .select("id, user_id, start_time, end_time, duration_minutes, category, is_deep_work, description, created_at")
        .eq("user_id", current_user.user.id)
        .order("start_time", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{entry_id}", summary="Get a time entry by ID", response_model=TimeEntryResponse)
async def get_time_entry(entry_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("time_entries")
        .select("id, user_id, start_time, end_time, duration_minutes, category, is_deep_work, description, created_at")
        .eq("id", entry_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return response.data[0]


@router.post("/", summary="Create a time entry", status_code=201, response_model=TimeEntryResponse)
async def create_time_entry(entry: TimeEntryCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = entry.model_dump()
    data["user_id"] = current_user.user.id
    if data.get("start_time"):
        data["start_time"] = data["start_time"].isoformat()
    if data.get("end_time"):
        data["end_time"] = data["end_time"].isoformat()
    if data.get("start_time") and data.get("end_time"):
        start = datetime.fromisoformat(data["start_time"])
        end = datetime.fromisoformat(data["end_time"])
        data["duration_minutes"] = int((end - start).total_seconds() / 60)
    response = supabase.from_("time_entries").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{entry_id}", summary="Update a time entry", response_model=TimeEntryResponse)
async def update_time_entry(entry_id: str, entry_update: TimeEntryUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in entry_update.model_dump().items() if v is not None}
    if update_data.get("start_time"):
        update_data["start_time"] = update_data["start_time"].isoformat()
    if update_data.get("end_time"):
        update_data["end_time"] = update_data["end_time"].isoformat()
    response = (
        supabase.from_("time_entries")
        .update(update_data)
        .eq("id", entry_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return response.data[0]


@router.delete("/{entry_id}", summary="Delete a time entry", status_code=204)
async def delete_time_entry(entry_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("time_entries").delete().eq("id", entry_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.get("/stats/daily", summary="Get daily time stats")
async def get_daily_time_stats(date: Optional[str] = None, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    response = (
        supabase.from_("time_entries")
        .select("category, duration_minutes")
        .eq("user_id", current_user.user.id)
        .gte("start_time", f"{target_date}T00:00:00")
        .lte("start_time", f"{target_date}T23:59:59")
        .execute()
    )
    stats = {}
    for entry in response.data or []:
        cat = entry.get("category", "work")
        stats[cat] = stats.get(cat, 0) + (entry.get("duration_minutes") or 0)
    return {
        "date": target_date,
        "categories": stats,
        "total_minutes": sum(stats.values()),
    }


@router.post("/stop", summary="Stop an active timer", status_code=201)
async def stop_timer(entry_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    end_time = datetime.now().isoformat()
    response = (
        supabase.from_("time_entries")
        .update({"end_time": end_time})
        .eq("id", entry_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Time entry not found")
    entry = response.data[0]
    if entry.get("start_time") and entry.get("end_time"):
        start = datetime.fromisoformat(entry["start_time"])
        end = datetime.fromisoformat(entry["end_time"])
        duration = int((end - start).total_seconds() / 60)
        supabase.from_("time_entries").update({"duration_minutes": duration}).eq("id", entry_id).execute()
    return response.data[0]
