from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse

router = APIRouter()


@router.get("/", summary="List all income entries", response_model=List[IncomeResponse])
async def get_income(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("income_entries")
        .select("id, user_id, amount, source, date, hours_spent, effective_hourly_rate, created_at")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{income_id}", summary="Get an income entry by ID", response_model=IncomeResponse)
async def get_income_entry(income_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("income_entries").select("id, user_id, amount, source, date, hours_spent, effective_hourly_rate, created_at").eq("id", income_id).eq("user_id", current_user.user.id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Income entry not found")
    return response.data[0]


@router.post("/", summary="Create an income entry", status_code=201, response_model=IncomeResponse)
async def create_income(income: IncomeCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = income.model_dump()
    data["user_id"] = current_user.user.id
    if data.get("hours_spent") and data.get("amount"):
        data["effective_hourly_rate"] = round(data["amount"] / data["hours_spent"], 2)
    response = supabase.from_("income_entries").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{income_id}", summary="Update an income entry", response_model=IncomeResponse)
async def update_income(income_id: str, income_update: IncomeUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in income_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("income_entries")
        .update(update_data)
        .eq("id", income_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Income not found")
    return response.data[0]


@router.delete("/{income_id}", summary="Delete an income entry", status_code=204)
async def delete_income(income_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("income_entries").delete().eq("id", income_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
