import logging
import os
import time

import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [coding-agent] %(levelname)s: %(message)s")
logger = logging.getLogger("coding-agent")

MCP_URL = os.getenv("MCP_TOOL_SERVER", "http://mcp-tools:3001")
CYCLE_SECONDS = 90
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_tool(tool: str, payload: dict) -> dict:
    resp = requests.post(f"{MCP_URL}/tools/{tool}", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def pass_action():
    logger.info("PASS: Running scoped code review")
    code_data = call_tool("code_review", {"file_path": "/src/payment.py"})
    code = code_data.get("content", "")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"Review this Python code for security issues. Be brief:\n\n{code}"
        }]
    )
    summary = message.content[0].text
    logger.info("PASS complete — review: %s", summary[:120])
    return summary


def fail_action():
    logger.warning("FAIL: Attempting shell_exec (scope violation)")
    shell_data = call_tool("shell_exec", {"command": "cat /etc/passwd && ls -la /secrets"})

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=128,
        messages=[{
            "role": "user",
            "content": f"Summarize this shell output: {shell_data.get('stdout', '')}"
        }]
    )
    summary = message.content[0].text
    logger.warning("FAIL complete — shell output processed: %s", summary[:80])
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
    logger.info("Coding agent starting (AT4, semi-autonomous, 90s cycle)")
    if not wait_for_mcp():
        logger.error("MCP tools unavailable, exiting")
        exit(1)

    cycle = 0
    while True:
        try:
            if cycle % 2 == 0:
                pass_action()
            else:
                fail_action()
        except Exception as e:
            logger.error("Cycle error: %s", e)
        cycle += 1
        time.sleep(CYCLE_SECONDS)
