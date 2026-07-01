ASI_RISK_MAP = {
    "ASI01": "Prompt Injection",
    "ASI02": "Sensitive Information Disclosure",
    "ASI03": "Supply Chain Vulnerabilities",
    "ASI04": "Output Handling",
    "ASI05": "Insecure Plugins/Tools",
    "ASI06": "Excessive Permissions",
    "ASI07": "Identity and Access Mismanagement",
    "ASI08": "Vector/Embedding Weaknesses",
    "ASI09": "Misinformation/Hallucination",
    "ASI10": "Unbounded Consumption",
}

TIER_RISK_MATRIX: dict[str, list[str]] = {
    "AT0": ["ASI01", "ASI02", "ASI06", "ASI07", "ASI09"],
    "AT1": ["ASI01", "ASI09"],
    "AT2": ["ASI01", "ASI02", "ASI04", "ASI09"],
    "AT3": ["ASI01", "ASI02", "ASI04", "ASI05", "ASI09"],
    "AT4": ["ASI01", "ASI02", "ASI03", "ASI04", "ASI05", "ASI06"],
    "AT5": ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06", "ASI07"],
    "AT6": ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06", "ASI07", "ASI10"],
    "AT7": ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06", "ASI07", "ASI08", "ASI10"],
    "AT8": ["ASI01", "ASI02", "ASI03", "ASI04", "ASI05", "ASI06", "ASI07", "ASI08", "ASI09", "ASI10"],
}


def map_risks(tier: str) -> tuple[list[str], dict[str, str]]:
    risk_codes = TIER_RISK_MATRIX.get(tier, TIER_RISK_MATRIX["AT0"])
    descriptions = {code: ASI_RISK_MAP[code] for code in risk_codes if code in ASI_RISK_MAP}
    return risk_codes, descriptions
