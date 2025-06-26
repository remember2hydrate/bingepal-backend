from fastapi import Request
from app.utils.logger import logger

def anonymize_ip(ip: str) -> str:
    parts = ip.split(".")
    return ".".join(parts[:2]) + ".*.*" if len(parts) == 4 else ip

async def log_request(request: Request):
    path = request.url.path
    query = str(request.url.query)
    method = request.method
    raw_ip = request.client.host
    ip = anonymize_ip(raw_ip)

    user_agent = request.headers.get("user-agent", "Unknown")
    if "Android" in user_agent:
        platform = "Android"
    elif "iPhone" in user_agent:
        platform = "iOS"
    elif "Windows" in user_agent:
        platform = "Windows"
    elif "Mac" in user_agent:
        platform = "macOS"
    elif "Linux" in user_agent:
        platform = "Linux"
    else:
        platform = "Unknown"

    if user_agent == "Unknown":
        logger.info(f"[Request] {method} {path}?{query} from {ip}")
    else:
        logger.info(f"[Request] {method} {path}?{query} from {ip} using {platform}")
