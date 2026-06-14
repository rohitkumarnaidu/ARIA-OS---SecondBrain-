from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "active"
    progress: int = 0
    deadline: Optional[str] = None
    tech_stack: Optional[list] = []
    repo_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    deadline: Optional[str] = None
    tech_stack: Optional[list] = None
    repo_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
