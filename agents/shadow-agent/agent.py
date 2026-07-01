import logging
import os
import time

import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [shadow-agent] %(levelname)s: %(message)s")
logger = logging.getLogger("shadow-agent")

CYCLE_SECONDS = 60
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TASKS = [
    "Draft a 2-sentence status update email for the engineering team about last week's deployment.",
    "Summarize the key risks of deploying AI agents without governance controls in 3 bullet points.",
    "Write a brief incident report template for a production outage.",
    "List 3 metrics an enterprise should track for AI agent governance.",
]


def run_task(task: str) -> str:
    logger.info("Running unsanctioned task: %s", task[:60])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": task}]
    )
    result = message.content[0].text
    logger.info("Task complete: %s", result[:100])
    return result


if __name__ == "__main__":
    logger.info("Shadow agent starting (AT0, no labels, no governance, always RED)")
    logger.info("This agent has no nhi-dex labels and will be flagged as Shadow AI")

    cycle = 0
    while True:
        try:
            task = TASKS[cycle % len(TASKS)]
            run_task(task)
        except Exception as e:
            logger.error("Cycle error: %s", e)
        cycle += 1
        time.sleep(CYCLE_SECONDS)
