from typing import Optional
from fastapi import FastAPI, HTTPException, Header
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