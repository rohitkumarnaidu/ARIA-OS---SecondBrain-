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
    SkillAuditLogCreate, SkillAuditLogResponse,
    SkillEventSubscriptionCreate, SkillEventSubscriptionUpdate, SkillEventSubscriptionResponse,
    SkillAnalyticsSnapshotCreate, SkillAnalyticsSnapshotResponse,
    SkillWebhookQueueResponse,
    SkillTaxonomyHistoryCreate, SkillTaxonomyHistoryResponse,
    SkillUserSkillHistoryCreate, SkillUserSkillHistoryResponse,
    SkillMarketHistoryCreate, SkillMarketHistoryResponse,
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


@router.put("/roadmap-definitions/{roadmap_id}", response_model=SkillRoadmapDefinitionResponse)
async def update_roadmap_definition(roadmap_id: str, update: SkillRoadmapDefinitionCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = update.model_dump()
    response = supabase.from_("skill_roadmap_definitions").update(data).eq("roadmap_id", roadmap_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Roadmap definition not found")
    return response.data[0]


@router.delete("/roadmap-definitions/{roadmap_id}", status_code=204)
async def delete_roadmap_definition(roadmap_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmap_definitions").delete().eq("roadmap_id", roadmap_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Income Data ====================


@router.post("/income", status_code=201, response_model=SkillIncomeDataResponse)
async def create_income_data(data: SkillIncomeDataCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = data.model_dump()
    response = supabase.from_("skill_income_data").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/income", response_model=List[SkillIncomeDataResponse])
async def list_income_data(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_income_data").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Market Data Write ====================


@router.post("/market-data", status_code=201, response_model=SkillMarketDataResponse)
async def create_market_data(data: SkillMarketDataCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = data.model_dump()
    response = supabase.from_("skill_market_data").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/market-data/{skill_id}", response_model=SkillMarketDataResponse)
async def update_market_data(skill_id: str, update: SkillMarketDataCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_market_data").update(payload).eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Market data not found")
    return response.data[0]


# ==================== Certifications Write ====================


@router.post("/certifications", status_code=201, response_model=SkillCertificationResponse)
async def create_certification(cert: SkillCertificationCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = cert.model_dump()
    response = supabase.from_("skill_certifications").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/certifications/{certification_id}", response_model=SkillCertificationResponse)
async def update_certification(certification_id: str, update: SkillCertificationCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_certifications").update(payload).eq("certification_id", certification_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Certification not found")
    return response.data[0]


@router.delete("/certifications/{certification_id}", status_code=204)
async def delete_certification(certification_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_certifications").delete().eq("certification_id", certification_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Topics ====================


@router.post("/topics", status_code=201, response_model=SkillTopicResponse)
async def create_topic(topic: SkillTopicCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = topic.model_dump()
    response = supabase.from_("skill_topics").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/topics", response_model=List[SkillTopicResponse])
async def list_topics(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_topics").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


@router.put("/topics/{topic_id}", response_model=SkillTopicResponse)
async def update_topic(topic_id: str, update: SkillTopicCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_topics").update(payload).eq("topic_id", topic_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Topic not found")
    return response.data[0]


@router.delete("/topics/{topic_id}", status_code=204)
async def delete_topic(topic_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_topics").delete().eq("topic_id", topic_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Resources Write ====================


@router.post("/resources", status_code=201, response_model=SkillResourceResponse)
async def create_skill_resource(resource: SkillResourceCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = resource.model_dump()
    response = supabase.from_("skill_resources").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/resources/{resource_id}", response_model=SkillResourceResponse)
async def update_skill_resource(resource_id: str, update: SkillResourceCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_resources").update(payload).eq("resource_id", resource_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Resource not found")
    return response.data[0]


@router.delete("/resources/{resource_id}", status_code=204)
async def delete_skill_resource(resource_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_resources").delete().eq("resource_id", resource_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Learning Paths Write ====================


@router.post("/learning-paths", status_code=201, response_model=SkillLearningPathResponse)
async def create_learning_path(path: SkillLearningPathCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = path.model_dump()
    response = supabase.from_("skill_learning_paths").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/learning-paths/{path_id}", response_model=SkillLearningPathResponse)
async def update_learning_path(path_id: str, update: SkillLearningPathCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_learning_paths").update(payload).eq("path_id", path_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return response.data[0]


@router.delete("/learning-paths/{path_id}", status_code=204)
async def delete_learning_path(path_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_learning_paths").delete().eq("path_id", path_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Junction Links ====================


@router.post("/projects-link", status_code=201)
async def create_project_skill_link(link: SkillProjectLinkCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = link.model_dump()
    response = supabase.from_("skill_projects").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/projects-link", status_code=204)
async def delete_project_skill_link(project_id: str = Query(...), skill_id: str = Query(...), current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_projects").delete().eq("project_id", project_id).eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.post("/roadmaps-link", status_code=201)
async def create_roadmap_skill_link(link: SkillRoadmapLinkCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = link.model_dump()
    response = supabase.from_("skill_roadmaps").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/roadmaps-link", status_code=204)
async def delete_roadmap_skill_link(roadmap_id: str = Query(...), skill_id: str = Query(...), current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmaps").delete().eq("roadmap_id", roadmap_id).eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


@router.post("/opportunities-link", status_code=201)
async def create_opportunity_skill_link(link: SkillOpportunityLinkCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = link.model_dump()
    response = supabase.from_("skill_opportunities").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.delete("/opportunities-link", status_code=204)
async def delete_opportunity_skill_link(opportunity_id: str = Query(...), skill_id: str = Query(...), current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_opportunities").delete().eq("opportunity_id", opportunity_id).eq("skill_id", skill_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== External Mappings Write ====================


@router.post("/external-mappings", status_code=201, response_model=SkillExternalMappingResponse)
async def create_external_mapping(mapping: SkillExternalMappingCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = mapping.model_dump()
    response = supabase.from_("skill_external_mappings").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.put("/external-mappings/{mapping_id}", response_model=SkillExternalMappingResponse)
async def update_external_mapping(mapping_id: str, update: SkillExternalMappingUpdate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = update.model_dump()
    response = supabase.from_("skill_external_mappings").update(payload).eq("mapping_id", mapping_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="External mapping not found")
    return response.data[0]


@router.delete("/external-mappings/{mapping_id}", status_code=204)
async def delete_external_mapping(mapping_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_external_mappings").delete().eq("mapping_id", mapping_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return None


# ==================== Forecasts ====================


@router.post("/forecasts", status_code=201, response_model=SkillForecastResponse)
async def create_forecast(forecast: SkillForecastCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    payload = forecast.model_dump()
    response = supabase.from_("skill_forecasts").insert(payload).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/forecasts", response_model=List[SkillForecastResponse])
async def list_forecasts(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_forecasts").select("*").range(offset, offset + limit - 1)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Audit Log Endpoints ====================


@router.get("/audit-log", response_model=List[SkillAuditLogResponse])
async def list_audit_log(
    current_user=Depends(get_current_user),
    table_name: str = Query(None),
    record_id: str = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_audit_log").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if table_name:
        query = query.eq("table_name", table_name)
    if record_id:
        query = query.eq("record_id", record_id)
    response = query.execute()
    return response.data


@router.get("/audit-log/{audit_id}", response_model=SkillAuditLogResponse)
async def get_audit_entry(audit_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_audit_log").select("*").eq("audit_id", audit_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Audit entry not found")
    return response.data[0]


@router.get("/audit-log/table/{table_name}/record/{record_id}", response_model=List[SkillAuditLogResponse])
async def get_audit_for_record(table_name: str, record_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_audit_log").select("*").eq("table_name", table_name).eq("record_id", record_id).order("created_at", desc=True).execute()
    return response.data


# ==================== Event Subscription Endpoints ====================


@router.get("/event-subscriptions", response_model=List[SkillEventSubscriptionResponse])
async def list_event_subscriptions(
    current_user=Depends(get_current_user),
    is_active: bool = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_event_subscriptions").select("*").range(offset, offset + limit - 1).order("name")
    if is_active is not None:
        query = query.eq("is_active", is_active)
    response = query.execute()
    return response.data


@router.post("/event-subscriptions", status_code=201, response_model=SkillEventSubscriptionResponse)
async def create_event_subscription(sub: SkillEventSubscriptionCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = sub.model_dump()
    response = supabase.from_("skill_event_subscriptions").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/event-subscriptions/{subscription_id}", response_model=SkillEventSubscriptionResponse)
async def get_event_subscription(subscription_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_event_subscriptions").select("*").eq("subscription_id", subscription_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return response.data[0]


@router.put("/event-subscriptions/{subscription_id}", response_model=SkillEventSubscriptionResponse)
async def update_event_subscription(subscription_id: str, update: SkillEventSubscriptionUpdate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    response = supabase.from_("skill_event_subscriptions").update(update_data).eq("subscription_id", subscription_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return response.data[0]


@router.delete("/event-subscriptions/{subscription_id}", status_code=204)
async def delete_event_subscription(subscription_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    supabase.from_("skill_event_subscriptions").delete().eq("subscription_id", subscription_id).execute()
    return None


# ==================== Events GET Endpoints ====================


@router.get("/events", response_model=List[SkillEventResponse])
async def list_events(
    current_user=Depends(get_current_user),
    event_type: str = Query(None),
    aggregate_type: str = Query(None),
    aggregate_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_events").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if event_type:
        query = query.eq("event_type", event_type)
    if aggregate_type:
        query = query.eq("aggregate_type", aggregate_type)
    if aggregate_id:
        query = query.eq("aggregate_id", aggregate_id)
    response = query.execute()
    return response.data


@router.get("/events/{event_id}", response_model=SkillEventResponse)
async def get_event(event_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_events").select("*").eq("event_id", event_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
    return response.data[0]


# ==================== Analytics Snapshot Endpoints ====================


@router.get("/analytics-snapshots", response_model=List[SkillAnalyticsSnapshotResponse])
async def list_analytics_snapshots(
    current_user=Depends(get_current_user),
    user_id: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    limit: int = Query(100, ge=1, le=365),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_analytics_snapshots").select("*").range(offset, offset + limit - 1).order("snapshot_date", desc=True)
    if user_id:
        query = query.eq("user_id", user_id)
    if from_date:
        query = query.gte("snapshot_date", from_date)
    if to_date:
        query = query.lte("snapshot_date", to_date)
    response = query.execute()
    return response.data


@router.get("/analytics-snapshots/latest", response_model=SkillAnalyticsSnapshotResponse)
async def get_latest_analytics_snapshot(current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    user_id = current_user.user.id
    response = supabase.from_("skill_analytics_snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="No analytics snapshots found")
    return response.data[0]


@router.post("/analytics-snapshots/trigger-refresh", status_code=202)
async def trigger_analytics_refresh(current_user=Depends(get_current_user)):
    return {"status": "queued", "message": "Analytics refresh triggered"}


# ==================== Webhook Queue Endpoints (Admin) ====================


@router.get("/webhook-queue", response_model=List[SkillWebhookQueueResponse])
async def list_webhook_queue(
    current_user=Depends(get_current_user),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_webhook_queue").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    response = query.execute()
    return response.data


# ==================== Taxonomy History Endpoints ====================


@router.get("/taxonomy-history", response_model=List[SkillTaxonomyHistoryResponse])
async def list_taxonomy_history(
    current_user=Depends(get_current_user),
    entity_type: str = Query(None),
    entity_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_taxonomy_history").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if entity_type:
        query = query.eq("entity_type", entity_type)
    if entity_id:
        query = query.eq("entity_id", entity_id)
    response = query.execute()
    return response.data


# ==================== User Skill History Endpoints ====================


@router.get("/user-skill-history", response_model=List[SkillUserSkillHistoryResponse])
async def list_user_skill_history(
    current_user=Depends(get_current_user),
    user_id: str = Query(None),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_user_skill_history").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if user_id:
        query = query.eq("user_id", user_id)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Market History Endpoints ====================


@router.get("/market-history", response_model=List[SkillMarketHistoryResponse])
async def list_market_history(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_market_history").select("*").range(offset, offset + limit - 1).order("created_at", desc=True)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    response = query.execute()
    return response.data


# ==================== Materialized View Endpoints ====================


@router.post("/materialized-views/refresh", status_code=202)
async def refresh_all_views(current_user=Depends(get_current_user)):
    return {"status": "queued", "message": "Materialized view refresh triggered"}


@router.get("/materialized-views/user-proficiency", response_model=List)
async def get_user_proficiency(current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    user_id = current_user.user.id
    response = supabase.from_("mv_skill_user_proficiency").select("*").eq("user_id", user_id).execute()
    return response.data


@router.get("/materialized-views/market-intelligence", response_model=List)
async def get_market_intelligence(current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("mv_skill_market_intelligence").select("*").order("skill_health", desc=True).limit(50).execute()
    return response.data


# ==================== Roadmap Definitions GET by ID ====================


@router.get("/roadmap-definitions/{roadmap_id}", response_model=SkillRoadmapDefinitionResponse)
async def get_roadmap_definition(roadmap_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmap_definitions").select("*").eq("roadmap_id", roadmap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Roadmap definition not found")
    return response.data[0]
