-- NHI-Dex Database Schema
-- Tables are auto-created by SQLAlchemy, but this file serves as reference
-- and can be used for manual initialization if needed.

CREATE TABLE IF NOT EXISTS agents (
    container_id VARCHAR(12) PRIMARY KEY,
    container_name VARCHAR(255) NOT NULL,
    image_name VARCHAR(255),
    image_tag VARCHAR(64),
    classification_json TEXT NOT NULL,
    adoption_tier VARCHAR(4),
    alert_level VARCHAR(10),
    agent_type VARCHAR(32),
    autonomy_level VARCHAR(20),
    detection_mode VARCHAR(12),
    overall_confidence VARCHAR(10),
    status VARCHAR(16) DEFAULT 'active',
    first_detected TIMESTAMPTZ,
    last_seen TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agents_tier ON agents(adoption_tier);
CREATE INDEX IF NOT EXISTS idx_agents_alert ON agents(alert_level);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    container_id VARCHAR(12),
    container_name VARCHAR(255),
    level VARCHAR(10),
    reasons_json TEXT,
    tier VARCHAR(4),
    timestamp TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level);
CREATE INDEX IF NOT EXISTS idx_alerts_container ON alerts(container_id);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);

CREATE TABLE IF NOT EXISTS violations (
    id SERIAL PRIMARY KEY,
    container_id VARCHAR(12),
    container_name VARCHAR(255),
    violation_type VARCHAR(32),
    severity VARCHAR(10),
    description TEXT,
    asi_codes_json TEXT,
    nhi_codes_json TEXT,
    timestamp TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_violations_type ON violations(violation_type);
CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity);
CREATE INDEX IF NOT EXISTS idx_violations_container ON violations(container_id);
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
