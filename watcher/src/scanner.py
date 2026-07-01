import logging
from typing import Optional

import docker
from docker.models.containers import Container

from .signals import SignalFingerprint
from .config import SELF_CONTAINER_NAMES

logger = logging.getLogger("nhi-dex.scanner")

IMAGE_SIGNATURES = {
    "mcp": ["mcp-server", "modelcontextprotocol"],
    "orchestration": ["langchain", "langgraph", "autogen", "crewai", "dspy", "google-adk"],
    "coding": ["claude-code", "codex", "devin", "cursor", "aider", "cline", "open-interpreter", "sweep"],
    "platform": ["copilot", "amazon-q", "bedrock-agent", "vertex-ai", "einstein", "agentforce"],
    "llm_inference": ["ollama", "vllm", "llama-cpp", "tgi"],
}

GENERIC_AGENT_PATTERNS = ["agent-", "-agent", "ai-agent"]

CREDENTIAL_ENV_PATTERNS = ["API_KEY", "SECRET", "TOKEN", "PASSWORD"]
MCP_ENV_PATTERNS = ["MCP", "MODEL_CONTEXT"]
MODEL_ENDPOINT_PATTERNS = ["OPENAI", "ANTHROPIC", "MODEL_ENDPOINT", "LLM_BASE", "OLLAMA_HOST"]
OAUTH_ENV_PATTERNS = ["OAUTH", "CLIENT_ID", "CLIENT_SECRET"]

GOVERNANCE_LABEL_PREFIXES = ["agent.name", "agent.type", "agent.owner", "agent.scope", "mcp.server", "nhi-dex."]

CREDENTIAL_VOLUME_PATTERNS = [".aws", ".azure", ".gcp", ".kube", "vault", "secrets", "credentials", ".ssh"]

LLM_API_DOMAINS = [
    "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
    "api.cohere.ai", "api.mistral.ai", "api.together.xyz",
    "api.groq.com", "api.fireworks.ai", "api.replicate.com",
]

MCP_BEHAVIORAL_INDICATORS = ["sse", "tools/call", "tools/list", "resources/read"]

AGENT_PORTS = {3000, 3001, 8080, 8888, 9000}


def is_self_container(container: Container) -> bool:
    name = container.name.lower().lstrip("/")
    if name in SELF_CONTAINER_NAMES:
        return True
    for self_name in SELF_CONTAINER_NAMES:
        if self_name in name:
            return True
    return False


def _match_env_patterns(env_names: list[str], patterns: list[str]) -> bool:
    for name in env_names:
        upper = name.upper()
        for pattern in patterns:
            if pattern in upper:
                return True
    return False


def _match_image_signatures(image_name: str) -> tuple[Optional[str], float]:
    lower = image_name.lower()
    for category, patterns in IMAGE_SIGNATURES.items():
        for pattern in patterns:
            if pattern in lower:
                return category, 0.7
    for pattern in GENERIC_AGENT_PATTERNS:
        if pattern in lower:
            return "generic_agent", 0.5
    return None, 0.0


def _check_governance_labels(labels: dict) -> tuple[bool, bool, bool, float]:
    has_owner = False
    has_name = False
    has_scope = False
    confidence_boost = 0.0

    for key in labels:
        lower_key = key.lower()
        for prefix in GOVERNANCE_LABEL_PREFIXES:
            if lower_key.startswith(prefix) or lower_key.startswith(f"nhi-dex.{prefix}"):
                confidence_boost = 0.2
                break
        if "owner" in lower_key:
            has_owner = True
        if "agent.name" in lower_key or "nhi-dex.agent.name" in lower_key:
            has_name = True
        if "scope" in lower_key:
            has_scope = True

    return has_name, has_owner, has_scope, confidence_boost


def _check_credential_volumes(mounts: list[str]) -> tuple[bool, bool]:
    mounts_docker_socket = False
    mounts_credential_store = False

    for mount in mounts:
        lower = mount.lower()
        if "docker.sock" in lower:
            mounts_docker_socket = True
        for pattern in CREDENTIAL_VOLUME_PATTERNS:
            if pattern in lower:
                mounts_credential_store = True
                break

    return mounts_docker_socket, mounts_credential_store


def extract_fingerprint(container: Container) -> SignalFingerprint:
    attrs = container.attrs or {}
    config = attrs.get("Config", {})
    host_config = attrs.get("HostConfig", {})
    network_settings = attrs.get("NetworkSettings", {})

    image_name = config.get("Image", "")
    image_parts = image_name.rsplit(":", 1)
    image_base = image_parts[0]
    image_tag = image_parts[1] if len(image_parts) > 1 else "latest"

    labels = config.get("Labels", {}) or {}

    env_list = config.get("Env", []) or []
    env_names = [e.split("=", 1)[0] for e in env_list]

    exposed_ports = []
    ports_config = config.get("ExposedPorts", {}) or {}
    for port_str in ports_config:
        try:
            exposed_ports.append(int(port_str.split("/")[0]))
        except (ValueError, IndexError):
            pass

    mounts = []
    mount_list = attrs.get("Mounts", []) or []
    for mount in mount_list:
        source = mount.get("Source", "")
        if source:
            mounts.append(source)
    binds = host_config.get("Binds", []) or []
    for bind in binds:
        source = bind.split(":")[0]
        if source and source not in mounts:
            mounts.append(source)

    networks = list((network_settings.get("Networks", {}) or {}).keys())
    network_mode = host_config.get("NetworkMode", "")

    entrypoint = " ".join(config.get("Entrypoint", []) or [])
    command = " ".join(config.get("Cmd", []) or [])

    has_api_key = _match_env_patterns(env_names, CREDENTIAL_ENV_PATTERNS)
    has_mcp = _match_env_patterns(env_names, MCP_ENV_PATTERNS)
    has_model_endpoint = _match_env_patterns(env_names, MODEL_ENDPOINT_PATTERNS)
    has_oauth = _match_env_patterns(env_names, OAUTH_ENV_PATTERNS)
    has_hardcoded = _match_env_patterns(env_names, ["API_KEY", "SECRET_KEY"])

    has_name_label, has_owner_label, has_scope_label, label_confidence = _check_governance_labels(labels)
    mounts_docker_socket, mounts_credential_store = _check_credential_volumes(mounts)

    # --- Signature detection ---
    image_category, image_confidence = _match_image_signatures(image_base)
    env_confidence = 0.15 if has_api_key or has_model_endpoint or has_mcp else 0.0

    signature_confidence = min(1.0, image_confidence + label_confidence + env_confidence)

    # --- Behavioral inference ---
    behavioral_confidence = 0.0
    port_match = bool(set(exposed_ports) & AGENT_PORTS)
    if port_match:
        behavioral_confidence += 0.1
    if has_mcp:
        behavioral_confidence += 0.15

    behavioral_confidence = min(1.0, behavioral_confidence)

    # --- Detection mode ---
    if signature_confidence >= 0.3 and behavioral_confidence > 0:
        detection_mode = "HYBRID"
        overall_confidence = min(1.0, max(signature_confidence, behavioral_confidence) + 0.1)
    elif signature_confidence >= 0.3:
        detection_mode = "SIGNATURE"
        overall_confidence = signature_confidence
    elif behavioral_confidence >= 0.2:
        detection_mode = "BEHAVIORAL"
        overall_confidence = behavioral_confidence
    else:
        detection_mode = "SIGNATURE"
        overall_confidence = max(signature_confidence, behavioral_confidence)

    return SignalFingerprint(
        container_id=container.id[:12],
        container_name=container.name.lstrip("/"),
        image_name=image_base,
        image_tag=image_tag,
        labels=labels,
        has_owner_label=has_owner_label,
        has_agent_name_label=has_name_label,
        has_agent_scope_label=has_scope_label,
        env_var_names=env_names,
        has_api_key_env=has_api_key,
        has_hardcoded_secret_env=has_hardcoded,
        has_oauth_config=has_oauth,
        has_mcp_config=has_mcp,
        has_model_endpoint=has_model_endpoint,
        exposed_ports=exposed_ports,
        mounted_volumes=mounts,
        mounts_docker_socket=mounts_docker_socket,
        mounts_credential_store=mounts_credential_store,
        network_mode=network_mode,
        connected_networks=networks,
        entrypoint=entrypoint,
        command=command,
        detection_mode=detection_mode,
        signature_confidence=round(signature_confidence, 2),
        behavioral_confidence=round(behavioral_confidence, 2),
        overall_confidence=round(overall_confidence, 2),
    )
