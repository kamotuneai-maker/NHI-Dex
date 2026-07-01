import logging
from datetime import datetime
import random

logger = logging.getLogger("mcp-tools.cloud_status")


def cloud_status(region: str = "us-east-1") -> dict:
    logger.info("cloud_status called: region=%s", region)
    return {
        "tool": "cloud_status",
        "region": region,
        "services": {
            "ec2": {"status": "healthy", "instances_running": random.randint(8, 24)},
            "rds": {"status": "healthy", "connections": random.randint(40, 120)},
            "s3": {"status": "healthy", "buckets": 14},
            "eks": {"status": random.choice(["healthy", "degraded"]), "nodes": random.randint(3, 9)},
        },
        "alerts": random.randint(0, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
