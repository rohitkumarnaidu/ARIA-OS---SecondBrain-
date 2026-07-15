"""Pydantic models for the ToolCalling System."""

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolDefinitionSchema(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    handler: str
    required_permissions: list[str] = Field(default_factory=list)
    timeout: float = 30
    audit: bool = True


class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    user_id: str
    request_id: Optional[str] = None


class ToolCallResponse(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = 0
    tool_name: str
    request_id: str


class ToolExecutionLog(BaseModel):
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    user_id: str
    request_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    success: bool = False
    error: Optional[str] = None


class ToolAuditEntry(BaseModel):
    action: str = "tool_execute"
    resource: str = "tool"
    resource_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
