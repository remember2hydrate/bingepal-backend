from fastapi import Request
from app.utils.logger import logger

async def log_request(request: Request):
    path = request.url.path
    query = str(request.url.query)
    method = request.method
    ip = request.client.host
    logger.info(f"[Request] {method} {path}?{query} from {ip}")
