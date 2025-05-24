from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    file_id: UUID
    filename: str
    sha256: str
    stats: Dict[str, Any]
    duplicate_of: Optional[UUID] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
