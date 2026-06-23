from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.briefing import BriefingRead

router = APIRouter()


@router.get("/", summary="List daily briefings", response_model=List[BriefingRead])
async def list_briefings(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("daily_briefings")
        .select("id, user_id, date, title, summary, priorities, read, created_at")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/today", summary="Get today's briefing", response_model=Optional[BriefingRead])
async def get_today_briefing(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    today = datetime.now().strftime("%Y-%m-%d")
    response = (
        supabase.from_("daily_briefings")
        .select("id, user_id, date, title, summary, priorities, read, created_at")
        .eq("user_id", current_user.user.id)
        .eq("date", today)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]
    response = (
        supabase.from_("daily_briefings")
        .select("id, user_id, date, title, summary, priorities, read, created_at")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


@router.get("/{briefing_id}", summary="Get a briefing by ID", response_model=BriefingRead)
async def get_briefing(briefing_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("daily_briefings")
        .select("id, user_id, date, title, summary, priorities, read, created_at")
        .eq("id", briefing_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return response.data[0]


@router.put("/{briefing_id}/read", summary="Mark a briefing as read", response_model=BriefingRead)
async def mark_briefing_read(briefing_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("daily_briefings")
        .update({"read": True})
        .eq("id", briefing_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return response.data[0]
