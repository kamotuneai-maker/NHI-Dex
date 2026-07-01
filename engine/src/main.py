import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .classifier import run_classification_pipeline
from .db import PostgresStorage
from .events import event_manager
from .models import AlertLevel, ClassifiedAgent
from .storage import StorageBackend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("nhi-dex.engine")

agents_cache: dict[str, ClassifiedAgent] = {}
storage: Optional[StorageBackend] = None


def _init_storage() -> Optional[StorageBackend]:
    if os.getenv("DISABLE_POSTGRES", "").lower() in ("1", "true"):
        logger.info("Postgres disabled — running with in-memory storage only")
        return None
    try:
        pg = PostgresStorage()
        pg.initialize()
        logger.info("Postgres storage initialized")
        return pg
    except Exception as e:
        logger.warning("Postgres unavailable, falling back to in-memory: %s", e)
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global storage
    storage = _init_storage()
    yield


app = FastAPI(title="NHI-Dex Classification Engine", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectionEvent(BaseModel):
    container_id: str
    container_name: str
    image_name: str = ""
    image_tag: str = "latest"
    labels: dict = {}
    has_owner_label: bool = False
    has_agent_name_label: bool = False
    has_agent_scope_label: bool = False
    env_var_names: list[str] = []
    has_api_key_env: bool = False
    has_hardcoded_secret_env: bool = False
    has_oauth_config: bool = False
    has_mcp_config: bool = False
    has_model_endpoint: bool = False
    exposed_ports: list[int] = []
    mounted_volumes: list[str] = []
    mounts_docker_socket: bool = False
    mounts_credential_store: bool = False
    network_mode: str = ""
    connected_networks: list[str] = []
    entrypoint: str = ""
    command: str = ""
    outbound_domains: list[str] = []
    api_call_rate: float = 0.0
    mcp_protocol_detected: bool = False
    llm_api_traffic_detected: bool = False
    detection_mode: str = "SIGNATURE"
    signature_confidence: float = 0.0
    behavioral_confidence: float = 0.0
    overall_confidence: float = 0.0
    event: str | None = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "nhi-dex-engine",
        "version": "0.3.0",
        "storage": "postgres" if storage else "in-memory",
    }


@app.post("/api/detect")
async def detect(event: DetectionEvent):
    if event.event == "removed":
        removed = agents_cache.pop(event.container_id, None)
        if removed:
            logger.info("Agent removed: %s (%s)", event.container_name, event.container_id)
            if storage:
                storage.remove_agent(event.container_id)
            await event_manager.broadcast("agent_removed", {
                "container_id": event.container_id,
                "container_name": event.container_name,
            })
        return {"status": "removed", "container_id": event.container_id}

    classified = run_classification_pipeline(event.model_dump())

    existing = agents_cache.get(event.container_id)
    if existing:
        classified.first_detected = existing.first_detected

    agents_cache[event.container_id] = classified

    if storage:
        storage.upsert_agent(classified)
        for v in classified.violations:
            storage.log_violation(v)

    agent_data = classified.model_dump()
    await event_manager.broadcast("agent_classified", agent_data)

    if classified.alert_level in (AlertLevel.RED, AlertLevel.YELLOW):
        alert_record = {
            "container_id": classified.container_id,
            "container_name": classified.container_name,
            "level": classified.alert_level.value,
            "reasons": classified.alert_reasons,
            "tier": classified.adoption_tier,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await event_manager.broadcast("alert", alert_record)

    for v in classified.violations:
        await event_manager.broadcast("violation", v.model_dump())

    return {"status": "classified", "container_id": classified.container_id, "tier": classified.adoption_tier}


@app.get("/api/agents")
async def list_agents():
    if storage:
        agents = storage.list_agents(status="active")
    else:
        agents = [a.model_dump() for a in agents_cache.values()]
    return {"agents": agents, "count": len(agents)}


@app.get("/api/agents/{container_id}")
async def get_agent(container_id: str):
    if storage:
        agent = storage.get_agent(container_id)
    else:
        cached = agents_cache.get(container_id)
        agent = cached.model_dump() if cached else None
    if not agent:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return agent


@app.get("/api/summary")
async def summary():
    agents = list(agents_cache.values())
    tier_dist: dict[str, int] = {}
    for a in agents:
        tier_dist[a.adoption_tier] = tier_dist.get(a.adoption_tier, 0) + 1

    return {
        "total_agents": len(agents),
        "active": sum(1 for a in agents if a.status == "active"),
        "shadow_ai_count": sum(1 for a in agents if a.adoption_tier == "AT0"),
        "red_alerts": sum(1 for a in agents if a.alert_level == AlertLevel.RED),
        "yellow_alerts": sum(1 for a in agents if a.alert_level == AlertLevel.YELLOW),
        "green_alerts": sum(1 for a in agents if a.alert_level == AlertLevel.GREEN),
        "trifecta_violations": sum(1 for a in agents if a.trifecta.rule_of_two_violation),
        "active_violations": sum(len(a.violations) for a in agents),
        "tier_distribution": tier_dist,
        "storage": "postgres" if storage else "in-memory",
    }


@app.get("/api/alerts")
async def list_alerts(
    level: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    if storage:
        alerts = storage.get_alert_history(level=level, limit=limit)
    else:
        alerts = []
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/api/violations")
async def list_violations(
    violation_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    container_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    if storage:
        violations = storage.get_violations(
            violation_type=violation_type,
            severity=severity,
            container_id=container_id,
            limit=limit,
        )
    else:
        violations = []
    return {"violations": violations, "count": len(violations)}


@app.get("/api/events")
async def sse_events():
    async def stream():
        async for message in event_manager.subscribe():
            yield {"data": message}
    return EventSourceResponse(stream())
