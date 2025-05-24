from fastapi import FastAPI, Request, HTTPException
from starlette.responses import StreamingResponse
import httpx

from config.base import get_settings
from config.gateway import GatewaySettings

settings: GatewaySettings = get_settings(GatewaySettings)
app = FastAPI(title="API-Gateway", version="1.0.1")


async def proxy(req: Request, upstream: str, tail: str) -> StreamingResponse:
    url = f"{upstream}{tail}"
    headers = {k: v for k, v in req.headers.items() if k.lower() != "host"}
    body = await req.body()

    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as cli:
        try:
            resp = await cli.request(
                req.method, url,
                params=req.query_params,
                headers=headers,
                content=body,
            )
        except httpx.RequestError as exc:
            raise HTTPException(503, f"Upstream {upstream} unreachable: {exc}")

    return StreamingResponse(
        resp.aiter_raw(),
        status_code=resp.status_code,
        headers=resp.headers,
        media_type=resp.headers.get("content-type"),
    )


@app.get("/healthz", include_in_schema=False)
def health(): return {"ok": True}


@app.api_route("/files", methods=["POST"])
async def upload_file(req: Request):
    return await proxy(req, settings.filestore_base_url, "/files")


@app.api_route("/files/{rest:path}",
               methods=["GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def files_passthrough(rest: str, req: Request):
    return await proxy(req, settings.filestore_base_url, f"/files/{rest}")


@app.api_route("/analysis/{rest:path}",
               methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def analysis_passthrough(rest: str, req: Request):
    tail = f"/analysis/{rest}" if rest else "/analysis"
    return await proxy(req, settings.analysis_base_url, tail)
