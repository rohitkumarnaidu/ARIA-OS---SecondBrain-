from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    phase: str = "planning"
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    next_action: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    next_action: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    phase: str
    github_url: Optional[str]
    live_url: Optional[str]
    next_action: Optional[str]
    created_at: str


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    data = project.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("projects").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    update_data = {
        k: v for k, v in project_update.model_dump().items() if v is not None
    }
    response = (
        supabase.from_("projects")
        .update(update_data)
        .eq("id", project_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return response.data[0]


@router.delete("/{project_id}")
async def delete_project(project_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .delete()
        .eq("id", project_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Project deleted"}
