import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.db_query")


def db_query(query: str) -> dict:
    logger.info("db_query called: query=%s", query[:80])
    return {
        "tool": "db_query",
        "query": query,
        "rows": [
            {"user_id": 1001, "email": "alice@example.com", "plan": "enterprise", "revenue": 4200},
            {"user_id": 1002, "email": "bob@example.com", "plan": "pro", "revenue": 299},
            {"user_id": 1003, "email": "carol@example.com", "plan": "enterprise", "revenue": 8500},
        ],
        "row_count": 3,
        "timestamp": datetime.utcnow().isoformat(),
    }
