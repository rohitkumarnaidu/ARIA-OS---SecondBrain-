from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    year: Optional[int] = None
    skills: Optional[list] = []
    bio: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    year: Optional[int] = None
    skills: Optional[list] = None
    bio: Optional[str] = None
    daily_routine: Optional[dict] = None
    opportunity_preferences: Optional[dict] = None


class UserResponse(UserBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
