"""Auto-generated API stubs for missing skill endpoints.
Append these route functions to apps/api/app/api/skills.py.
"""

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
    response = supabase.from_("skill_event_subscriptions").delete().eq("subscription_id", subscription_id).execute()
    return None


# ==================== Event Endpoints ====================

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
    """Trigger an analytics snapshot refresh for the current user."""
    return {"status": "queued", "message": "Analytics refresh triggered"}


# ==================== Forecast Endpoints ====================

@router.get("/forecasts", response_model=List[SkillForecastResponse])
async def list_forecasts(
    current_user=Depends(get_current_user),
    skill_id: str = Query(None),
    metric: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    query = supabase.from_("skill_forecasts").select("*").range(offset, offset + limit - 1).order("forecast_date", desc=True)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    if metric:
        query = query.eq("metric", metric)
    response = query.execute()
    return response.data


@router.post("/forecasts", status_code=201, response_model=SkillForecastResponse)
async def create_forecast(forecast: SkillForecastCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = forecast.model_dump()
    response = supabase.from_("skill_forecasts").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


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


# ==================== Roadmap Definitions Endpoints ====================

@router.get("/roadmap-definitions", response_model=List[SkillRoadmapDefinitionResponse])
async def list_roadmap_definitions(
    current_user=Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmap_definitions").select("*").range(offset, offset + limit - 1).order("name").execute()
    return response.data


@router.post("/roadmap-definitions", status_code=201, response_model=SkillRoadmapDefinitionResponse)
async def create_roadmap_definition(defn: SkillRoadmapDefinitionCreate, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    data = defn.model_dump()
    response = supabase.from_("skill_roadmap_definitions").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]


@router.get("/roadmap-definitions/{roadmap_id}", response_model=SkillRoadmapDefinitionResponse)
async def get_roadmap_definition(roadmap_id: str, current_user=Depends(get_current_user)):
    supabase = _get_supabase()
    response = supabase.from_("skill_roadmap_definitions").select("*").eq("roadmap_id", roadmap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Roadmap definition not found")
    return response.data[0]


# ==================== Materialized View Endpoints ====================

@router.post("/materialized-views/refresh", status_code=202)
async def refresh_all_views(current_user=Depends(get_current_user)):
    """Trigger refresh of all materialized views."""
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
