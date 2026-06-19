from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    phase: str = "planning"
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    next_action: Optional[str] = None
    blocker: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    next_action: Optional[str] = None
    blocker: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
