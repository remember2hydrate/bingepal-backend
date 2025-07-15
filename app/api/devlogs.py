from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from hashlib import sha256
import os

from app.utils.logger import get_recent_logs

router = APIRouter()

@router.get("/dev-logs", response_class=PlainTextResponse)
async def get_dev_logs(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing Authorization token")

    #token_hash = sha256(token.encode()).hexdigest()
    if token != os.getenv("STORED_HASH"):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        logs = get_recent_logs()
        return "\n".join(logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve logs")
