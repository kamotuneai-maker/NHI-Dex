from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SignalFingerprint:
    # Identity
    container_id: str
    container_name: str
    image_name: str
    image_tag: str = "latest"

    # Governance signals
    labels: dict = field(default_factory=dict)
    has_owner_label: bool = False
    has_agent_name_label: bool = False
    has_agent_scope_label: bool = False

    # Credential signals (names only, NEVER values)
    env_var_names: list[str] = field(default_factory=list)
    has_api_key_env: bool = False
    has_hardcoded_secret_env: bool = False
    has_oauth_config: bool = False
    has_mcp_config: bool = False
    has_model_endpoint: bool = False

    # Infrastructure signals
    exposed_ports: list[int] = field(default_factory=list)
    mounted_volumes: list[str] = field(default_factory=list)
    mounts_docker_socket: bool = False
    mounts_credential_store: bool = False

    # Network signals
    network_mode: str = ""
    connected_networks: list[str] = field(default_factory=list)

    # Process signals
    entrypoint: str = ""
    command: str = ""

    # Behavioral signals (populated by behavioral inference)
    outbound_domains: list[str] = field(default_factory=list)
    api_call_rate: float = 0.0
    mcp_protocol_detected: bool = False
    llm_api_traffic_detected: bool = False

    # Detection metadata
    detection_mode: str = "SIGNATURE"
    signature_confidence: float = 0.0
    behavioral_confidence: float = 0.0
    overall_confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "container_id": self.container_id,
            "container_name": self.container_name,
            "image_name": self.image_name,
            "image_tag": self.image_tag,
            "labels": self.labels,
            "has_owner_label": self.has_owner_label,
            "has_agent_name_label": self.has_agent_name_label,
            "has_agent_scope_label": self.has_agent_scope_label,
            "env_var_names": self.env_var_names,
            "has_api_key_env": self.has_api_key_env,
            "has_hardcoded_secret_env": self.has_hardcoded_secret_env,
            "has_oauth_config": self.has_oauth_config,
            "has_mcp_config": self.has_mcp_config,
            "has_model_endpoint": self.has_model_endpoint,
            "exposed_ports": self.exposed_ports,
            "mounted_volumes": self.mounted_volumes,
            "mounts_docker_socket": self.mounts_docker_socket,
            "mounts_credential_store": self.mounts_credential_store,
            "network_mode": self.network_mode,
            "connected_networks": self.connected_networks,
            "entrypoint": self.entrypoint,
            "command": self.command,
            "outbound_domains": self.outbound_domains,
            "api_call_rate": self.api_call_rate,
            "mcp_protocol_detected": self.mcp_protocol_detected,
            "llm_api_traffic_detected": self.llm_api_traffic_detected,
            "detection_mode": self.detection_mode,
            "signature_confidence": self.signature_confidence,
            "behavioral_confidence": self.behavioral_confidence,
            "overall_confidence": self.overall_confidence,
        }
