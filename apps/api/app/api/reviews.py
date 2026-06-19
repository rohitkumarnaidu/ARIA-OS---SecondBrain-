from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.review import WeeklyReviewRead

router = APIRouter()


@router.get("/", response_model=List[WeeklyReviewRead])
async def list_reviews(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("weekly_reviews")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("week_start", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/latest", response_model=Optional[WeeklyReviewRead])
async def get_latest_review(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("weekly_reviews")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("week_start", ascending=False)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


@router.get("/{review_id}", response_model=WeeklyReviewRead)
async def get_review(review_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("weekly_reviews")
        .select("*")
        .eq("id", review_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Review not found")
    return response.data[0]
