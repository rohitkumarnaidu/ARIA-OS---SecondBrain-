from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class IdeaCreate(BaseModel):
    title: str
    description: Optional[str] = None


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    market_research: Optional[str] = None
    competitors: Optional[str] = None


class IdeaResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    market_research: Optional[str]
    competitors: Optional[str]
    created_at: str


@router.get("/", response_model=List[IdeaResponse])
async def get_ideas(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("ideas")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = idea.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "raw"
    response = supabase.from_("ideas").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: str, idea_update: IdeaUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in idea_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("ideas")
        .update(update_data)
        .eq("id", idea_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Idea not found")
    return response.data[0]


@router.delete("/{idea_id}")
async def delete_idea(idea_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("ideas")
        .delete()
        .eq("id", idea_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Idea deleted"}
