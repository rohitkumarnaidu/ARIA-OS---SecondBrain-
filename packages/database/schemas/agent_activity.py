from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentActivityLogCreate(BaseModel):
    agent_name: str
    status: str = Field(..., pattern=r"^(running|completed|failed)$")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None


class AgentActivityLogResponse(BaseModel):
    id: str
    user_id: str
    agent_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    created_at: str


class AgentActivityFeedResponse(BaseModel):
    data: list[AgentActivityLogResponse]
    total: int
    limit: int
    offset: int