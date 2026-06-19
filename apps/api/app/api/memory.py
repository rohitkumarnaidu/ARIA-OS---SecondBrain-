from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse

router = APIRouter()


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    response = (
        supabase.from_("memory")
        .select("*")
        .eq("user_id", current_user.user.id)
        .order("created_at", ascending=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("memory").select("*").eq("id", memory_id).eq("user_id", current_user.user.id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Memory not found")
    return response.data[0]


@router.post("/", status_code=201, response_model=MemoryResponse)
async def create_memory(memory: MemoryCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = memory.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("memory").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str, memory_update: MemoryUpdate, current_user=Depends(get_current_user)
):
    supabase = get_supabase_client()
    update_data = {k: v for k, v in memory_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("memory")
        .update(update_data)
        .eq("id", memory_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Memory not found")
    return response.data[0]


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(memory_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("memory").delete().eq("id", memory_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None
