import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    desc,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .models import ClassifiedAgent, Violation
from .storage import StorageBackend

logger = logging.getLogger("nhi-dex.db")


class Base(DeclarativeBase):
    pass


class AgentRecord(Base):
    __tablename__ = "agents"

    container_id = Column(String(12), primary_key=True)
    container_name = Column(String(255), nullable=False)
    image_name = Column(String(255))
    image_tag = Column(String(64))
    classification_json = Column(Text, nullable=False)
    adoption_tier = Column(String(4), index=True)
    alert_level = Column(String(10), index=True)
    agent_type = Column(String(32), index=True)
    autonomy_level = Column(String(20))
    detection_mode = Column(String(12))
    overall_confidence = Column(String(10))
    status = Column(String(16), index=True, default="active")
    first_detected = Column(DateTime(timezone=True))
    last_seen = Column(DateTime(timezone=True))


class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(12), index=True)
    container_name = Column(String(255))
    level = Column(String(10), index=True)
    reasons_json = Column(Text)
    tier = Column(String(4))
    timestamp = Column(DateTime(timezone=True), index=True)


class ViolationRecord(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(12), index=True)
    container_name = Column(String(255))
    violation_type = Column(String(32), index=True)
    severity = Column(String(10), index=True)
    description = Column(Text)
    asi_codes_json = Column(Text)
    nhi_codes_json = Column(Text)
    timestamp = Column(DateTime(timezone=True), index=True)


def _get_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "nhidex")
    password = os.getenv("POSTGRES_PASSWORD", "nhidex-dev")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "nhidex")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


class PostgresStorage(StorageBackend):
    def __init__(self, database_url: Optional[str] = None):
        self._url = database_url or _get_database_url()
        self._engine = None
        self._session_factory = None

    def initialize(self) -> None:
        self._engine = create_engine(self._url, pool_pre_ping=True)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)
        logger.info("PostgreSQL storage initialized at %s", self._url.split("@")[-1])

    def _session(self) -> Session:
        return self._session_factory()

    def upsert_agent(self, agent: ClassifiedAgent) -> None:
        with self._session() as session:
            existing = session.get(AgentRecord, agent.container_id)
            classification = agent.model_dump(mode="json")

            if existing:
                existing.container_name = agent.container_name
                existing.image_name = agent.image_name
                existing.image_tag = agent.image_tag
                existing.classification_json = json.dumps(classification)
                existing.adoption_tier = agent.adoption_tier
                existing.alert_level = agent.alert_level.value
                existing.agent_type = agent.agent_type.value
                existing.autonomy_level = agent.autonomy_level.value
                existing.detection_mode = agent.detection_mode.value
                existing.overall_confidence = str(agent.overall_confidence)
                existing.status = agent.status
                existing.last_seen = datetime.now(timezone.utc)
            else:
                record = AgentRecord(
                    container_id=agent.container_id,
                    container_name=agent.container_name,
                    image_name=agent.image_name,
                    image_tag=agent.image_tag,
                    classification_json=json.dumps(classification),
                    adoption_tier=agent.adoption_tier,
                    alert_level=agent.alert_level.value,
                    agent_type=agent.agent_type.value,
                    autonomy_level=agent.autonomy_level.value,
                    detection_mode=agent.detection_mode.value,
                    overall_confidence=str(agent.overall_confidence),
                    status=agent.status,
                    first_detected=datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc),
                )
                session.add(record)

            if agent.alert_level.value in ("RED", "YELLOW"):
                alert = AlertRecord(
                    container_id=agent.container_id,
                    container_name=agent.container_name,
                    level=agent.alert_level.value,
                    reasons_json=json.dumps(agent.alert_reasons),
                    tier=agent.adoption_tier,
                    timestamp=datetime.now(timezone.utc),
                )
                session.add(alert)

            session.commit()

    def remove_agent(self, container_id: str) -> None:
        with self._session() as session:
            record = session.get(AgentRecord, container_id)
            if record:
                record.status = "removed"
                record.last_seen = datetime.now(timezone.utc)
                session.commit()

    def get_agent(self, container_id: str) -> Optional[dict]:
        with self._session() as session:
            record = session.get(AgentRecord, container_id)
            if not record:
                return None
            return json.loads(record.classification_json)

    def list_agents(self, status: Optional[str] = None) -> list[dict]:
        with self._session() as session:
            query = session.query(AgentRecord)
            if status:
                query = query.filter(AgentRecord.status == status)
            records = query.order_by(desc(AgentRecord.last_seen)).all()
            return [json.loads(r.classification_json) for r in records]

    def log_violation(self, violation: Violation) -> None:
        with self._session() as session:
            record = ViolationRecord(
                container_id=violation.container_id,
                container_name=violation.container_name,
                violation_type=violation.violation_type.value,
                severity=violation.severity.value,
                description=violation.description,
                asi_codes_json=json.dumps(violation.asi_codes),
                nhi_codes_json=json.dumps(violation.nhi_codes),
                timestamp=datetime.now(timezone.utc),
            )
            session.add(record)
            session.commit()

    def get_violations(
        self,
        violation_type: Optional[str] = None,
        severity: Optional[str] = None,
        container_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        with self._session() as session:
            query = session.query(ViolationRecord)
            if violation_type:
                query = query.filter(ViolationRecord.violation_type == violation_type)
            if severity:
                query = query.filter(ViolationRecord.severity == severity)
            if container_id:
                query = query.filter(ViolationRecord.container_id == container_id)
            records = query.order_by(desc(ViolationRecord.timestamp)).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "violation_type": r.violation_type,
                    "container_id": r.container_id,
                    "container_name": r.container_name,
                    "description": r.description,
                    "severity": r.severity,
                    "asi_codes": json.loads(r.asi_codes_json),
                    "nhi_codes": json.loads(r.nhi_codes_json),
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                }
                for r in records
            ]

    def log_alert(self, alert: dict) -> None:
        with self._session() as session:
            record = AlertRecord(
                container_id=alert["container_id"],
                container_name=alert["container_name"],
                level=alert["level"],
                reasons_json=json.dumps(alert.get("reasons", [])),
                tier=alert.get("tier", ""),
                timestamp=datetime.now(timezone.utc),
            )
            session.add(record)
            session.commit()

    def get_alert_history(
        self,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        with self._session() as session:
            query = session.query(AlertRecord)
            if level:
                query = query.filter(AlertRecord.level == level.upper())
            records = query.order_by(desc(AlertRecord.timestamp)).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "container_id": r.container_id,
                    "container_name": r.container_name,
                    "level": r.level,
                    "reasons": json.loads(r.reasons_json) if r.reasons_json else [],
                    "tier": r.tier,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                }
                for r in records
            ]
