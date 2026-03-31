from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class IncomeCreate(BaseModel):
    source_type: str
    amount: float
    platform: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    hours_spent: Optional[float] = None


class IncomeUpdate(BaseModel):
    source_type: Optional[str] = None
    amount: Optional[float] = None
    platform: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    hours_spent: Optional[float] = None


class IncomeResponse(BaseModel):
    id: str
    user_id: str
    source_type: str
    amount: float
    platform: Optional[str]
    description: Optional[str]
    date: str
    hours_spent: Optional[float]
    effective_hourly_rate: Optional[float]
    created_at: str


@router.get("/", response_model=List[IncomeResponse])
async def get_income(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("income_entries")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("date", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=IncomeResponse)
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


@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: str, income_update: IncomeUpdate, current_user=Depends(get_current_user)
):
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


@router.delete("/{income_id}")
async def delete_income(income_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("income_entries")
        .delete()
        .eq("id", income_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Income deleted"}
