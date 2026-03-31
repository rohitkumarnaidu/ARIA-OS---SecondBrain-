from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()


class ResourceCreate(BaseModel):
    title: str
    url: str
    resource_type: str = "article"
    tags: Optional[List[str]] = []
    notes: Optional[str] = None


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_archived: Optional[bool] = None


class ResourceResponse(BaseModel):
    id: str
    user_id: str
    title: str
    url: str
    resource_type: str
    tags: List[str]
    notes: Optional[str]
    is_archived: bool
    created_at: str


@router.get("/", response_model=List[ResourceResponse])
async def get_resources(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .execute()
    )
    return response.data


@router.post("/", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    data = resource.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("resources").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    resource_update: ResourceUpdate,
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    update_data = {
        k: v for k, v in resource_update.model_dump().items() if v is not None
    }
    response = (
        supabase.from_("resources")
        .update(update_data)
        .eq("id", resource_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Resource not found")
    return response.data[0]


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .delete()
        .eq("id", resource_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Resource deleted"}
