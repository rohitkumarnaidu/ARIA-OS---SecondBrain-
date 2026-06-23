from pydantic import BaseModel
from typing import Optional


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    category: str
    priority: str
    read: bool
    action_url: Optional[str] = None
    icon: Optional[str] = None
    created_at: str


class NotificationRead(BaseModel):
    id: str
