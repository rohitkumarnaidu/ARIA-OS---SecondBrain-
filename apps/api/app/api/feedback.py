from fastapi import APIRouter, Depends, HTTPException
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackSummary
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", summary="Submit feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(fb: FeedbackCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    record = {
        "id": str(uuid4()),
        "user_id": current_user.user.id,
        "source": fb.source,
        "target_id": fb.target_id,
        "rating": fb.rating,
        "comment": fb.comment,
        "metadata": fb.metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        result = supabase.from_("feedback").insert(record).execute()
        return result.data[0] if result.data else record
    except Exception as e:
        logger.error("Failed to save feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@router.get("/summary", summary="Get feedback summary", response_model=FeedbackSummary)
async def feedback_summary(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        result = supabase.from_("feedback").select("id, user_id, source, target_id, rating, comment, metadata, created_at").eq("user_id", current_user.user.id).execute()
        items = result.data or []
    except Exception as e:
        logger.error("Failed to fetch feedback summary", error=str(e))
        return FeedbackSummary(total=0, positive=0, negative=0, positive_rate=0.0, by_source={})

    total = len(items)
    pos = sum(1 for i in items if i.get("rating", 0) >= 4)
    neg = sum(1 for i in items if i.get("rating", 0) <= 2)
    by_source: dict[str, int] = {}
    for i in items:
        src = i.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    return FeedbackSummary(
        total=total,
        positive=pos,
        negative=neg,
        positive_rate=round(pos / max(total, 1) * 100, 1),
        by_source=by_source,
    )
