import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from watcher.src.signals import SignalFingerprint
from watcher.src.scanner import (
    extract_fingerprint,
    is_self_container,
    _match_image_signatures,
    _check_governance_labels,
    _match_env_patterns,
    CREDENTIAL_ENV_PATTERNS,
    MCP_ENV_PATTERNS,
)


def _make_container(
    name="test-container",
    image="python:3.11",
    labels=None,
    env=None,
    exposed_ports=None,
    mounts=None,
    container_id="abc123def456",
):
    container = MagicMock()
    container.id = container_id
    container.name = name
    container.status = "running"
    container.attrs = {
        "Config": {
            "Image": image,
            "Labels": labels or {},
            "Env": env or [],
            "ExposedPorts": {f"{p}/tcp": {} for p in (exposed_ports or [])},
            "Entrypoint": ["python"],
            "Cmd": ["main.py"],
        },
        "HostConfig": {
            "Binds": [],
            "NetworkMode": "bridge",
        },
        "NetworkSettings": {
            "Networks": {"nhidex": {}},
        },
        "Mounts": [{"Source": m, "Destination": m} for m in (mounts or [])],
    }
    return container


class TestSelfContainerDetection:
    def test_self_names_detected(self):
        for name in ["engine", "watcher", "dashboard", "db", "mcp-tools"]:
            container = MagicMock()
            container.name = name
            assert is_self_container(container), f"{name} should be detected as self"

    def test_prefixed_self_names(self):
        container = MagicMock()
        container.name = "nhi-dex-engine-1"
        assert is_self_container(container)

    def test_non_self_container(self):
        container = MagicMock()
        container.name = "my-cool-agent"
        assert not is_self_container(container)


class TestImageSignatures:
    def test_langchain_match(self):
        cat, conf = _match_image_signatures("langchain/langchain:latest")
        assert cat == "orchestration"
        assert conf == 0.7

    def test_mcp_server_match(self):
        cat, conf = _match_image_signatures("my-mcp-server")
        assert cat == "mcp"
        assert conf == 0.7

    def test_coding_agent_match(self):
        cat, conf = _match_image_signatures("claude-code")
        assert cat == "coding"
        assert conf == 0.7

    def test_generic_agent_pattern(self):
        cat, conf = _match_image_signatures("agent-scheduler")
        assert cat == "generic_agent"
        assert conf == 0.5

    def test_no_match(self):
        cat, conf = _match_image_signatures("nginx:latest")
        assert cat is None
        assert conf == 0.0


class TestEnvPatterns:
    def test_api_key_detected(self):
        assert _match_env_patterns(["ANTHROPIC_API_KEY", "PATH"], CREDENTIAL_ENV_PATTERNS)

    def test_mcp_detected(self):
        assert _match_env_patterns(["MCP_TOOL_SERVER"], MCP_ENV_PATTERNS)

    def test_no_match(self):
        assert not _match_env_patterns(["PATH", "HOME"], CREDENTIAL_ENV_PATTERNS)


class TestGovernanceLabels:
    def test_full_governance(self):
        labels = {
            "nhi-dex.agent.name": "test",
            "nhi-dex.agent.owner": "team",
            "nhi-dex.agent.scope": "read-only",
        }
        has_name, has_owner, has_scope, conf = _check_governance_labels(labels)
        assert has_name
        assert has_owner
        assert has_scope
        assert conf == 0.2

    def test_no_governance(self):
        labels = {"maintainer": "someone"}
        has_name, has_owner, has_scope, conf = _check_governance_labels(labels)
        assert not has_name
        assert not has_owner
        assert not has_scope
        assert conf == 0.0


class TestExtractFingerprint:
    def test_agent_with_labels_and_api_key(self):
        container = _make_container(
            name="code-review-agent",
            image="nhi-dex-agent-coding",
            labels={
                "nhi-dex.agent.name": "code-review-agent",
                "nhi-dex.agent.owner": "engineering",
                "nhi-dex.agent.scope": "read-only",
            },
            env=["ANTHROPIC_API_KEY=sk-ant-xxx", "MCP_TOOL_SERVER=http://mcp:3001"],
        )
        fp = extract_fingerprint(container)
        assert fp.container_name == "code-review-agent"
        assert fp.has_agent_name_label
        assert fp.has_owner_label
        assert fp.has_agent_scope_label
        assert fp.has_api_key_env
        assert fp.has_mcp_config
        assert "ANTHROPIC_API_KEY" in fp.env_var_names
        assert "sk-ant-xxx" not in fp.env_var_names
        assert fp.overall_confidence >= 0.3

    def test_shadow_agent_no_labels(self):
        container = _make_container(
            name="rogue-script",
            image="python:3.11",
            env=["ANTHROPIC_API_KEY=sk-ant-xxx", "LLM_BASE_URL=https://api.anthropic.com"],
        )
        fp = extract_fingerprint(container)
        assert not fp.has_agent_name_label
        assert not fp.has_owner_label
        assert fp.has_api_key_env
        assert fp.has_model_endpoint

    def test_docker_socket_mount_detected(self):
        container = _make_container(
            name="dangerous-agent",
            image="agent-runner",
            mounts=["/var/run/docker.sock"],
        )
        fp = extract_fingerprint(container)
        assert fp.mounts_docker_socket

    def test_credential_store_mount_detected(self):
        container = _make_container(
            name="infra-agent",
            image="cloud-ops",
            mounts=["/home/user/.kube/config"],
        )
        fp = extract_fingerprint(container)
        assert fp.mounts_credential_store

    def test_fingerprint_to_dict(self):
        container = _make_container()
        fp = extract_fingerprint(container)
        d = fp.to_dict()
        assert isinstance(d, dict)
        assert "container_id" in d
        assert "detection_mode" in d
        assert "overall_confidence" in d


class TestSignatureDetection:
    def test_high_confidence_known_image(self):
        container = _make_container(
            name="langchain-agent",
            image="langchain/langchain:v0.1",
            labels={"nhi-dex.agent.name": "test"},
            env=["OPENAI_API_KEY=sk-xxx"],
        )
        fp = extract_fingerprint(container)
        assert fp.detection_mode in ("SIGNATURE", "HYBRID")
        assert fp.signature_confidence >= 0.7

    def test_low_confidence_plain_container(self):
        container = _make_container(
            name="web-server",
            image="nginx:latest",
        )
        fp = extract_fingerprint(container)
        assert fp.overall_confidence < 0.3
