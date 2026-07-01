from pydantic import BaseModel
from typing import Optional
from enum import Enum


class RelationshipType(str, Enum):
    prerequisite = "prerequisite"
    related_to = "related_to"
    supersedes = "supersedes"
    variant_of = "variant_of"
    similar_to = "similar_to"
    recommended_before = "recommended_before"
    complementary = "complementary"
    alternative = "alternative"


class UserSkillState(str, Enum):
    planned = "planned"
    learning = "learning"
    practicing = "practicing"
    active = "active"
    reviewing = "reviewing"
    archived = "archived"
    deprecated = "deprecated"


class EvidenceSourceType(str, Enum):
    project = "project"
    github = "github"
    certification = "certification"
    hackathon = "hackathon"
    freelance = "freelance"
    opensource = "opensource"
    assessment = "assessment"
    work_experience = "work_experience"
    course = "course"
    publication = "publication"
    patent = "patent"
    award = "award"


class EvidenceState(str, Enum):
    raw = "raw"
    pending_verification = "pending_verification"
    verified = "verified"
    verified_auto = "verified_auto"
    verified_ai = "verified_ai"
    verified_human = "verified_human"
    rejected = "rejected"
    flagged = "flagged"
    active = "active"
    expired = "expired"


class TargetPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TargetStatus(str, Enum):
    active = "active"
    in_progress = "in_progress"
    achieved = "achieved"
    paused = "paused"
    abandoned = "abandoned"
    expired = "expired"


class AssessmentType(str, Enum):
    self = "self"
    ai_evaluated = "ai_evaluated"
    auto_mcq = "auto_mcq"
    peer_review = "peer_review"
    human_review = "human_review"
    project_evaluation = "project_evaluation"
    certification_equivalency = "certification_equivalency"


class AssessmentStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    expired = "expired"
    invalidated = "invalidated"


class VersionChangeType(str, Enum):
    created = "created"
    level_changed = "level_changed"
    state_changed = "state_changed"
    evidence_added = "evidence_added"
    metadata_updated = "metadata_updated"
    archived = "archived"
    deprecated = "deprecated"
    restored = "restored"


class MappingType(str, Enum):
    exact = "exact"
    broader = "broader"
    narrower = "narrower"
    related = "related"
    close_match = "close_match"


class ExternalSystem(str, Enum):
    linkedin = "linkedin"
    esco = "esco"
    onet = "onet"
    workday = "workday"
    bamboohr = "bamboohr"
    cornerstone = "cornerstone"
    docebo = "docebo"
    greenhouse = "greenhouse"
    lever = "lever"
    custom = "custom"


class IncomeSource(str, Enum):
    employment = "employment"
    freelance = "freelance"
    consulting = "consulting"
    content = "content"
    product = "product"
    agency = "agency"
    teaching = "teaching"
    opensource = "opensource"
    digital = "digital"
    affiliate = "affiliate"


class ResourceType(str, Enum):
    course = "course"
    book = "book"
    tutorial = "tutorial"
    video = "video"
    article = "article"
    documentation = "documentation"
    tool = "tool"
    workshop = "workshop"
    podcast = "podcast"
    certification_prep = "certification_prep"


class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class RecommendationType(str, Enum):
    learn = "learn"
    improve = "improve"
    drop = "drop"
    emerging = "emerging"
    opportunity_readiness = "opportunity_readiness"
    career_path = "career_path"
    resource_suggestion = "resource_suggestion"
    certification_suggestion = "certification_suggestion"


class ActivityType(str, Enum):
    skill_added = "skill_added"
    level_changed = "level_changed"
    evidence_submitted = "evidence_submitted"
    assessment_taken = "assessment_taken"
    target_set = "target_set"
    target_achieved = "target_achieved"
    recommendation_viewed = "recommendation_viewed"
    recommendation_accepted = "recommendation_accepted"
    skill_archived = "skill_archived"
    skill_deprecated = "skill_deprecated"
    skill_tree_viewed = "skill_tree_viewed"
    dashboard_viewed = "dashboard_viewed"
    market_data_viewed = "market_data_viewed"
    income_data_viewed = "income_data_viewed"
    career_readiness_viewed = "career_readiness_viewed"


class DataFreshness(str, Enum):
    current = "current"
    stale = "stale"
    refreshing = "refreshing"


# === Core Taxonomy Models ===


class SkillCategoryBase(BaseModel):
    name: str
    slug: str
    description: str = ""
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    parent_category_id: Optional[str] = None
    is_active: bool = True
    metadata: dict = {}


class SkillCategoryCreate(SkillCategoryBase):
    pass


class SkillCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    parent_category_id: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[dict] = None


class SkillCategoryResponse(SkillCategoryBase):
    category_id: str
    level: int
    path: Optional[str] = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    category_id: str
    name: str
    slug: str
    description: str = ""
    level_min: int = 0
    level_max: int = 5
    aliases: list = []
    metadata: dict = {}
    is_deprecated: bool = False


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    category_id: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    level_min: Optional[int] = None
    level_max: Optional[int] = None
    aliases: Optional[list] = None
    metadata: Optional[dict] = None
    is_deprecated: Optional[bool] = None


class SkillResponse(SkillBase):
    skill_id: str
    skill_health: Optional[float] = None
    deprecated_at: Optional[int] = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillRelationshipBase(BaseModel):
    from_skill_id: str
    to_skill_id: str
    relationship_type: RelationshipType
    min_level_from: Optional[int] = None
    min_level_to: Optional[int] = None
    weight: float = 1.0
    is_directed: bool = True
    metadata: dict = {}


class SkillRelationshipCreate(SkillRelationshipBase):
    pass


class SkillRelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    min_level_from: Optional[int] = None
    min_level_to: Optional[int] = None
    weight: Optional[float] = None
    is_directed: Optional[bool] = None
    metadata: Optional[dict] = None


class SkillRelationshipResponse(SkillRelationshipBase):
    relationship_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str
    slug: str
    description: str = ""
    color: Optional[str] = None
    metadata: dict = {}


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[dict] = None


class TagResponse(TagBase):
    tag_id: str
    created_at: int

    class Config:
        from_attributes = True


class SkillTagCreate(BaseModel):
    skill_id: str
    tag_id: str


class SkillExternalMappingBase(BaseModel):
    skill_id: str
    external_system: ExternalSystem
    external_id: str
    external_name: str
    mapping_type: MappingType = MappingType.exact
    confidence: float = 1.0
    metadata: dict = {}


class SkillExternalMappingCreate(SkillExternalMappingBase):
    pass


class SkillExternalMappingUpdate(BaseModel):
    external_name: Optional[str] = None
    mapping_type: Optional[MappingType] = None
    confidence: Optional[float] = None
    metadata: Optional[dict] = None


class SkillExternalMappingResponse(SkillExternalMappingBase):
    mapping_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillRoadmapDefinitionBase(BaseModel):
    name: str
    description: str = ""
    target_skill_id: Optional[str] = None
    difficulty: Difficulty = Difficulty.intermediate
    estimated_duration: Optional[str] = None
    is_ai_generated: bool = False
    metadata: dict = {}


class SkillRoadmapDefinitionCreate(SkillRoadmapDefinitionBase):
    pass


class SkillRoadmapDefinitionResponse(SkillRoadmapDefinitionBase):
    roadmap_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


# === User Skills Models ===


class UserSkillBase(BaseModel):
    user_id: str
    skill_id: str
    level: int = 0
    state: UserSkillState = UserSkillState.learning
    metadata: dict = {}


class UserSkillCreate(UserSkillBase):
    pass


class UserSkillUpdate(BaseModel):
    level: Optional[int] = None
    state: Optional[UserSkillState] = None
    metadata: Optional[dict] = None


class UserSkillResponse(BaseModel):
    user_skill_id: str
    user_id: str
    skill_id: str
    level: int
    state: UserSkillState
    confidence_score: float
    evidence_score: float
    level_change_90d: float
    is_emerging: bool
    is_stale: bool
    last_activity_at: Optional[int] = None
    metadata: dict
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class UserSkillEvidenceBase(BaseModel):
    user_skill_id: str
    user_id: str
    source_type: EvidenceSourceType
    title: str
    description: str = ""
    url: Optional[str] = None
    signed_hash: str
    previous_hash: Optional[str] = None
    metadata: dict = {}
    collected_at: int


class UserSkillEvidenceCreate(UserSkillEvidenceBase):
    pass


class UserSkillEvidenceResponse(UserSkillEvidenceBase):
    evidence_id: str
    state: EvidenceState
    quality_score: float
    trust_score: float
    weight: float
    verified_at: Optional[int] = None
    expires_at: Optional[int] = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class UserSkillTargetBase(BaseModel):
    user_skill_id: str
    user_id: str
    target_level: int
    current_level: int = 0
    priority: TargetPriority = TargetPriority.medium
    target_date: Optional[str] = None
    status: TargetStatus = TargetStatus.active
    metadata: dict = {}


class UserSkillTargetCreate(UserSkillTargetBase):
    pass


class UserSkillTargetUpdate(BaseModel):
    target_level: Optional[int] = None
    current_level: Optional[int] = None
    priority: Optional[TargetPriority] = None
    target_date: Optional[str] = None
    status: Optional[TargetStatus] = None
    metadata: Optional[dict] = None


class UserSkillTargetResponse(UserSkillTargetBase):
    target_id: str
    gap_size: int
    progress_pct: float
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class UserSkillAssessmentBase(BaseModel):
    user_skill_id: str
    user_id: str
    assessment_type: AssessmentType
    score: Optional[float] = None
    level_achieved: Optional[int] = None
    confidence: Optional[float] = None
    status: AssessmentStatus = AssessmentStatus.pending
    duration_seconds: Optional[int] = None
    result_data: dict = {}
    started_at: Optional[int] = None
    completed_at: Optional[int] = None


class UserSkillAssessmentCreate(UserSkillAssessmentBase):
    pass


class UserSkillAssessmentResponse(UserSkillAssessmentBase):
    assessment_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


# === Intelligence Models ===


class SkillMarketDataBase(BaseModel):
    skill_id: str
    demand_score: int
    growth_score: float
    salary_median: Optional[int] = None
    salary_p10: Optional[int] = None
    salary_p25: Optional[int] = None
    salary_p75: Optional[int] = None
    salary_p90: Optional[int] = None
    competition_score: Optional[int] = None
    future_relevance: Optional[float] = None
    job_postings_count: Optional[int] = None
    source_data: dict = {}
    data_freshness: DataFreshness = DataFreshness.current


class SkillMarketDataCreate(SkillMarketDataBase):
    pass


class SkillMarketDataResponse(SkillMarketDataBase):
    skill_health: Optional[float] = None
    updated_at: int

    class Config:
        from_attributes = True


class SkillIncomeDataBase(BaseModel):
    skill_id: str
    source: IncomeSource
    level: int
    p10: Optional[int] = None
    p25: Optional[int] = None
    p50: Optional[int] = None
    p75: Optional[int] = None
    p90: Optional[int] = None
    currency: str = "USD"
    location: Optional[str] = None
    source_data: dict = {}


class SkillIncomeDataCreate(SkillIncomeDataBase):
    pass


class SkillIncomeDataResponse(SkillIncomeDataBase):
    income_id: str
    updated_at: int

    class Config:
        from_attributes = True


class SkillCertificationBase(BaseModel):
    skill_id: str
    category_id: Optional[str] = None
    name: str
    provider: str
    level_mapped: int
    quality_weight: float = 0.5
    is_verified: bool = False
    verification_url: Optional[str] = None
    expiration_months: Optional[int] = None
    metadata: dict = {}


class SkillCertificationCreate(SkillCertificationBase):
    pass


class SkillCertificationResponse(SkillCertificationBase):
    certification_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillProjectLinkBase(BaseModel):
    project_id: str
    skill_id: str
    min_level: int = 1
    weight: float = 1.0


class SkillProjectLinkCreate(SkillProjectLinkBase):
    pass


class SkillRoadmapLinkBase(BaseModel):
    roadmap_id: str
    skill_id: str
    phase: str
    sort_order: int = 0
    target_level: int
    estimated_hours: Optional[int] = None


class SkillRoadmapLinkCreate(SkillRoadmapLinkBase):
    pass


class SkillOpportunityLinkBase(BaseModel):
    opportunity_id: str
    skill_id: str
    min_level: int = 1
    weight: float = 1.0
    is_required: bool = True


class SkillOpportunityLinkCreate(SkillOpportunityLinkBase):
    pass


# === Supporting Models ===


class SkillTopicBase(BaseModel):
    skill_id: str
    name: str
    description: str = ""
    parent_topic_id: Optional[str] = None
    sort_order: int = 0
    metadata: dict = {}


class SkillTopicCreate(SkillTopicBase):
    pass


class SkillTopicResponse(SkillTopicBase):
    topic_id: str
    created_at: int

    class Config:
        from_attributes = True


class SkillResourceBase(BaseModel):
    skill_id: str
    title: str
    resource_type: ResourceType
    url: Optional[str] = None
    provider: Optional[str] = None
    difficulty: Difficulty = Difficulty.intermediate
    estimated_hours: Optional[float] = None
    quality_rating: Optional[float] = None
    is_free: bool = False
    metadata: dict = {}


class SkillResourceCreate(SkillResourceBase):
    pass


class SkillResourceResponse(SkillResourceBase):
    resource_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillLearningPathBase(BaseModel):
    target_skill_id: str
    name: str
    description: str = ""
    estimated_duration: Optional[str] = None
    difficulty: Difficulty = Difficulty.intermediate
    steps: list = []
    is_ai_generated: bool = False
    metadata: dict = {}


class SkillLearningPathCreate(SkillLearningPathBase):
    pass


class SkillLearningPathResponse(SkillLearningPathBase):
    path_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillAIRecommendationBase(BaseModel):
    user_id: str
    recommendation_type: RecommendationType
    skill_id: str
    reasoning: str
    priority: int = 0
    source: str = "ai"
    metadata: dict = {}
    expires_at: Optional[int] = None


class SkillAIRecommendationCreate(SkillAIRecommendationBase):
    pass


class SkillAIRecommendationUpdate(BaseModel):
    accepted: Optional[bool] = None
    metadata: Optional[dict] = None


class SkillAIRecommendationResponse(SkillAIRecommendationBase):
    recommendation_id: str
    accepted: Optional[bool] = None
    created_at: int

    class Config:
        from_attributes = True


class SkillActivityLogBase(BaseModel):
    user_id: str
    activity_type: ActivityType
    skill_id: Optional[str] = None
    metadata: dict = {}


class SkillActivityLogCreate(SkillActivityLogBase):
    pass


class SkillActivityLogResponse(SkillActivityLogBase):
    activity_id: str
    created_at: int

    class Config:
        from_attributes = True


# === Audit & Analytics Models ===


class SkillEventBase(BaseModel):
    event_type: str
    event_version: str = "1.0"
    aggregate_type: str
    aggregate_id: str
    user_id: Optional[str] = None
    data: dict
    metadata: dict = {}
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


class SkillEventCreate(SkillEventBase):
    pass


class SkillEventResponse(SkillEventBase):
    event_id: str
    created_at: int

    class Config:
        from_attributes = True


class AuditAction(str, Enum):
    insert = "INSERT"
    update = "UPDATE"
    delete = "DELETE"
    soft_delete = "SOFT_DELETE"
    restore = "RESTORE"


class EventOutboxStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    delivered = "delivered"
    failed = "failed"
    dead_letter = "dead_letter"


class WebhookStatus(str, Enum):
    pending = "pending"
    delivering = "delivering"
    delivered = "delivered"
    failed = "failed"
    dead_letter = "dead_letter"


class SubscriptionStatus(str, Enum):
    active = "active"
    paused = "paused"
    disabled = "disabled"


class ForecastMetric(str, Enum):
    demand = "demand"
    growth = "growth"
    salary = "salary"
    competition = "competition"
    future_relevance = "future_relevance"
    skill_health = "skill_health"
    avg_skill_level = "avg_skill_level"
    skill_count = "skill_count"
    readiness_score = "readiness_score"
    learning_velocity = "learning_velocity"
    income_potential = "income_potential"
    emerging_coverage = "emerging_coverage"


class ForecastScope(str, Enum):
    individual = "individual"
    organization = "organization"
    global_ = "global"


class ForecastModel(str, Enum):
    linear = "linear"
    holt_winters = "holt_winters"
    arima = "arima"
    bass_diffusion = "bass_diffusion"
    ensemble = "ensemble"


class SkillForecastBase(BaseModel):
    skill_id: str
    metric: ForecastMetric
    forecast_date: str
    predicted_value: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    model_version: str = "1.0"
    metadata: dict = {}


class SkillForecastCreate(SkillForecastBase):
    pass


class SkillForecastResponse(SkillForecastBase):
    forecast_id: str
    created_at: int

    class Config:
        from_attributes = True


# === Audit & Event Infrastructure Models ===


class SkillAuditLogCreate(BaseModel):
    table_name: str
    record_id: str
    user_id: Optional[str] = None
    action: AuditAction
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    changed_fields: Optional[list[str]] = None
    change_reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None


class SkillAuditLogResponse(SkillAuditLogCreate):
    audit_id: str
    created_at: int

    class Config:
        from_attributes = True


class SkillEventSubscriptionCreate(BaseModel):
    name: str
    url: str
    event_types: list[str] = []
    headers: dict = {}
    is_active: bool = True
    retry_policy: dict = {"max_retries": 5, "backoff": "exponential", "initial_delay_ms": 1000}


class SkillEventSubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    event_types: Optional[list[str]] = None
    headers: Optional[dict] = None
    is_active: Optional[bool] = None
    retry_policy: Optional[dict] = None


class SkillEventSubscriptionResponse(SkillEventSubscriptionCreate):
    subscription_id: str
    last_delivered_at: Optional[int] = None
    last_error_at: Optional[int] = None
    delivery_count: int = 0
    failure_count: int = 0
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class SkillEventOutboxCreate(BaseModel):
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: dict
    headers: dict = {}


class SkillEventOutboxResponse(SkillEventOutboxCreate):
    outbox_id: str
    status: EventOutboxStatus
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    scheduled_at: Optional[int] = None
    processed_at: Optional[int] = None
    created_at: int

    class Config:
        from_attributes = True


class SkillWebhookQueueResponse(BaseModel):
    webhook_id: str
    subscription_id: str
    event_type: str
    payload: dict
    url: str
    headers: dict = {}
    status: WebhookStatus
    retry_count: int = 0
    max_retries: int = 5
    last_error: Optional[str] = None
    last_http_status: Optional[int] = None
    scheduled_at: Optional[int] = None
    delivered_at: Optional[int] = None
    created_at: int

    class Config:
        from_attributes = True


# === Analytics Snapshot Models ===


class SkillAnalyticsSnapshotCreate(BaseModel):
    user_id: str
    snapshot_date: str
    avg_skill_level: Optional[float] = None
    skill_count: Optional[int] = None
    readiness_score: Optional[float] = None
    learning_velocity: Optional[float] = None
    diversification_score: Optional[float] = None
    income_per_hour: Optional[float] = None
    market_alignment: Optional[float] = None
    emerging_coverage: Optional[int] = None
    milestone_completion: Optional[float] = None
    evidence_ratio: Optional[float] = None
    metadata: dict = {}


class SkillAnalyticsSnapshotResponse(SkillAnalyticsSnapshotCreate):
    snapshot_id: str
    created_at: int

    class Config:
        from_attributes = True


# === History Models ===


class SkillTaxonomyHistoryCreate(BaseModel):
    entity_type: str
    entity_id: str
    version: int
    previous_state: dict
    new_state: dict
    change_type: str
    changed_by: Optional[str] = None
    change_reason: Optional[str] = None


class SkillTaxonomyHistoryResponse(SkillTaxonomyHistoryCreate):
    history_id: str
    created_at: int

    class Config:
        from_attributes = True


class SkillUserSkillHistoryCreate(BaseModel):
    user_id: str
    skill_id: str
    version: int
    proficiency_before: Optional[int] = None
    proficiency_after: Optional[int] = None
    hours_since_last: Optional[float] = None
    change_type: str
    changed_by: Optional[str] = None


class SkillUserSkillHistoryResponse(SkillUserSkillHistoryCreate):
    history_id: str
    created_at: int

    class Config:
        from_attributes = True


class SkillMarketHistoryCreate(BaseModel):
    skill_id: str
    demand_score: Optional[int] = None
    growth_score: Optional[float] = None
    salary_median: Optional[int] = None
    competition_score: Optional[int] = None
    future_relevance: Optional[float] = None
    skill_health: Optional[float] = None
    snapshot_source: str = "automated"


class SkillMarketHistoryResponse(SkillMarketHistoryCreate):
    market_history_id: str
    created_at: int

    class Config:
        from_attributes = True
