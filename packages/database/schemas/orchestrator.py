from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class PlanRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class MemorySearchRequest(BaseModel):
    query: str


class PatternRequest(BaseModel):
    query: str


class MatchRequest(BaseModel):
    query: str


class OrchestratorStep(BaseModel):
    action: str
    target: str
    reasoning: str
    confidence: float


class PlanResponse(BaseModel):
    plan_id: str
    steps: List[OrchestratorStep]
    summary: str


class MemorySearchResponse(BaseModel):
    memories: List[dict]
    preferences: dict
    summary: str


class PatternInsight(BaseModel):
    type: str
    description: str
    confidence: float
    data: dict


class PatternResponse(BaseModel):
    patterns: List[PatternInsight]
    summary: str


class OpportunityMatch(BaseModel):
    id: str
    title: str
    score: float
    reasoning: str


class MatchResponse(BaseModel):
    matches: List[OpportunityMatch]
    summary: str


class ExecuteResponse(BaseModel):
    action: str
    result: dict
    summary: str
