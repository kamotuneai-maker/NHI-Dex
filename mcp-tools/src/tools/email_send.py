import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.email_send")


def email_send(to: str, subject: str, body: str) -> dict:
    logger.warning("email_send called (trifecta trigger — external communication): to=%s subject=%s", to, subject)
    return {
        "tool": "email_send",
        "to": to,
        "subject": subject,
        "status": "delivered",
        "message_id": f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
    }
