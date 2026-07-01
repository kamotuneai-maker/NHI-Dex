from ..models import TaxonomyResult

CODING_SIGNALS = {
    "images": ["claude-code", "codex", "devin", "cursor", "aider", "cline", "open-interpreter", "sweep"],
    "labels": ["coding", "code-review", "code-gen", "developer"],
    "env": ["GITHUB_TOKEN", "GITLAB_TOKEN", "BITBUCKET", "CODE_REVIEW"],
    "tools": ["code_review", "shell_exec", "git_"],
}

ENTERPRISE_SIGNALS = {
    "images": ["bedrock-agent", "vertex-ai", "einstein", "agentforce"],
    "labels": ["enterprise", "business", "analytics", "data-analyst"],
    "env": ["OAUTH_CLIENT_ID", "SAML", "SSO_", "LDAP"],
    "tools": ["db_query", "file_read", "analytics"],
}

CLIENT_FACING_SIGNALS = {
    "images": ["chatbot", "support-agent", "customer-"],
    "labels": ["client-facing", "customer", "support", "chatbot", "helpdesk"],
    "env": ["WEBHOOK_URL", "CRM_", "ZENDESK", "INTERCOM", "FRESHDESK"],
    "tools": ["customer_query", "ticket_"],
}

INFRASTRUCTURE_SIGNALS = {
    "images": ["infra-agent", "cloud-ops", "k8s-agent", "terraform-"],
    "labels": ["infrastructure", "infra", "ops", "devops", "sre", "cloud"],
    "env": ["AWS_REGION", "KUBECONFIG", "AZURE_", "GCP_", "TERRAFORM_", "KUBECTL"],
    "tools": ["cloud_status", "deploy_", "scale_"],
}

PERSONAL_SIGNALS = {
    "labels": ["personal", "assistant", "helper"],
    "env": ["LLM_BASE_URL"],
}


def _label_match(labels: dict, keywords: list[str]) -> float:
    score = 0.0
    for key, value in labels.items():
        lower = f"{key} {value}".lower()
        for kw in keywords:
            if kw in lower:
                score += 0.3
    return min(score, 0.9)


def _env_match(env_names: list[str], patterns: list[str]) -> float:
    score = 0.0
    for name in env_names:
        upper = name.upper()
        for pattern in patterns:
            if pattern in upper:
                score += 0.15
    return min(score, 0.6)


def _image_match(image_name: str, patterns: list[str]) -> float:
    lower = image_name.lower()
    for pattern in patterns:
        if pattern in lower:
            return 0.5
    return 0.0


def classify_agent_type(
    image_name: str,
    labels: dict,
    env_names: list[str],
    has_oauth: bool,
    mounts_credential_store: bool,
) -> TaxonomyResult:
    scores: dict[str, tuple[float, str]] = {}

    # Coding
    c = _image_match(image_name, CODING_SIGNALS["images"])
    c += _label_match(labels, CODING_SIGNALS["labels"])
    c += _env_match(env_names, CODING_SIGNALS["env"])
    if c > 0:
        scores["coding"] = (min(c, 1.0), "Matches coding agent signatures (IDE tools, code review, GitHub tokens)")

    # Enterprise
    e = _image_match(image_name, ENTERPRISE_SIGNALS["images"])
    e += _label_match(labels, ENTERPRISE_SIGNALS["labels"])
    e += _env_match(env_names, ENTERPRISE_SIGNALS["env"])
    if has_oauth:
        e += 0.2
    if e > 0:
        scores["enterprise"] = (min(e, 1.0), "Matches enterprise agent signatures (OAuth, analytics, business tools)")

    # Client-facing
    cf = _image_match(image_name, CLIENT_FACING_SIGNALS["images"])
    cf += _label_match(labels, CLIENT_FACING_SIGNALS["labels"])
    cf += _env_match(env_names, CLIENT_FACING_SIGNALS["env"])
    if cf > 0:
        scores["client-facing"] = (min(cf, 1.0), "Matches client-facing signatures (webhooks, CRM, customer tools)")

    # Infrastructure
    i = _image_match(image_name, INFRASTRUCTURE_SIGNALS["images"])
    i += _label_match(labels, INFRASTRUCTURE_SIGNALS["labels"])
    i += _env_match(env_names, INFRASTRUCTURE_SIGNALS["env"])
    if mounts_credential_store:
        i += 0.2
    if i > 0:
        scores["infrastructure"] = (min(i, 1.0), "Matches infrastructure signatures (cloud APIs, k8s, credential stores)")

    # Personal
    p = _label_match(labels, PERSONAL_SIGNALS.get("labels", []))
    p += _env_match(env_names, PERSONAL_SIGNALS.get("env", []))
    if p > 0:
        scores["personal"] = (min(p, 1.0), "Matches personal/shadow agent signatures")

    if not scores:
        return TaxonomyResult(value="unknown", confidence=0.0, reasoning="No agent type signals detected")

    best_type = max(scores, key=lambda k: scores[k][0])
    confidence, reasoning = scores[best_type]
    return TaxonomyResult(value=best_type, confidence=round(confidence, 2), reasoning=reasoning)
