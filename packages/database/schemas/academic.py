from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[str] = None
    exam_date: Optional[str] = None
    target_marks: Optional[float] = None


class SubjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    code: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[str] = None
    exam_date: Optional[str] = None
    target_marks: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MarkCreate(BaseModel):
    subject_id: str
    exam_type: str
    marks_obtained: float
    max_marks: float
    date: str


class MarkResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    exam_type: str
    marks_obtained: float
    max_marks: float
    date: str
    created_at: datetime

    class Config:
        from_attributes = True
