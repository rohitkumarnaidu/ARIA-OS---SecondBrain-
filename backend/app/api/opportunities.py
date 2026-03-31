from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class OpportunityCreate(BaseModel):
    title: str
    company: Optional[str] = None
    url: str
    opportunity_type: str = "internship"
    description: Optional[str] = None
    skills_required: Optional[List[str]] = []
    deadline: Optional[str] = None


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    opportunity_type: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[List[str]] = None
    deadline: Optional[str] = None
    status: Optional[str] = None


class OpportunityResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: Optional[str]
    url: str
    opportunity_type: str
    description: Optional[str]
    skills_required: List[str]
    deadline: Optional[str]
    status: str
    created_at: str


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("opportunities")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=OpportunityResponse)
async def create_opportunity(
    opportunity: OpportunityCreate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    data = opportunity.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "new"
    response = supabase.from_("opportunities").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{opp_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opp_id: str,
    opportunity_update: OpportunityUpdate,
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    update_data = {
        k: v for k, v in opportunity_update.model_dump().items() if v is not None
    }
    response = (
        supabase.from_("opportunities")
        .update(update_data)
        .eq("id", opp_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return response.data[0]


@router.delete("/{opp_id}")
async def delete_opportunity(opp_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("opportunities")
        .delete()
        .eq("id", opp_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Opportunity deleted"}
