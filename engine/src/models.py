from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    ENTERPRISE = "enterprise"
    CODING = "coding"
    CLIENT_FACING = "client-facing"
    PERSONAL = "personal"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class ImplementationPattern(str, Enum):
    FRAMEWORK = "framework"
    LIBRARY = "library"
    LOW_CODE = "low-code"
    PLATFORM = "platform"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class CompositionPattern(str, Enum):
    STANDALONE = "standalone"
    PIPELINE = "pipeline"
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    UNKNOWN = "unknown"


class AutonomyLevel(str, Enum):
    SUPERVISED = "supervised"
    SEMI_AUTONOMOUS = "semi-autonomous"
    AUTONOMOUS = "autonomous"
    UNKNOWN = "unknown"


class AdoptionTier(str, Enum):
    AT0 = "AT0"
    AT1 = "AT1"
    AT2 = "AT2"
    AT3 = "AT3"
    AT4 = "AT4"
    AT5 = "AT5"
    AT6 = "AT6"
    AT7 = "AT7"
    AT8 = "AT8"


class AlertLevel(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class DetectionMode(str, Enum):
    SIGNATURE = "SIGNATURE"
    BEHAVIORAL = "BEHAVIORAL"
    HYBRID = "HYBRID"


class ViolationType(str, Enum):
    SCOPE_EXCEEDED = "SCOPE_EXCEEDED"
    CROSS_ENVIRONMENT = "CROSS_ENVIRONMENT"
    TRIFECTA_VIOLATION = "TRIFECTA_VIOLATION"
    STATIC_CREDENTIALS = "STATIC_CREDENTIALS"
    UNREGISTERED_AGENT = "UNREGISTERED_AGENT"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    DOCKER_SOCKET_ACCESS = "DOCKER_SOCKET_ACCESS"
    EXTERNAL_COMM_UNSCOPED = "EXTERNAL_COMM_UNSCOPED"


class ViolationSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaxonomyResult(BaseModel):
    value: str
    confidence: float = 0.0
    reasoning: str = ""


class TrifectaScore(BaseModel):
    has_private_data_access: bool = False
    has_untrusted_content_exposure: bool = False
    has_external_communication: bool = False
    score: int = 0
    rule_of_two_violation: bool = False


class Violation(BaseModel):
    violation_type: ViolationType
    container_id: str
    container_name: str
    description: str
    severity: ViolationSeverity
    asi_codes: list[str] = []
    nhi_codes: list[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ClassifiedAgent(BaseModel):
    # Identity
    container_id: str
    container_name: str
    image_name: str
    image_tag: str = "latest"

    # Detection
    detection_mode: DetectionMode = DetectionMode.SIGNATURE
    signature_confidence: float = 0.0
    behavioral_confidence: float = 0.0
    overall_confidence: float = 0.0

    # Taxonomy
    agent_type: TaxonomyResult = Field(default_factory=lambda: TaxonomyResult(value="unknown"))
    implementation_pattern: TaxonomyResult = Field(default_factory=lambda: TaxonomyResult(value="unknown"))
    composition_pattern: TaxonomyResult = Field(default_factory=lambda: TaxonomyResult(value="unknown"))
    autonomy_level: TaxonomyResult = Field(default_factory=lambda: TaxonomyResult(value="unknown"))

    # Tier
    adoption_tier: str = "AT0"
    tier_reasoning: str = ""

    # Risk
    asi_risks: list[str] = []
    asi_risk_descriptions: dict[str, str] = {}
    trifecta: TrifectaScore = Field(default_factory=TrifectaScore)

    # Governance
    is_registered: bool = False
    is_labeled: bool = False
    has_owner: bool = False
    governance_flags: list[str] = []

    # Alert
    alert_level: AlertLevel = AlertLevel.GREEN
    alert_reasons: list[str] = []

    # Violations
    violations: list[Violation] = []

    # Temporal
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"

    # Raw signals (for re-classification)
    labels: dict = {}
    env_var_names: list[str] = []
    exposed_ports: list[int] = []
    mounted_volumes: list[str] = []
    mounts_docker_socket: bool = False
    mounts_credential_store: bool = False
    has_api_key_env: bool = False
    has_hardcoded_secret_env: bool = False
    has_oauth_config: bool = False
    has_mcp_config: bool = False
    has_model_endpoint: bool = False
