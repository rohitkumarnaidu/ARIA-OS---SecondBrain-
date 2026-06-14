from pydantic import BaseModel
from typing import Optional


class OpportunityBase(BaseModel):
    title: str
    url: str
    opportunity_type: str = "internship"
    company: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[list] = []
    deadline: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    opportunity_type: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[list] = None
    deadline: Optional[str] = None
    status: Optional[str] = None


class OpportunityResponse(OpportunityBase):
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
