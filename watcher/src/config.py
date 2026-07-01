import os

ENGINE_URL = os.getenv("ENGINE_URL", "http://engine:8000")
DETECT_ENDPOINT = f"{ENGINE_URL}/api/detect"
HEALTH_ENDPOINT = f"{ENGINE_URL}/health"

DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "unix:///var/run/docker.sock")

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "30"))

SELF_CONTAINER_NAMES = frozenset({
    # bare service names
    "engine", "watcher", "dashboard", "db", "mcp-tools",
    # compose-prefixed (nhi-dex-<service>-<n>)
    "nhi-dex-engine", "nhi-dex-watcher", "nhi-dex-dashboard",
    "nhi-dex-db", "nhi-dex-mcp-tools",
})

HEALTH_CHECK_ATTEMPTS = 30
HEALTH_CHECK_INTERVAL = 2
