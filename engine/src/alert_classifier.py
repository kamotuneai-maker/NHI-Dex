from .models import AlertLevel, ViolationSeverity


def classify_alert(
    adoption_tier: str,
    is_registered: bool,
    has_owner: bool,
    has_agent_scope_label: bool,
    detection_mode: str,
    overall_confidence: float,
    trifecta_score: int,
    trifecta_rule_of_two: bool,
    mounts_docker_socket: bool,
    has_hardcoded_secret_env: bool,
    has_oauth_config: bool,
    violations: list,
) -> tuple[AlertLevel, list[str]]:
    reasons = []

    # RED conditions
    if adoption_tier == "AT0":
        reasons.append("AT0 Shadow AI — unregistered agent")

    if trifecta_rule_of_two:
        reasons.append(f"Lethal Trifecta Rule of Two violation (score {trifecta_score})")

    if mounts_docker_socket:
        reasons.append("Docker socket mounted — host-level control plane access")

    tier_int = int(adoption_tier.replace("AT", ""))
    if has_hardcoded_secret_env and not has_oauth_config and tier_int >= 5:
        reasons.append(f"Static credentials at {adoption_tier}")

    critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
    if critical_violations:
        reasons.append(f"{len(critical_violations)} critical violation(s) active")

    if reasons:
        return AlertLevel.RED, reasons

    # YELLOW conditions
    yellow_reasons = []

    if detection_mode == "BEHAVIORAL":
        yellow_reasons.append("Classification based on behavioral inference only — not signature-confirmed")

    if overall_confidence < 0.5:
        yellow_reasons.append(f"Low classification confidence ({overall_confidence:.0%})")

    if trifecta_score >= 2:
        yellow_reasons.append(f"Trifecta score {trifecta_score} — approaching Rule of Two threshold")

    if is_registered and (not has_owner or not has_agent_scope_label):
        yellow_reasons.append("Partially registered — missing owner or scope labels")

    if has_hardcoded_secret_env and not has_oauth_config:
        yellow_reasons.append("API key without OAuth — static credential risk")

    high_med_violations = [
        v for v in violations
        if v.severity in (ViolationSeverity.HIGH, ViolationSeverity.MEDIUM)
    ]
    if high_med_violations:
        yellow_reasons.append(f"{len(high_med_violations)} high/medium violation(s) active")

    if yellow_reasons:
        return AlertLevel.YELLOW, yellow_reasons

    return AlertLevel.GREEN, ["Registered, governed, signature-confirmed, no active violations"]
