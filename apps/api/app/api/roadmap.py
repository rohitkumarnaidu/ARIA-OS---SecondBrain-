from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.roadmap import RoadmapMilestoneCreate, RoadmapMilestoneUpdate, RoadmapMilestoneResponse

router = APIRouter()


@router.get("/", response_model=List[RoadmapMilestoneResponse])
async def list_milestones(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("roadmaps")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{milestone_id}", response_model=RoadmapMilestoneResponse)
async def get_milestone(milestone_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("roadmaps")
        .select("*")
        .eq("id", milestone_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return response.data[0]


@router.post("/", status_code=201, response_model=RoadmapMilestoneResponse)
async def create_milestone(
    milestone: RoadmapMilestoneCreate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    data = milestone.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("roadmaps").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{milestone_id}", response_model=RoadmapMilestoneResponse)
async def update_milestone(
    milestone_id: str,
    milestone_update: RoadmapMilestoneUpdate,
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in milestone_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("roadmaps")
        .update(update_data)
        .eq("id", milestone_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return response.data[0]


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(milestone_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("roadmaps").delete().eq("id", milestone_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
