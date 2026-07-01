import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.code_review")

SAMPLE_CODE = '''def process_payment(user_id, amount):
    """Process payment for a user."""
    conn = get_db_connection()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # potential SQL injection
    result = conn.execute(query)
    if result:
        charge(result["card_token"], amount)
        return {"status": "success"}
    return {"status": "error"}
'''


def code_review(file_path: str) -> dict:
    logger.info("code_review called: file_path=%s", file_path)
    return {
        "tool": "code_review",
        "file_path": file_path,
        "content": SAMPLE_CODE,
        "language": "python",
        "lines": 12,
        "timestamp": datetime.utcnow().isoformat(),
    }
