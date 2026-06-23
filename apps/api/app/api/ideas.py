from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.idea import IdeaCreate, IdeaUpdate, IdeaResponse

router = APIRouter()


@router.get("/", summary="List all ideas", response_model=List[IdeaResponse])
async def get_ideas(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("ideas")
        .select("id, user_id, title, description, stage, created_at, updated_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{idea_id}", summary="Get an idea by ID", response_model=IdeaResponse)
async def get_idea(idea_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("ideas").select("id, user_id, title, description, stage, created_at, updated_at").eq("id", idea_id).eq("user_id", current_user.user.id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Idea not found")
    return response.data[0]


@router.post("/", summary="Create a new idea", status_code=201, response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = idea.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "raw"
    response = supabase.from_("ideas").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{idea_id}", summary="Update an idea", response_model=IdeaResponse)
async def update_idea(idea_id: str, idea_update: IdeaUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in idea_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("ideas").update(update_data).eq("id", idea_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Idea not found")
    return response.data[0]


@router.delete("/{idea_id}", summary="Delete an idea", status_code=204)
async def delete_idea(idea_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("ideas").delete().eq("id", idea_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
