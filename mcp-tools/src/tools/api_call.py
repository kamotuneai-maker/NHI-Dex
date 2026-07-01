import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.api_call")


def api_call(url: str, method: str = "GET", payload: dict = None) -> dict:
    logger.info("api_call called: method=%s url=%s", method, url)
    return {
        "tool": "api_call",
        "url": url,
        "method": method,
        "status_code": 200,
        "response": {"success": True, "data": {"id": "ext-001", "status": "processed"}},
        "timestamp": datetime.utcnow().isoformat(),
    }
