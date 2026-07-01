import logging
import sys
import time

import docker
import requests

from .config import (
    DETECT_ENDPOINT,
    HEALTH_ENDPOINT,
    HEALTH_CHECK_ATTEMPTS,
    HEALTH_CHECK_INTERVAL,
    SCAN_INTERVAL,
)
from .scanner import extract_fingerprint, is_self_container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("nhi-dex.watcher")

tracked_containers: dict[str, dict] = {}


def wait_for_engine() -> bool:
    logger.info("Waiting for Classification Engine at %s", HEALTH_ENDPOINT)
    for attempt in range(1, HEALTH_CHECK_ATTEMPTS + 1):
        try:
            resp = requests.get(HEALTH_ENDPOINT, timeout=5)
            if resp.status_code == 200:
                logger.info("Engine is healthy (attempt %d/%d)", attempt, HEALTH_CHECK_ATTEMPTS)
                return True
        except requests.ConnectionError:
            pass
        logger.info("Engine not ready, retrying (%d/%d)...", attempt, HEALTH_CHECK_ATTEMPTS)
        time.sleep(HEALTH_CHECK_INTERVAL)
    logger.error("Engine did not become healthy after %d attempts", HEALTH_CHECK_ATTEMPTS)
    return False


def push_detection(fingerprint_data: dict) -> bool:
    try:
        resp = requests.post(DETECT_ENDPOINT, json=fingerprint_data, timeout=10)
        if resp.status_code in (200, 201):
            logger.info(
                "Detection accepted: %s (%s) — mode=%s confidence=%.2f",
                fingerprint_data["container_name"],
                fingerprint_data["image_name"],
                fingerprint_data["detection_mode"],
                fingerprint_data["overall_confidence"],
            )
            return True
        logger.warning("Engine returned %d for %s", resp.status_code, fingerprint_data["container_name"])
        return False
    except requests.RequestException as e:
        logger.error("Failed to push detection for %s: %s", fingerprint_data["container_name"], e)
        return False


def scan_container(container) -> None:
    if is_self_container(container):
        return

    try:
        container.reload()
    except Exception:
        return

    if container.status != "running":
        return

    fingerprint = extract_fingerprint(container)

    if fingerprint.overall_confidence < 0.3 and not fingerprint.has_api_key_env:
        logger.debug("Skipping %s — low confidence (%.2f)", fingerprint.container_name, fingerprint.overall_confidence)
        return

    fingerprint_data = fingerprint.to_dict()
    tracked_containers[fingerprint.container_id] = fingerprint_data
    push_detection(fingerprint_data)


def handle_container_remove(container_id: str, container_name: str) -> None:
    short_id = container_id[:12]
    if short_id in tracked_containers:
        del tracked_containers[short_id]
        logger.info("Container removed from tracking: %s (%s)", container_name, short_id)
        try:
            requests.post(
                DETECT_ENDPOINT,
                json={"container_id": short_id, "container_name": container_name, "event": "removed"},
                timeout=5,
            )
        except requests.RequestException:
            pass


def initial_scan(client: docker.DockerClient) -> None:
    logger.info("Starting initial scan of all running containers...")
    containers = client.containers.list()
    scanned = 0
    for container in containers:
        scan_container(container)
        scanned += 1
    logger.info("Initial scan complete: %d containers examined, %d tracked", scanned, len(tracked_containers))


def event_stream(client: docker.DockerClient) -> None:
    logger.info("Subscribing to Docker event stream...")
    for event in client.events(decode=True):
        event_type = event.get("Type")
        action = event.get("Action")
        actor = event.get("Actor", {})
        container_id = actor.get("ID", "")
        attributes = actor.get("Attributes", {})
        container_name = attributes.get("name", "unknown")

        if event_type != "container":
            continue

        if action == "start":
            logger.info("Container started: %s (%s)", container_name, container_id[:12])
            try:
                container = client.containers.get(container_id)
                scan_container(container)
            except docker.errors.NotFound:
                logger.warning("Container %s not found after start event", container_name)

        elif action in ("stop", "die", "destroy"):
            logger.info("Container %s: %s (%s)", action, container_name, container_id[:12])
            handle_container_remove(container_id, container_name)


def main() -> None:
    logger.info("=" * 60)
    logger.info("NHI-Dex Watcher starting...")
    logger.info("=" * 60)

    if not wait_for_engine():
        logger.error("Aborting — Classification Engine unavailable")
        sys.exit(1)

    try:
        client = docker.from_env()
        client.ping()
        logger.info("Connected to Docker daemon")
    except docker.errors.DockerException as e:
        logger.error("Cannot connect to Docker daemon: %s", e)
        sys.exit(1)

    initial_scan(client)

    while True:
        try:
            event_stream(client)
        except Exception as e:
            logger.error("Event stream interrupted: %s — reconnecting in %ds", e, SCAN_INTERVAL)
            time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
