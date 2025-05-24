from fastapi import FastAPI, UploadFile, HTTPException, status, Depends
from fastapi.responses import Response
from uuid import UUID

from .schemas import FileMeta
from .storage import save_file, load_file, file_exists
from .db import SessionLocal, FileRecord, Base, engine

app = FastAPI(title="File‑Store Service", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/files", response_model=FileMeta, status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile, db=Depends(get_db)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=415, detail="Only text/plain accepted")

    fid, size, sha256 = await save_file(file)

    meta = FileRecord(
        file_id=fid,
        filename=file.filename,
        mime=file.content_type,
        size=size,
        sha256=sha256,
    )
    db.add(meta)
    await db.commit()

    return FileMeta(
        file_id=fid,
        filename=file.filename,
        size=size,
        mime=file.content_type,
    )


@app.get("/files/{fid}")
async def download(fid: UUID):
    if not file_exists(fid):
        raise HTTPException(status_code=404, detail="Not found")

    data = await load_file(fid)
    return Response(content=data, media_type="text/plain")


@app.head("/files/{fid}")
async def head(fid: UUID, db=Depends(get_db)):
    rec = await db.get(FileRecord, fid)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")

    headers = {
        "Content-Length": str(rec.size),
        "Content-Type": rec.mime,
        "X-Uploaded-At": rec.uploaded_at.isoformat(),
    }
    return Response(status_code=200, headers=headers)
