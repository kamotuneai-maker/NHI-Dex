from .models import AgentType, AutonomyLevel


def calculate_tier(
    agent_type: str,
    autonomy: str,
    is_registered: bool,
    has_owner: bool,
    has_mcp_config: bool,
    has_oauth_config: bool,
    mounts_docker_socket: bool,
    mounts_credential_store: bool,
    connected_networks: list[str],
    exposed_ports: list[int],
    env_names: list[str],
) -> tuple[str, str]:
    if not is_registered and not has_owner:
        return "AT0", "Unregistered agent with no governance — Shadow AI"

    has_external_access = any(
        kw in e.upper() for e in env_names
        for kw in ["WEBHOOK", "EXTERNAL", "AWS_REGION", "AZURE", "GCP"]
    )
    has_cross_boundary = len(connected_networks) >= 3 or any(
        kw in e.upper() for e in env_names for kw in ["FEDERATION", "CROSS_ORG", "MULTI_TENANT"]
    )

    if has_cross_boundary:
        return "AT8", "Cross-boundary or federated agent detected"

    if autonomy == "autonomous" and has_external_access and mounts_credential_store:
        return "AT7", "Fully autonomous with external access and credential store — high autonomy tier"

    if agent_type == "enterprise" or agent_type == "client-facing":
        if has_oauth_config or is_registered:
            return "AT5", f"Registered {agent_type} agent with governance controls"

    if has_external_access or (has_mcp_config and mounts_credential_store):
        return "AT6", "External tool access or credential-backed MCP — externally extended"

    if agent_type == "coding":
        return "AT4", "Code-executing agent tier"

    if has_mcp_config:
        return "AT3", "MCP tool access detected — tool-using tier"

    if agent_type in ("enterprise", "client-facing") and is_registered:
        return "AT2", "Registered conversational agent"

    if is_registered:
        return "AT1", "Basic registered agent — prompt/response only"

    return "AT0", "Insufficient governance signals — classified as Shadow AI"


TIER_ORDER = ["AT0", "AT1", "AT2", "AT3", "AT4", "AT5", "AT6", "AT7", "AT8"]


def tier_to_int(tier: str) -> int:
    try:
        return TIER_ORDER.index(tier)
    except ValueError:
        return 0
