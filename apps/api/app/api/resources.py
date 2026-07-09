from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse

router = APIRouter()


@router.get("/", summary="List all resources", response_model=List[ResourceResponse])
async def get_resources(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .select("id, user_id, title, url, tags, created_at")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{resource_id}", summary="Get a resource by ID", response_model=ResourceResponse)
async def get_resource(resource_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("resources")
        .select("id, user_id, title, url, tags, created_at")
        .eq("id", resource_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Resource not found")
    return response.data[0]


@router.post("/", summary="Create a new resource", status_code=201, response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = resource.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("resources").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{resource_id}", summary="Update a resource", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    resource_update: ResourceUpdate,
    current_user=Depends(get_current_user),
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in resource_update.model_dump().items() if v is not None}
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


@router.delete("/{resource_id}", summary="Delete a resource", status_code=204)
async def delete_resource(resource_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("resources").delete().eq("id", resource_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
