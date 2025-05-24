import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .settings import settings

Base = declarative_base()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class FileRecord(Base):
    __tablename__ = "files"

    file_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    mime = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
