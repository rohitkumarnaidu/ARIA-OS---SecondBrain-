from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatMessage(BaseModel):
    id: str
    user_id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None


class ChatSessionResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    ai_response: str
