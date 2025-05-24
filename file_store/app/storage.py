import uuid
from pathlib import Path
import hashlib
from fastapi import UploadFile

from .settings import settings


def _path_for(fid: uuid.UUID) -> Path:
    """Return filesystem path for given file id."""
    return settings.storage_dir / f"{fid}.bin"


async def save_file(f: UploadFile) -> tuple[uuid.UUID, int, str]:
    """Write uploaded file to disk, return (uuid, size, sha256)."""
    fid = uuid.uuid4()
    path = _path_for(fid)
    path.parent.mkdir(parents=True, exist_ok=True)

    hasher = hashlib.sha256()
    size = 0
    async with path.open("wb") as out:
        while chunk := await f.read(8192):
            hasher.update(chunk)
            size += len(chunk)
            await out.write(chunk)

    return fid, size, hasher.hexdigest()


async def load_file(fid: uuid.UUID) -> bytes:
    """Read file bytes by id."""
    return _path_for(fid).read_bytes()


def file_exists(fid: uuid.UUID) -> bool:
    """Check if file is stored."""
    return _path_for(fid).exists()
