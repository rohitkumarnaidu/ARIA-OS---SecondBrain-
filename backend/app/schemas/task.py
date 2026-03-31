from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Category(str, Enum):
    study = "study"
    project = "project"
    habit = "habit"
    personal = "personal"
    income = "income"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    category: Category = Category.personal
    estimated_minutes: Optional[int] = None
    due_date: Optional[datetime] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    dependency_id: Optional[str] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    status: Optional[TaskStatus] = None
    estimated_minutes: Optional[int] = None
    due_date: Optional[datetime] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    dependency_id: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None


class TaskResponse(TaskBase):
    id: str
    user_id: str
    status: TaskStatus
    completed_at: Optional[datetime]
    missed_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
