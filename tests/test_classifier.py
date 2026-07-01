import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.src.classifier import run_classification_pipeline
from engine.src.models import AlertLevel


def _make_detection(**overrides):
    base = {
        "container_id": "abc123",
        "container_name": "test-agent",
        "image_name": "python:3.11",
        "image_tag": "latest",
        "labels": {},
        "has_owner_label": False,
        "has_agent_name_label": False,
        "has_agent_scope_label": False,
        "env_var_names": [],
        "has_api_key_env": False,
        "has_hardcoded_secret_env": False,
        "has_oauth_config": False,
        "has_mcp_config": False,
        "has_model_endpoint": False,
        "exposed_ports": [],
        "mounted_volumes": [],
        "mounts_docker_socket": False,
        "mounts_credential_store": False,
        "network_mode": "bridge",
        "connected_networks": ["nhidex"],
        "entrypoint": "",
        "command": "",
        "outbound_domains": [],
        "api_call_rate": 0.0,
        "mcp_protocol_detected": False,
        "llm_api_traffic_detected": False,
        "detection_mode": "SIGNATURE",
        "signature_confidence": 0.5,
        "behavioral_confidence": 0.0,
        "overall_confidence": 0.5,
    }
    base.update(overrides)
    return base


class TestCodingAgent:
    def test_classification(self):
        detection = _make_detection(
            container_name="code-review-agent",
            image_name="nhi-dex-agent-coding",
            labels={
                "nhi-dex.agent.name": "code-review-agent",
                "nhi-dex.agent.type": "coding",
                "nhi-dex.agent.owner": "engineering-team",
                "nhi-dex.agent.scope": "code-review-read-only",
            },
            has_owner_label=True,
            has_agent_name_label=True,
            has_agent_scope_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "GITHUB_TOKEN", "MCP_TOOL_SERVER"],
            has_api_key_env=True,
            has_mcp_config=True,
        )
        result = run_classification_pipeline(detection)
        assert result.agent_type.value == "coding"
        assert result.adoption_tier == "AT4"
        assert result.alert_level == AlertLevel.GREEN


class TestEnterpriseAgent:
    def test_classification(self):
        detection = _make_detection(
            container_name="data-analyst-agent",
            image_name="nhi-dex-agent-enterprise",
            labels={
                "nhi-dex.agent.name": "data-analyst-agent",
                "nhi-dex.agent.type": "enterprise",
                "nhi-dex.agent.owner": "platform-team",
                "nhi-dex.agent.scope": "read-only-analytics",
                "nhi-dex.agent.autonomy": "supervised",
            },
            has_owner_label=True,
            has_agent_name_label=True,
            has_agent_scope_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "OAUTH_CLIENT_ID", "MCP_TOOL_SERVER"],
            has_api_key_env=True,
            has_oauth_config=True,
            has_mcp_config=True,
        )
        result = run_classification_pipeline(detection)
        assert result.agent_type.value == "enterprise"
        assert result.adoption_tier == "AT5"
        assert result.autonomy_level.value == "supervised"
        assert result.alert_level == AlertLevel.GREEN


class TestClientFacingAgent:
    def test_classification(self):
        detection = _make_detection(
            container_name="customer-support-agent",
            image_name="nhi-dex-agent-client-facing",
            labels={
                "nhi-dex.agent.name": "customer-support-agent",
                "nhi-dex.agent.type": "client-facing",
                "nhi-dex.agent.owner": "support-team",
                "nhi-dex.agent.scope": "customer-query-response",
            },
            has_owner_label=True,
            has_agent_name_label=True,
            has_agent_scope_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "MCP_TOOL_SERVER", "WEBHOOK_URL"],
            has_api_key_env=True,
            has_mcp_config=True,
        )
        result = run_classification_pipeline(detection)
        assert result.agent_type.value == "client-facing"
        assert result.adoption_tier == "AT5"


class TestInfraAgent:
    def test_classification(self):
        detection = _make_detection(
            container_name="cloud-ops-agent",
            image_name="nhi-dex-agent-infra",
            labels={
                "nhi-dex.agent.name": "cloud-ops-agent",
                "nhi-dex.agent.type": "infrastructure",
                "nhi-dex.agent.owner": "platform-ops",
                "nhi-dex.agent.scope": "cloud-status-readonly",
            },
            has_owner_label=True,
            has_agent_name_label=True,
            has_agent_scope_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "MCP_TOOL_SERVER", "AWS_REGION", "KUBECONFIG"],
            has_api_key_env=True,
            has_mcp_config=True,
            mounts_credential_store=True,
            mounted_volumes=["/home/user/.kube/config"],
        )
        result = run_classification_pipeline(detection)
        assert result.agent_type.value == "infrastructure"
        assert result.adoption_tier == "AT6"


class TestShadowAgent:
    def test_at0_classification(self):
        detection = _make_detection(
            container_name="rogue-script",
            image_name="python:3.11",
            labels={},
            has_owner_label=False,
            has_agent_name_label=False,
            has_agent_scope_label=False,
            env_var_names=["ANTHROPIC_API_KEY", "LLM_BASE_URL"],
            has_api_key_env=True,
            has_hardcoded_secret_env=True,
            has_model_endpoint=True,
            exposed_ports=[8888],
        )
        result = run_classification_pipeline(detection)
        assert result.adoption_tier == "AT0"
        assert result.alert_level == AlertLevel.RED
        assert not result.is_registered
        assert any(v.violation_type.value == "UNREGISTERED_AGENT" for v in result.violations)

    def test_shadow_always_has_violations(self):
        detection = _make_detection(
            container_name="shadow",
            labels={},
            has_api_key_env=True,
        )
        result = run_classification_pipeline(detection)
        assert result.adoption_tier == "AT0"
        assert len(result.violations) > 0


class TestTrifecta:
    def test_full_trifecta(self):
        detection = _make_detection(
            container_name="dangerous-agent",
            labels={"nhi-dex.agent.name": "test", "nhi-dex.agent.type": "client-facing"},
            has_agent_name_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "DATABASE_URL", "WEBHOOK_URL"],
            has_api_key_env=True,
            exposed_ports=[8080, 9090],
        )
        result = run_classification_pipeline(detection)
        assert result.trifecta.score >= 2

    def test_zero_trifecta(self):
        detection = _make_detection(
            container_name="safe-agent",
            labels={
                "nhi-dex.agent.name": "safe",
                "nhi-dex.agent.owner": "team",
                "nhi-dex.agent.autonomy": "supervised",
            },
            has_agent_name_label=True,
            has_owner_label=True,
        )
        result = run_classification_pipeline(detection)
        assert result.trifecta.score == 0


class TestViolations:
    def test_docker_socket_violation(self):
        detection = _make_detection(
            container_name="socket-agent",
            labels={"nhi-dex.agent.name": "test"},
            has_agent_name_label=True,
            mounts_docker_socket=True,
        )
        result = run_classification_pipeline(detection)
        assert any(v.violation_type.value == "DOCKER_SOCKET_ACCESS" for v in result.violations)
        assert result.alert_level == AlertLevel.RED


class TestAlertLevels:
    def test_green_fully_governed(self):
        detection = _make_detection(
            container_name="good-agent",
            labels={
                "nhi-dex.agent.name": "good",
                "nhi-dex.agent.type": "coding",
                "nhi-dex.agent.owner": "team",
                "nhi-dex.agent.scope": "read-only",
            },
            has_agent_name_label=True,
            has_owner_label=True,
            has_agent_scope_label=True,
            env_var_names=["ANTHROPIC_API_KEY", "GITHUB_TOKEN", "MCP_TOOL_SERVER"],
            has_api_key_env=True,
            has_mcp_config=True,
        )
        result = run_classification_pipeline(detection)
        assert result.alert_level == AlertLevel.GREEN

    def test_red_shadow_ai(self):
        detection = _make_detection(
            container_name="shadow",
            labels={},
            has_api_key_env=True,
        )
        result = run_classification_pipeline(detection)
        assert result.alert_level == AlertLevel.RED
