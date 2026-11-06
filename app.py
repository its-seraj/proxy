from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PROXY_API_KEY")

# ALLOWED_DOMAINS = [
#     "https://api.choiceindia.com",
#     "https://openapi.choiceindia.com"
# ]

app = FastAPI()


class ProxyRequest(BaseModel):
    method: str
    url: str
    headers: dict = {}
    body: Optional[dict] = None


@app.post("/")
def proxy(
    req: ProxyRequest,
    x_api_key: str = Header(default="")
):

    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API Key")

    # if not any(req.url.startswith(d) for d in ALLOWED_DOMAINS):
    #     raise HTTPException(403, "URL not allowed")

    try:

        response = requests.request(
            method=req.method.upper(),
            url=req.url,
            headers=req.headers,
            json=req.body,
        )

        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": response.json()
            if "application/json" in response.headers.get("content-type", "")
            else response.text
        }

    except Exception as e:
        raise HTTPException(500, str(e))


STREAM_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Range, x-api-key",
    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
    "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges, Content-Disposition",
}


def _forwarded_response_headers(upstream_headers):
    headers = dict(STREAM_CORS_HEADERS)
    headers["Accept-Ranges"] = upstream_headers.get("Accept-Ranges", "none")
    for h in ("Content-Range", "Content-Length", "Content-Type", "Content-Disposition"):
        if h in upstream_headers:
            headers[h] = upstream_headers[h]
    return headers


@app.options("/stream")
def stream_options():
    return Response(headers=STREAM_CORS_HEADERS)


@app.head("/stream")
def stream_head(url: str, request: Request, x_api_key: str = Header(default="")):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API Key")

    range_header = request.headers.get("range")
    fwd_headers = {"Range": range_header} if range_header else {}

    try:
        upstream = requests.head(url, headers=fwd_headers, allow_redirects=True)
    except Exception as e:
        raise HTTPException(500, str(e))

    return Response(
        status_code=upstream.status_code,
        headers=_forwarded_response_headers(upstream.headers),
    )


@app.get("/stream")
def stream(url: str, request: Request, x_api_key: str = Header(default="")):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API Key")

    range_header = request.headers.get("range")
    fwd_headers = {"Range": range_header} if range_header else {}

    try:
        upstream = requests.get(url, headers=fwd_headers, stream=True)
    except Exception as e:
        raise HTTPException(500, str(e))

    return StreamingResponse(
        upstream.iter_content(chunk_size=65536),
        status_code=upstream.status_code,
        headers=_forwarded_response_headers(upstream.headers),
    )