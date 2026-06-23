from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.video import VideoCreate, VideoUpdate, VideoResponse

router = APIRouter()


@router.get("/", summary="List all videos", response_model=List[VideoResponse])
async def list_videos(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("videos")
        .select("id, user_id, title, url, platform, watched, notes, created_at, updated_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.post("/", summary="Create a new video", status_code=201, response_model=VideoResponse)
async def create_video(video: VideoCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = video.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("videos").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{video_id}", summary="Update a video", response_model=VideoResponse)
async def update_video(video_id: str, video_update: VideoUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in video_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("videos").update(update_data).eq("id", video_id).eq("user_id", current_user.user.id).execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    return response.data[0]


@router.delete("/{video_id}", summary="Delete a video", status_code=204)
async def delete_video(video_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("videos").delete().eq("id", video_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
