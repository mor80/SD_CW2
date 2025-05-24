import pytest
from httpx import AsyncClient
from pathlib import Path
from importlib import reload

from file_store.app.main import app
from file_store.app import settings as settings_module

TEST_TXT = "hello\nworld\n"


@pytest.mark.asyncio
async def test_upload_download(tmp_path, monkeypatch):
    monkeypatch.setenv("FILESTORE_STORAGE_DIR", str(tmp_path))
    reload(settings_module)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/files",
            files={"file": ("hello.txt", TEST_TXT, "text/plain")},
        )
        assert resp.status_code == 201
        file_id = resp.json()["file_id"]

        out = await ac.get(f"/files/{file_id}")
        assert out.text == TEST_TXT
