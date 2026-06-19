from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.academic import SubjectCreate, SubjectResponse, MarkCreate, MarkResponse

router = APIRouter()


@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("subjects")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.post("/subjects", status_code=201, response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = subject.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("subjects").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/subjects/{subject_id}", status_code=204)
async def delete_subject(subject_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("subjects").delete().eq("id", subject_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.get("/marks", response_model=List[MarkResponse])
async def list_marks(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("marks")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.post("/marks", status_code=201, response_model=MarkResponse)
async def create_mark(mark: MarkCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = mark.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("marks").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/marks/{mark_id}", status_code=204)
async def delete_mark(mark_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("marks").delete().eq("id", mark_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
