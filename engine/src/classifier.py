import logging
from datetime import datetime, timezone

from .models import ClassifiedAgent, DetectionMode, TaxonomyResult
from .rules.agent_types import classify_agent_type
from .rules.implementation import classify_implementation
from .rules.composition import classify_composition
from .rules.autonomy import classify_autonomy
from .tier_calculator import calculate_tier
from .risk_mapper import map_risks
from .trifecta import score_trifecta
from .violation_tracker import detect_violations
from .alert_classifier import classify_alert

logger = logging.getLogger("nhi-dex.classifier")


def run_classification_pipeline(detection: dict) -> ClassifiedAgent:
    container_id = detection["container_id"]
    container_name = detection["container_name"]
    image_name = detection.get("image_name", "")
    image_tag = detection.get("image_tag", "latest")

    labels = detection.get("labels", {})
    env_names = detection.get("env_var_names", [])
    exposed_ports = detection.get("exposed_ports", [])
    mounted_volumes = detection.get("mounted_volumes", [])
    connected_networks = detection.get("connected_networks", [])

    has_api_key_env = detection.get("has_api_key_env", False)
    has_hardcoded_secret_env = detection.get("has_hardcoded_secret_env", False)
    has_oauth_config = detection.get("has_oauth_config", False)
    has_mcp_config = detection.get("has_mcp_config", False)
    has_model_endpoint = detection.get("has_model_endpoint", False)
    mounts_docker_socket = detection.get("mounts_docker_socket", False)
    mounts_credential_store = detection.get("mounts_credential_store", False)

    has_owner = detection.get("has_owner_label", False)
    has_agent_name = detection.get("has_agent_name_label", False)
    has_agent_scope = detection.get("has_agent_scope_label", False)

    detection_mode_str = detection.get("detection_mode", "SIGNATURE")
    signature_confidence = detection.get("signature_confidence", 0.0)
    behavioral_confidence = detection.get("behavioral_confidence", 0.0)
    overall_confidence = detection.get("overall_confidence", 0.0)

    is_registered = has_agent_name or bool(labels)
    is_labeled = bool(labels)

    # 1. Classify agent type
    agent_type = classify_agent_type(
        image_name=image_name,
        labels=labels,
        env_names=env_names,
        has_oauth=has_oauth_config,
        mounts_credential_store=mounts_credential_store,
    )

    # 2. Classify implementation pattern
    implementation = classify_implementation(
        image_name=image_name,
        labels=labels,
        env_names=env_names,
        has_mcp_config=has_mcp_config,
    )

    # 3. Classify composition pattern
    composition = classify_composition(
        image_name=image_name,
        labels=labels,
        has_mcp_config=has_mcp_config,
        connected_networks=connected_networks,
        env_names=env_names,
    )

    # 4. Classify autonomy level
    autonomy = classify_autonomy(
        labels=labels,
        env_names=env_names,
        has_owner=has_owner,
        is_registered=is_registered,
        mounts_docker_socket=mounts_docker_socket,
        mounts_credential_store=mounts_credential_store,
        exposed_ports=exposed_ports,
    )

    # 5. Calculate adoption tier
    adoption_tier, tier_reasoning = calculate_tier(
        agent_type=agent_type.value,
        autonomy=autonomy.value,
        is_registered=is_registered,
        has_owner=has_owner,
        has_mcp_config=has_mcp_config,
        has_oauth_config=has_oauth_config,
        mounts_docker_socket=mounts_docker_socket,
        mounts_credential_store=mounts_credential_store,
        connected_networks=connected_networks,
        exposed_ports=exposed_ports,
        env_names=env_names,
    )

    # 6. Map ASI risks
    asi_risks, asi_descriptions = map_risks(adoption_tier)

    # 7. Score Lethal Trifecta
    trifecta = score_trifecta(
        has_api_key_env=has_api_key_env,
        has_model_endpoint=has_model_endpoint,
        mounts_credential_store=mounts_credential_store,
        mounts_docker_socket=mounts_docker_socket,
        has_mcp_config=has_mcp_config,
        env_names=env_names,
        mounted_volumes=mounted_volumes,
        exposed_ports=exposed_ports,
        labels=labels,
        autonomy=autonomy.value,
    )

    # 8. Build governance flags
    governance_flags = []
    if not is_registered:
        governance_flags.append("UNREGISTERED")
    if not has_owner:
        governance_flags.append("NO_OWNER")
    if not has_agent_scope:
        governance_flags.append("NO_SCOPE")
    if has_hardcoded_secret_env and not has_oauth_config:
        governance_flags.append("STATIC_CREDENTIALS")
    if mounts_docker_socket:
        governance_flags.append("DOCKER_SOCKET_ACCESS")

    # 9. Detect violations
    violations = detect_violations(
        container_id=container_id,
        container_name=container_name,
        is_registered=is_registered,
        has_owner=has_owner,
        mounts_docker_socket=mounts_docker_socket,
        has_hardcoded_secret_env=has_hardcoded_secret_env,
        has_oauth_config=has_oauth_config,
        adoption_tier=adoption_tier,
        trifecta_score=trifecta.score,
        trifecta_rule_of_two=trifecta.rule_of_two_violation,
        autonomy=autonomy.value,
        labels=labels,
        env_names=env_names,
    )

    # 10. Classify alert level
    alert_level, alert_reasons = classify_alert(
        adoption_tier=adoption_tier,
        is_registered=is_registered,
        has_owner=has_owner,
        has_agent_scope_label=has_agent_scope,
        detection_mode=detection_mode_str,
        overall_confidence=overall_confidence,
        trifecta_score=trifecta.score,
        trifecta_rule_of_two=trifecta.rule_of_two_violation,
        mounts_docker_socket=mounts_docker_socket,
        has_hardcoded_secret_env=has_hardcoded_secret_env,
        has_oauth_config=has_oauth_config,
        violations=violations,
    )

    now = datetime.now(timezone.utc).isoformat()

    classified = ClassifiedAgent(
        container_id=container_id,
        container_name=container_name,
        image_name=image_name,
        image_tag=image_tag,
        detection_mode=DetectionMode(detection_mode_str),
        signature_confidence=signature_confidence,
        behavioral_confidence=behavioral_confidence,
        overall_confidence=overall_confidence,
        agent_type=agent_type,
        implementation_pattern=implementation,
        composition_pattern=composition,
        autonomy_level=autonomy,
        adoption_tier=adoption_tier,
        tier_reasoning=tier_reasoning,
        asi_risks=asi_risks,
        asi_risk_descriptions=asi_descriptions,
        trifecta=trifecta,
        is_registered=is_registered,
        is_labeled=is_labeled,
        has_owner=has_owner,
        governance_flags=governance_flags,
        alert_level=alert_level,
        alert_reasons=alert_reasons,
        violations=violations,
        first_detected=now,
        last_seen=now,
        status="active",
        labels=labels,
        env_var_names=env_names,
        exposed_ports=exposed_ports,
        mounted_volumes=mounted_volumes,
        mounts_docker_socket=mounts_docker_socket,
        mounts_credential_store=mounts_credential_store,
        has_api_key_env=has_api_key_env,
        has_hardcoded_secret_env=has_hardcoded_secret_env,
        has_oauth_config=has_oauth_config,
        has_mcp_config=has_mcp_config,
        has_model_endpoint=has_model_endpoint,
    )

    logger.info(
        "Classified %s: type=%s tier=%s autonomy=%s alert=%s trifecta=%d violations=%d",
        container_name, agent_type.value, adoption_tier,
        autonomy.value, alert_level.value, trifecta.score, len(violations),
    )

    return classified
