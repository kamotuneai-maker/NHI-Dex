import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.file_read")


def file_read(path: str) -> dict:
    logger.info("file_read called: path=%s", path)
    return {
        "tool": "file_read",
        "path": path,
        "content": (
            "date,metric,value\n"
            "2026-06-01,active_users,12400\n"
            "2026-06-02,active_users,13100\n"
            "2026-06-03,active_users,12800\n"
            "2026-06-04,active_users,14200\n"
            "2026-06-05,active_users,15600\n"
        ),
        "size_bytes": 148,
        "timestamp": datetime.utcnow().isoformat(),
    }
