from ..models import TaxonomyResult

FRAMEWORK_IMAGES = ["langchain", "langgraph", "autogen", "crewai", "dspy", "google-adk"]
PLATFORM_IMAGES = ["copilot", "amazon-q", "bedrock-agent", "vertex-ai", "einstein", "agentforce"]
LLM_INFERENCE_IMAGES = ["ollama", "vllm", "llama-cpp", "tgi"]


def classify_implementation(
    image_name: str,
    labels: dict,
    env_names: list[str],
    has_mcp_config: bool,
) -> TaxonomyResult:
    lower_image = image_name.lower()

    for pattern in FRAMEWORK_IMAGES:
        if pattern in lower_image:
            return TaxonomyResult(
                value="framework",
                confidence=0.85,
                reasoning=f"Image matches known framework: {pattern}",
            )

    for pattern in PLATFORM_IMAGES:
        if pattern in lower_image:
            return TaxonomyResult(
                value="platform",
                confidence=0.85,
                reasoning=f"Image matches known platform: {pattern}",
            )

    for pattern in LLM_INFERENCE_IMAGES:
        if pattern in lower_image:
            return TaxonomyResult(
                value="library",
                confidence=0.7,
                reasoning=f"Image matches LLM inference server: {pattern}",
            )

    label_values = " ".join(f"{k} {v}" for k, v in labels.items()).lower()

    if any(fw in label_values for fw in ["langchain", "autogen", "crewai", "dspy"]):
        return TaxonomyResult(value="framework", confidence=0.75, reasoning="Labels reference known framework")

    if any(p in label_values for p in ["platform", "saas", "managed"]):
        return TaxonomyResult(value="platform", confidence=0.6, reasoning="Labels suggest platform-based implementation")

    if any(p in label_values for p in ["low-code", "no-code", "visual", "workflow"]):
        return TaxonomyResult(value="low-code", confidence=0.6, reasoning="Labels suggest low-code implementation")

    env_upper = [e.upper() for e in env_names]
    has_sdk = any("ANTHROPIC" in e or "OPENAI" in e for e in env_upper)

    if has_sdk and not has_mcp_config:
        return TaxonomyResult(
            value="library",
            confidence=0.6,
            reasoning="Direct SDK usage detected (API key, no framework indicators)",
        )

    if has_sdk and has_mcp_config:
        return TaxonomyResult(
            value="custom",
            confidence=0.55,
            reasoning="SDK + MCP configuration suggests custom implementation",
        )

    return TaxonomyResult(value="unknown", confidence=0.0, reasoning="Insufficient signals for implementation classification")
