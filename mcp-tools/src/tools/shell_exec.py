import logging
from datetime import datetime

logger = logging.getLogger("mcp-tools.shell_exec")


def shell_exec(command: str) -> dict:
    logger.warning("shell_exec called (scope violation trigger): command=%s", command)
    return {
        "tool": "shell_exec",
        "command": command,
        "stdout": "total 48\ndrwxr-xr-x 12 root root 4096 Jun 29 00:00 .\ndrwxr-xr-x  3 root root 4096 Jun 29 00:00 ..",
        "stderr": "",
        "exit_code": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }
