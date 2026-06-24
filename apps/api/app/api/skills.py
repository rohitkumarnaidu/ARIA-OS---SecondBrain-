from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.skill import (
    SkillCategoryCreate, SkillCategoryUpdate, SkillCategoryResponse,
    SkillCreate, SkillUpdate, SkillResponse,
    SkillRelationshipCreate, SkillRelationshipUpdate, SkillRelationshipResponse,
    TagCreate, TagUpdate, TagResponse, SkillTagCreate,
    SkillExternalMappingCreate, SkillExternalMappingUpdate, SkillExternalMappingResponse,
    SkillRoadmapDefinitionCreate, SkillRoadmapDefinitionResponse,
    UserSkillCreate, UserSkillUpdate, UserSkillResponse,
    UserSkillEvidenceCreate, UserSkillEvidenceResponse,
    UserSkillTargetCreate, UserSkillTargetUpdate, UserSkillTargetResponse,
    UserSkillAssessmentCreate, UserSkillAssessmentResponse,
    SkillMarketDataCreate, SkillMarketDataResponse,
    SkillIncomeDataCreate, SkillIncomeDataResponse,
    SkillCertificationCreate, SkillCertificationResponse,
    SkillProjectLinkCreate, SkillRoadmapLinkCreate, SkillOpportunityLinkCreate,
    SkillTopicCreate, SkillTopicResponse,
    SkillResourceCreate, SkillResourceResponse,
    SkillLearningPathCreate, SkillLearningPathResponse,
    SkillAIRecommendationCreate, SkillAIRecommendationUpdate, SkillAIRecommendationResponse,
    SkillActivityLogCreate, SkillActivityLogResponse,
    SkillEventCreate, SkillEventResponse,
    SkillForecastCreate, SkillForecastResponse,
)

router = APIRouter()


def _get_supabase():
    return get_supabase_client()


# ==================== Skill Categories ====================


@router.get("/categories", response_model=List[SkillCategoryResponse])
async def list_categories(
    current_user=Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    response = supabase.from_("skill_categories").select("*").range(offset, offset + limit - 1).order("sort_order").execute()
    return response.data


@router.post("/categories", status_code=201, response_model=SkillCategoryResponse)
async def create_category(category: SkillCategoryCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = category.model_dump()
    response = supabase.from_("skill_categories").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/categories/{category_id}", response_model=SkillCategoryResponse)
async def get_category(category_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_categories").select("*").eq("category_id", category_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Category not found")
    return response.data[0]


@router.put("/categories/{category_id}", response_model=SkillCategoryResponse)
async def update_category(category_id: str, update: SkillCategoryUpdate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    response = supabase.from_("skill_categories").update(update_data).eq("category_id", category_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Category not found")
    return response.data[0]


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_categories").delete().eq("category_id", category_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Skills ====================


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
    current_user=Depends(get_current_user),
    category_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skills").select("*").range(offset, offset + limit - 1).order("name")
    if category_id:
        query = query.eq("category_id", category_id)
    response = query.execute()
    return response.data


@router.post("/", status_code=201, response_model=SkillResponse)
async def create_skill(skill: SkillCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = skill.model_dump()
    response = supabase.from_("skills").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skills").select("*").eq("skill_id", skill_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Skill not found")
    return response.data[0]


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: str, update: SkillUpdate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    response = supabase.from_("skills").update(update_data).eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Skill not found")
    return response.data[0]


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skills").delete().eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Skill Relationships ====================


@router.get("/relationships", response_model=List[SkillRelationshipResponse])
async def list_relationships(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    relationship_type: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_relationships").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.or_(f"from_skill_id.eq.{skill_id},to_skill_id.eq.{skill_id}")
    if relationship_type:
        query = query.eq("relationship_type", relationship_type)
    response = query.execute()
    return response.data


@router.post("/relationships", status_code=201, response_model=SkillRelationshipResponse)
async def create_relationship(rel: SkillRelationshipCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = rel.model_dump()
    response = supabase.from_("skill_relationships").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/relationships/{relationship_id}", status_code=204)
async def delete_relationship(relationship_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_relationships").delete().eq("relationship_id", relationship_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Tags ====================


@router.get("/tags", response_model=List[TagResponse])
async def list_tags(current_user=Depends(get_current_user), limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    supabase = _get_supabase()
    response = supabase.from_("tags").select("*").range(offset, offset + limit - 1).order("name").execute()
    return response.data


@router.post("/tags", status_code=201, response_model=TagResponse)
async def create_tag(tag: TagCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = tag.model_dump()
    response = supabase.from_("tags").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.post("/tags/link", status_code=201)
async def link_skill_tag(link: SkillTagCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = link.model_dump()
    response = supabase.from_("skill_tags").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"status": "linked"}


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("tags").delete().eq("tag_id", tag_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== External Mappings ====================


@router.get("/external-mappings", response_model=List[SkillExternalMappingResponse])
async def list_external_mappings(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    system: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_external_mappings").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    if system:
        query = query.eq("external_system", system)
    response = query.execute()
    return response.data


# ==================== User Skills ====================


@router.get("/user-skills", response_model=List[UserSkillResponse])
async def list_user_skills(
    current_user=Depends(get_current_user),
    state: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("user_skills").select("*").eq("user_id", user_id).range(offset, offset + limit - 1)
    if state:
        query = query.eq("state", state)
    response = query.execute()
    return response.data


@router.post("/user-skills", status_code=201, response_model=UserSkillResponse)
async def create_user_skill(us: UserSkillCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = us.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("user_skills").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/user-skills/{user_skill_id}", response_model=UserSkillResponse)
async def update_user_skill(user_skill_id: str, update: UserSkillUpdate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    response = supabase.from_("user_skills").update(update_data).eq("user_skill_id", user_skill_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="User skill not found")
    return response.data[0]


@router.delete("/user-skills/{user_skill_id}", status_code=204)
async def delete_user_skill(user_skill_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("user_skills").delete().eq("user_skill_id", user_skill_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== User Skill Evidence ====================


@router.get("/evidence", response_model=List[UserSkillEvidenceResponse])
async def list_evidence(
    current_user=Depends(get_current_user),
    user_skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("user_skill_evidence").select("*").eq("user_id", user_id).range(offset, offset + limit - 1)
    if user_skill_id:
        query = query.eq("user_skill_id", user_skill_id)
    response = query.execute()
    return response.data


@router.post("/evidence", status_code=201, response_model=UserSkillEvidenceResponse)
async def create_evidence(ev: UserSkillEvidenceCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = ev.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("user_skill_evidence").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


# ==================== User Skill Targets ====================


@router.get("/targets", response_model=List[UserSkillTargetResponse])
async def list_targets(
    current_user=Depends(get_current_user),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("user_skill_targets").select("*").eq("user_id", user_id).range(offset, offset + limit - 1)
    if status:
        query = query.eq("status", status)
    response = query.execute()
    return response.data


@router.post("/targets", status_code=201, response_model=UserSkillTargetResponse)
async def create_target(target: UserSkillTargetCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = target.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("user_skill_targets").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


# ==================== Assessments ====================


@router.get("/assessments", response_model=List[UserSkillAssessmentResponse])
async def list_assessments(
    current_user=Depends(get_current_user),
    user_skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("user_skill_assessments").select("*").eq("user_id", user_id).range(offset, offset + limit - 1)
    if user_skill_id:
        query = query.eq("user_skill_id", user_skill_id)
    response = query.execute()
    return response.data


@router.post("/assessments", status_code=201, response_model=UserSkillAssessmentResponse)
async def create_assessment(assessment: UserSkillAssessmentCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = assessment.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("user_skill_assessments").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


# ==================== Market Data ====================


@router.get("/market-data", response_model=List[SkillMarketDataResponse])
async def list_market_data(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_market_data").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Certifications ====================


@router.get("/certifications", response_model=List[SkillCertificationResponse])
async def list_certifications(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_certifications").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Learning Paths ====================


@router.get("/learning-paths", response_model=List[SkillLearningPathResponse])
async def list_learning_paths(
    current_user=Depends(get_current_user),
    target_skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_learning_paths").select("*").range(offset, offset + limit - 1)
    if target_skill_id:
        query = query.eq("target_skill_id", target_skill_id)
    response = query.execute()
    return response.data


# ==================== Resources ====================


@router.get("/resources", response_model=List[SkillResourceResponse])
async def list_skill_resources(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    resource_type: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_resources").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    if resource_type:
        query = query.eq("resource_type", resource_type)
    response = query.execute()
    return response.data


# ==================== AI Recommendations ====================


@router.get("/recommendations", response_model=List[SkillAIRecommendationResponse])
async def list_recommendations(
    current_user=Depends(get_current_user),
    recommendation_type: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("skill_ai_recommendations").select("*").eq("user_id", user_id).range(offset, offset + limit - 1)
    if recommendation_type:
        query = query.eq("recommendation_type", recommendation_type)
    response = query.execute()
    return response.data


@router.put("/recommendations/{recommendation_id}/accept")
async def accept_recommendation(recommendation_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_ai_recommendations").update({"accepted": True}).eq("recommendation_id", recommendation_id).eq("user_id", current_user.user.id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return response.data[0]


# ==================== Activity Log ====================


@router.get("/activity", response_model=List[SkillActivityLogResponse])
async def list_activity(
    current_user=Depends(get_current_user),
    activity_type: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    user_id = current_user.user.id
    query = supabase.from_("skill_user_activity_log").select("*").eq("user_id", user_id).range(offset, offset + limit - 1).order("created_at", desc=True)
    if activity_type:
        query = query.eq("activity_type", activity_type)
    response = query.execute()
    return response.data


@router.post("/activity", status_code=201, response_model=SkillActivityLogResponse)
async def log_activity(activity: SkillActivityLogCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = activity.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("skill_user_activity_log").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


# ==================== Events (internal) ====================


@router.post("/events", status_code=201, response_model=SkillEventResponse)
async def publish_event(event: SkillEventCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = event.model_dump()
    data["user_id"] = current_user.user.id
    response = supabase.from_("skill_events").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


# ==================== Roadmap Definitions ====================


@router.get("/roadmap-definitions", response_model=List[SkillRoadmapDefinitionResponse])
async def list_roadmap_definitions(current_user=Depends(get_current_user), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmap_definitions").select("*").range(offset, offset + limit - 1).execute()
    return response.data


@router.post("/roadmap-definitions", status_code=201, response_model=SkillRoadmapDefinitionResponse)
async def create_roadmap_definition(defn: SkillRoadmapDefinitionCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = defn.model_dump()
    response = supabase.from_("skill_roadmap_definitions").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]
