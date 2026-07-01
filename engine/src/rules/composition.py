from ..models import TaxonomyResult

MULTI_AGENT_IMAGES = ["autogen", "crewai", "langgraph"]
PIPELINE_IMAGES = ["airflow", "prefect", "dagster", "step-functions"]


def classify_composition(
    image_name: str,
    labels: dict,
    has_mcp_config: bool,
    connected_networks: list[str],
    env_names: list[str],
) -> TaxonomyResult:
    lower_image = image_name.lower()

    for pattern in MULTI_AGENT_IMAGES:
        if pattern in lower_image:
            return TaxonomyResult(
                value="hierarchical",
                confidence=0.8,
                reasoning=f"Image matches multi-agent framework: {pattern}",
            )

    for pattern in PIPELINE_IMAGES:
        if pattern in lower_image:
            return TaxonomyResult(
                value="pipeline",
                confidence=0.8,
                reasoning=f"Image matches pipeline orchestrator: {pattern}",
            )

    label_values = " ".join(f"{k} {v}" for k, v in labels.items()).lower()

    if any(kw in label_values for kw in ["mesh", "swarm", "distributed"]):
        return TaxonomyResult(value="mesh", confidence=0.7, reasoning="Labels indicate mesh/distributed composition")

    if any(kw in label_values for kw in ["pipeline", "chain", "sequential", "workflow"]):
        return TaxonomyResult(value="pipeline", confidence=0.7, reasoning="Labels indicate pipeline composition")

    if any(kw in label_values for kw in ["hierarchical", "supervisor", "orchestrator", "multi-agent"]):
        return TaxonomyResult(value="hierarchical", confidence=0.7, reasoning="Labels indicate hierarchical composition")

    network_count = len(connected_networks)
    env_has_agent_refs = sum(1 for e in env_names if "AGENT" in e.upper() or "WORKER" in e.upper())

    if env_has_agent_refs >= 2 or network_count >= 3:
        return TaxonomyResult(
            value="pipeline",
            confidence=0.5,
            reasoning="Multiple agent references or network connections suggest pipeline",
        )

    if has_mcp_config:
        return TaxonomyResult(
            value="standalone",
            confidence=0.7,
            reasoning="Single agent with MCP tool access (standalone + tools)",
        )

    return TaxonomyResult(
        value="standalone",
        confidence=0.6,
        reasoning="No multi-agent or pipeline indicators — defaulting to standalone",
    )
