from pydantic import BaseModel
from typing import Optional, Any


class ExportRequest(BaseModel):
    tables: Optional[list[str]] = None


class ExportResponse(BaseModel):
    user_id: str
    exported_at: str
    data: dict[str, list[dict[str, Any]]]
    table_count: int
    record_count: int
