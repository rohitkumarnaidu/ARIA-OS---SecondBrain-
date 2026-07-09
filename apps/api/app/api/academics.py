from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.academic import SubjectCreate, SubjectResponse, MarkCreate, MarkResponse
from shared.utils.logger import logger
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/subjects", summary="List all subjects", response_model=List[SubjectResponse])
async def list_subjects(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("subjects")
        .select("id, user_id, name, code, semester, created_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.post("/subjects", summary="Create a new subject", status_code=201, response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = subject.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("subjects").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/subjects/{subject_id}", summary="Delete a subject", status_code=204)
async def delete_subject(subject_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("subjects").delete().eq("id", subject_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.get("/marks", summary="List academic marks", response_model=List[MarkResponse])
async def list_marks(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("marks")
        .select("id, user_id, subject_id, exam_name, score, total, date, created_at")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.post("/marks", summary="Record a new mark", status_code=201, response_model=MarkResponse)
async def create_mark(mark: MarkCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = mark.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("marks").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/marks/{mark_id}", summary="Delete a mark", status_code=204)
async def delete_mark(mark_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("marks").delete().eq("id", mark_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.get("/learning-progress/stats", summary="Get learning progress stats", response_model=dict)
async def learning_stats(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        result = (
            supabase.from_("learning_progress")
            .select("id, user_id, date, completion_rate, courses_active, habits_streak, focus_minutes, sleep_score")
            .eq("user_id", current_user.user.id)
            .order("date", ascending=False)
            .limit(30)
            .execute()
        )
        snapshots = result.data or []
    except Exception:
        snapshots = []

    if not snapshots:
        return {"completion_rate": 0, "avg_completion_rate": 0, "trend": "stable", "snapshots": []}

    rates = [s.get("completion_rate", 0) or 0 for s in snapshots]
    avg_rate = round(sum(rates) / len(rates), 1) if rates else 0
    recent = rates[:7]
    older = rates[-14:-7] if len(rates) >= 14 else rates[:7]
    recent_avg = sum(recent) / len(recent) if recent else 0
    older_avg = sum(older) / len(older) if older else 0
    trend = "improving" if recent_avg > older_avg + 5 else ("declining" if recent_avg < older_avg - 5 else "stable")

    return {
        "completion_rate": rates[0] if rates else 0,
        "avg_completion_rate": avg_rate,
        "trend": trend,
        "snapshots": snapshots[:30],
    }


@router.get("/learning-progress/timeline", summary="Get learning progress timeline", response_model=list)
async def learning_timeline(days: int = Query(30, ge=1, le=365), current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    try:
        result = (
            supabase.from_("learning_progress")
            .select("id, user_id, date, completion_rate, courses_active, habits_streak, focus_minutes, sleep_score")
            .eq("user_id", current_user.user.id)
            .gte("date", cutoff)
            .order("date", ascending=False)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error("Failed to fetch learning timeline", error=str(e))
        return []
