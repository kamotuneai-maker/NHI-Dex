from .models import TrifectaScore


def score_trifecta(
    has_api_key_env: bool,
    has_model_endpoint: bool,
    mounts_credential_store: bool,
    mounts_docker_socket: bool,
    has_mcp_config: bool,
    env_names: list[str],
    mounted_volumes: list[str],
    exposed_ports: list[int],
    labels: dict,
    autonomy: str,
) -> TrifectaScore:
    has_private_data = (
        has_api_key_env
        or mounts_credential_store
        or any(kw in e.upper() for e in env_names for kw in ["DB_", "DATABASE", "REDIS", "MONGO"])
    )

    has_untrusted_content = (
        any(kw in e.upper() for e in env_names for kw in ["WEBHOOK", "CALLBACK", "EXTERNAL_INPUT"])
        or any(kw in " ".join(f"{k} {v}" for k, v in labels.items()).lower()
               for kw in ["client-facing", "customer", "public"])
        or mounts_docker_socket
    )

    has_external_comm = (
        any(kw in e.upper() for e in env_names
            for kw in ["WEBHOOK_URL", "SMTP", "EMAIL", "SLACK", "NOTIFICATION", "AWS_REGION", "AZURE", "GCP"])
        or len(exposed_ports) > 1
    )

    score = sum([has_private_data, has_untrusted_content, has_external_comm])

    is_unsupervised = autonomy in ("autonomous", "semi-autonomous")
    rule_of_two_violation = score >= 3 and is_unsupervised

    return TrifectaScore(
        has_private_data_access=has_private_data,
        has_untrusted_content_exposure=has_untrusted_content,
        has_external_communication=has_external_comm,
        score=score,
        rule_of_two_violation=rule_of_two_violation,
    )
