from .models import Violation, ViolationType, ViolationSeverity


def detect_violations(
    container_id: str,
    container_name: str,
    is_registered: bool,
    has_owner: bool,
    mounts_docker_socket: bool,
    has_hardcoded_secret_env: bool,
    has_oauth_config: bool,
    adoption_tier: str,
    trifecta_score: int,
    trifecta_rule_of_two: bool,
    autonomy: str,
    labels: dict,
    env_names: list[str],
) -> list[Violation]:
    violations = []

    if not is_registered:
        violations.append(Violation(
            violation_type=ViolationType.UNREGISTERED_AGENT,
            container_id=container_id,
            container_name=container_name,
            description="Agent running without governance labels — Shadow AI",
            severity=ViolationSeverity.CRITICAL,
            asi_codes=["ASI07"],
            nhi_codes=["NHI-GOV-001"],
        ))

    if mounts_docker_socket:
        violations.append(Violation(
            violation_type=ViolationType.DOCKER_SOCKET_ACCESS,
            container_id=container_id,
            container_name=container_name,
            description="Agent has Docker socket access — host-level control plane exposure",
            severity=ViolationSeverity.CRITICAL,
            asi_codes=["ASI06"],
            nhi_codes=["NHI-INF-001"],
        ))

    if trifecta_rule_of_two:
        violations.append(Violation(
            violation_type=ViolationType.TRIFECTA_VIOLATION,
            container_id=container_id,
            container_name=container_name,
            description=f"Lethal Trifecta — all three conditions met (score {trifecta_score}) without human-in-the-loop",
            severity=ViolationSeverity.CRITICAL,
            asi_codes=["ASI02", "ASI06"],
            nhi_codes=["NHI-TRI-001"],
        ))

    tier_int = int(adoption_tier.replace("AT", ""))
    if has_hardcoded_secret_env and not has_oauth_config and tier_int >= 5:
        violations.append(Violation(
            violation_type=ViolationType.STATIC_CREDENTIALS,
            container_id=container_id,
            container_name=container_name,
            description=f"Static credentials at {adoption_tier} — non-rotating secrets in high-tier agent",
            severity=ViolationSeverity.HIGH,
            asi_codes=["ASI07"],
            nhi_codes=["NHI-CRD-001"],
        ))

    scope_label = None
    for key, value in labels.items():
        if "scope" in key.lower():
            scope_label = value.lower()
            break

    if scope_label and autonomy == "autonomous":
        env_upper = " ".join(env_names).upper()
        has_external_tools = any(kw in env_upper for kw in ["WEBHOOK", "EMAIL", "SMTP", "SLACK"])
        if "readonly" in scope_label.replace("-", "").replace("_", "") and has_external_tools:
            violations.append(Violation(
                violation_type=ViolationType.EXTERNAL_COMM_UNSCOPED,
                container_id=container_id,
                container_name=container_name,
                description="Autonomous agent with read-only scope has external communication capabilities",
                severity=ViolationSeverity.HIGH,
                asi_codes=["ASI06"],
                nhi_codes=["NHI-SCP-002"],
            ))

    return violations
