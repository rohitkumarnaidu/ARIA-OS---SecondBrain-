from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("projects")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("projects").select("*").eq("id", project_id).eq("user_id", current_user.user.id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return response.data[0]


@router.post("/", status_code=201, response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user=Depends(get_current_user)):
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
    update_data = {k: v for k, v in project_update.model_dump().items() if v is not None}
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


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("projects").delete().eq("id", project_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
