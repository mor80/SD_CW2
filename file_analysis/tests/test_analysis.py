import pytest
from httpx import AsyncClient
from uuid import uuid4
from file_analysis.app.main import app


@pytest.mark.asyncio
async def test_run_analysis(monkeypatch, aiohttp_unused_port):
    # Dummy monkeypatch fetch_file_text to avoid file-store call
    from file_analysis.app import analysis_logic

    async def dummy_fetch(file_id):
        return b"hello world\n\nhello again"

    monkeypatch.setattr(analysis_logic, "fetch_file_text", dummy_fetch)

    fid = uuid4()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(f"/analysis/{fid}", params={"filename": "dummy.txt"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["stats"]["words"] == 4
