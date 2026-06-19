from pydantic import BaseModel
from typing import Optional


class NLPParseRequest(BaseModel):
    text: str
    context: Optional[dict] = None


class NLPParseResponse(BaseModel):
    type: str
    confidence: float
    task: Optional[dict] = None
    navigation: Optional[str] = None
    query: Optional[str] = None
    raw: str


class NLPExecuteRequest(BaseModel):
    type: str
    task: Optional[dict] = None
    navigation: Optional[str] = None


class NLPExecuteResponse(BaseModel):
    success: bool
    message: str
    redirect_url: Optional[str] = None
