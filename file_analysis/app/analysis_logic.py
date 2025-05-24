import uuid
from typing import Dict, Any, Optional, List
from .similarity import normalize, tokenize, sha256_bytes, simhash_from_tokens, hamming
from .settings import settings
from .db import SessionLocal, AnalysisRecord
from sqlalchemy import select
from httpx import AsyncClient


async def fetch_file_text(file_id: uuid.UUID) -> bytes:
    url = f"{settings.file_store_base_url}/files/{file_id}"
    async with AsyncClient() as ac:
        resp = await ac.get(url)
        resp.raise_for_status()
        return resp.content


def compute_stats(text: str) -> Dict[str, Any]:
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    words = len(tokenize(text))
    symbols = len(text)
    return {"paragraphs": paragraphs, "words": words, "symbols": symbols}


async def analyse(file_id: uuid.UUID, filename: str) -> AnalysisRecord:
    raw_bytes = await fetch_file_text(file_id)
    sha = sha256_bytes(raw_bytes)
    text = raw_bytes.decode("utf-8", errors="replace")
    norm = normalize(text)
    tokens = tokenize(norm)
    sh_val = simhash_from_tokens(tokens)
    stats = compute_stats(norm)

    async with SessionLocal() as session:
        existing_sha = await session.execute(
            select(AnalysisRecord).where(AnalysisRecord.sha256 == sha)
        )
        if row := existing_sha.scalars().first():
            return row

        candidates_rs = await session.execute(select(AnalysisRecord))
        duplicate_of: Optional[uuid.UUID] = None
        for cand in candidates_rs.scalars():
            if hamming(sh_val, int(cand.simhash, 16)) <= settings.near_threshold:
                duplicate_of = cand.file_id
                break

        rec = AnalysisRecord(
            file_id=file_id,
            filename=filename,
            sha256=sha,
            simhash=f"{sh_val:016x}",
            stats=stats,
            duplicate_of=duplicate_of,
        )
        session.add(rec)
        await session.commit()
        await session.refresh(rec)
        return rec
