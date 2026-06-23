from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
