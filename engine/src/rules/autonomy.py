from ..models import TaxonomyResult


def classify_autonomy(
    labels: dict,
    env_names: list[str],
    has_owner: bool,
    is_registered: bool,
    mounts_docker_socket: bool,
    mounts_credential_store: bool,
    exposed_ports: list[int],
) -> TaxonomyResult:
    label_values = " ".join(f"{k} {v}" for k, v in labels.items()).lower()

    if any(kw in label_values for kw in ["supervised", "human-in-the-loop", "hitl", "approval-required"]):
        return TaxonomyResult(
            value="supervised",
            confidence=0.85,
            reasoning="Labels explicitly declare supervised/HITL autonomy",
        )

    if any(kw in label_values for kw in ["autonomous", "fully-autonomous", "auto-execute"]):
        return TaxonomyResult(
            value="autonomous",
            confidence=0.85,
            reasoning="Labels explicitly declare fully autonomous operation",
        )

    if any(kw in label_values for kw in ["semi-autonomous", "semi-auto", "limited-auto"]):
        return TaxonomyResult(
            value="semi-autonomous",
            confidence=0.85,
            reasoning="Labels explicitly declare semi-autonomous operation",
        )

    env_upper = [e.upper() for e in env_names]
    has_approval_gate = any(kw in e for e in env_upper for kw in ["APPROVAL", "HITL", "HUMAN_REVIEW"])
    has_auto_exec = any(kw in e for e in env_upper for kw in ["AUTO_EXEC", "AUTO_DEPLOY", "AUTO_SCALE"])

    if has_approval_gate:
        return TaxonomyResult(
            value="supervised",
            confidence=0.7,
            reasoning="Environment variables indicate approval/HITL gates",
        )

    autonomy_score = 0.0
    reasons = []

    if not is_registered:
        autonomy_score += 0.3
        reasons.append("unregistered agent")

    if not has_owner:
        autonomy_score += 0.2
        reasons.append("no owner declared")

    if mounts_docker_socket:
        autonomy_score += 0.3
        reasons.append("Docker socket access")

    if mounts_credential_store:
        autonomy_score += 0.15
        reasons.append("credential store mounted")

    if has_auto_exec:
        autonomy_score += 0.3
        reasons.append("auto-execution environment config")

    if len(exposed_ports) > 2:
        autonomy_score += 0.1
        reasons.append("multiple exposed ports")

    if autonomy_score >= 0.6:
        return TaxonomyResult(
            value="autonomous",
            confidence=round(min(autonomy_score, 0.95), 2),
            reasoning=f"High autonomy indicators: {', '.join(reasons)}",
        )
    elif autonomy_score >= 0.3:
        return TaxonomyResult(
            value="semi-autonomous",
            confidence=round(0.5 + autonomy_score * 0.3, 2),
            reasoning=f"Moderate autonomy indicators: {', '.join(reasons)}",
        )
    else:
        return TaxonomyResult(
            value="semi-autonomous",
            confidence=0.4,
            reasoning="Default classification — insufficient autonomy signals for confident assessment",
        )
