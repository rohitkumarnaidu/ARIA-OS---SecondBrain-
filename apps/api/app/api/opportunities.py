from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityResponse

router = APIRouter()


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("opportunities")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("opportunities").select("*").eq("id", opportunity_id).eq("user_id", current_user.user.id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return response.data[0]


@router.post("/", status_code=201, response_model=OpportunityResponse)
async def create_opportunity(opportunity: OpportunityCreate, current_user=Depends(get_current_user)):
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
    update_data = {k: v for k, v in opportunity_update.model_dump().items() if v is not None}
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


@router.delete("/{opp_id}", status_code=204)
async def delete_opportunity(opp_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("opportunities").delete().eq("id", opp_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
