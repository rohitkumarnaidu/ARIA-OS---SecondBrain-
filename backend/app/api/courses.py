from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class CourseCreate(BaseModel):
    title: str
    platform: str
    url: Optional[str] = None
    total_videos: Optional[int] = 0
    deadline: Optional[str] = None
    why_enrolled: Optional[str] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    total_videos: Optional[int] = None
    completed_videos: Optional[int] = None
    deadline: Optional[str] = None
    why_enrolled: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(BaseModel):
    id: str
    user_id: str
    title: str
    platform: str
    url: Optional[str]
    total_videos: Optional[int]
    completed_videos: int
    deadline: Optional[str]
    why_enrolled: Optional[str]
    status: str
    created_at: str


@router.get("/", response_model=List[CourseResponse])
async def get_courses(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("courses")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = course.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "not_started"
    data["completed_videos"] = 0
    if data.get("deadline"):
        data["deadline"] = datetime.fromisoformat(
            data["deadline"].replace("Z", "+00:00")
        ).isoformat()
    response = supabase.from_("courses").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str, course_update: CourseUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in course_update.model_dump().items() if v is not None}
    if update_data.get("deadline") and update_data["deadline"]:
        try:
            update_data["deadline"] = datetime.fromisoformat(
                update_data["deadline"].replace("Z", "+00:00")
            ).isoformat()
        except:
            pass
    response = (
        supabase.from_("courses")
        .update(update_data)
        .eq("id", course_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Course not found")
    return response.data[0]


@router.delete("/{course_id}")
async def delete_course(course_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("courses")
        .delete()
        .eq("id", course_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Course deleted"}
