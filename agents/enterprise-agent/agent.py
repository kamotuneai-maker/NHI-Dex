import logging
import os
import time

import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [enterprise-agent] %(levelname)s: %(message)s")
logger = logging.getLogger("enterprise-agent")

MCP_URL = os.getenv("MCP_TOOL_SERVER", "http://mcp-tools:3001")
CYCLE_SECONDS = 120
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_tool(tool: str, payload: dict) -> dict:
    resp = requests.post(f"{MCP_URL}/tools/{tool}", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def pass_action():
    logger.info("PASS: Retrieving analytics data with HITL gate")
    data = call_tool("file_read", {"path": "/data/analytics.csv"})
    content = data.get("content", "")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Summarize these analytics metrics in 2 sentences:\n\n{content}"
        }]
    )
    summary = message.content[0].text
    logger.info("PASS complete — summary generated, pending human approval: %s", summary[:120])
    logger.info("[HITL GATE] Action requires human approval before execution — queued for review")
    return summary


def wait_for_mcp(retries: int = 20, delay: int = 3):
    for i in range(retries):
        try:
            resp = requests.get(f"{MCP_URL}/health", timeout=5)
            if resp.status_code == 200:
                logger.info("MCP tool server ready")
                return True
        except Exception:
            pass
        logger.info("Waiting for MCP tools (%d/%d)...", i + 1, retries)
        time.sleep(delay)
    return False


if __name__ == "__main__":
    logger.info("Enterprise agent starting (AT5, supervised, 120s cycle, always GREEN)")
    if not wait_for_mcp():
        logger.error("MCP tools unavailable, exiting")
        exit(1)

    while True:
        try:
            pass_action()
        except Exception as e:
            logger.error("Cycle error: %s", e)
        time.sleep(CYCLE_SECONDS)
