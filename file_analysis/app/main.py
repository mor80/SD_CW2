import uuid
from fastapi import FastAPI, HTTPException, status
from fastapi import Depends
from .db import Base, engine, SessionLocal, AnalysisRecord
from .schemas import AnalysisResult
from .analysis_logic import analyse
from uuid import UUID
from sqlalchemy import select

app = FastAPI(title="File‑Analysis Service", version="0.1.0")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/analysis/{file_id}", response_model=AnalysisResult, status_code=status.HTTP_201_CREATED)
async def run_analysis(file_id: UUID, filename: str):
    try:
        rec = await analyse(file_id, filename)
    except Exception as e:
        raise HTTPException(500, str(e)) from e
    return AnalysisResult(
        file_id=rec.file_id,
        filename=rec.filename,
        sha256=rec.sha256,
        stats=rec.stats,
        duplicate_of=rec.duplicate_of,
        uploaded_at=rec.uploaded_at,
    )


@app.get("/analysis/{file_id}", response_model=AnalysisResult)
async def get_analysis(file_id: UUID, db=Depends(get_db)):
    rs = await db.execute(select(AnalysisRecord).where(AnalysisRecord.file_id == file_id))
    rec = rs.scalars().first()
    if not rec:
        raise HTTPException(404, "Analysis not found")
    return AnalysisResult(
        file_id=rec.file_id,
        filename=rec.filename,
        sha256=rec.sha256,
        stats=rec.stats,
        duplicate_of=rec.duplicate_of,
        uploaded_at=rec.uploaded_at,
    )
