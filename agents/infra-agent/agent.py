import logging
import os
import time

import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [infra-agent] %(levelname)s: %(message)s")
logger = logging.getLogger("infra-agent")

MCP_URL = os.getenv("MCP_TOOL_SERVER", "http://mcp-tools:3001")
CYCLE_SECONDS = 120
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_tool(tool: str, payload: dict) -> dict:
    resp = requests.post(f"{MCP_URL}/tools/{tool}", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def pass_action():
    region = os.getenv("AWS_REGION", "us-east-1")
    logger.info("PASS: Checking cloud status for region %s", region)
    status = call_tool("cloud_status", {"region": region})

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Generate a 2-sentence infrastructure health summary from this status data: {status}"
        }]
    )
    summary = message.content[0].text
    logger.info("PASS complete — health report: %s", summary[:120])
    return summary


def fail_action():
    logger.warning("FAIL: Attempting cross-env access + external email")
    status = call_tool("cloud_status", {"region": "us-east-1"})

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": f"Write a 1-sentence alert email about: {status.get('alerts', 0)} alerts in prod"
        }]
    )
    email_body = message.content[0].text

    logger.warning("FAIL: Calling email_send outside cloud-status-readonly scope")
    email_result = call_tool("email_send", {
        "to": "oncall@ops-team.com",
        "subject": "[PROD ALERT] Infrastructure anomaly detected",
        "body": email_body,
    })
    logger.warning("FAIL complete — email sent outside scope: %s", email_result.get("message_id"))
    return email_result


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
    logger.info("Infra agent starting (AT6, fully autonomous, 120s cycle)")
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
