from datetime import datetime

from pydantic import BaseModel
from typing import Any, Dict, Optional, List


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


class ChatMessageRecord(BaseModel):
    """A persisted chat_messages row as returned by the transcript endpoint.

    `conversation_id` is nullable because the column is not NOT NULL in the
    schema; rows written before conversation tracking existed have NULL there.
    """

    id: str
    user_id: str
    conversation_id: Optional[str] = None
    role: str
    content: str
    action_taken: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatTranscriptResponse(BaseModel):
    """Paginated, user-scoped transcript for a single conversation."""

    conversation_id: str
    messages: List[ChatMessageRecord]
    total: int
    limit: int
    offset: int
