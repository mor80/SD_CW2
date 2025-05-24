from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    file_id: UUID
    filename: str
    size: int
    mime: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
