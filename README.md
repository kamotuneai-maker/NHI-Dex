<div align="center">
  <img src="dashboard/public/NHI-Dex 2.png" alt="NHI-Dex Logo" width="180" />

  <h1>NHI-Dex</h1>
  <p><strong>Non-Human Identity detection, classification, and monitoring for AI agents running in Docker.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" />
    <img src="https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=black" alt="React" />
    <img src="https://img.shields.io/badge/OWASP-Agentic%20AI-red" alt="OWASP" />
  </p>
</div>

---

## What is NHI-Dex?

Most organizations have no idea how many AI agents are running in their environment, what they have access to, or whether they follow any governance rules. **NHI-Dex fixes that.**

Inspired by the Pokédex, NHI-Dex scans your Docker environment in real time and generates a **Dex Card** for every AI agent it finds — known or unknown. Each card tells you what the agent is, what it has access to, how autonomous it is, and whether it poses a security risk.

It hooks into the Docker socket in **read-only mode**. It never reads environment variable values, file contents, or network traffic — only the same metadata visible in `docker inspect`. No data leaves your machine.

---

## Features

- **Real-time detection** — subscribes to Docker events and classifies new agents the moment they start
- **OWASP Agentic AI taxonomy** — classifies every agent across four dimensions: type, implementation, composition, and autonomy
- **Adoption Tiers AT0–AT8** — from unregistered Shadow AI (AT0) to federated cross-boundary agents (AT8)
- **Lethal Trifecta scoring** — detects the dangerous combination of private data access + untrusted content exposure + external communication
- **Rule of Two violation** — flags autonomous agents that hit all three trifecta conditions simultaneously
- **Shadow AI detection** — catches unregistered, unlabeled agents running outside your governance controls
- **ASI risk codes** — maps each agent to applicable OWASP ASI01–ASI10 risk codes
- **Live dashboard** — React UI with Dex Cards, fleet summary, tier distribution charts, autonomy spectrum, and ASI risk heatmap
- **SSE event feed** — real-time violation and alert stream at the bottom of the dashboard
- **Export** — download your full agent inventory as JSON or CSV at any time
- **PostgreSQL persistence** — full agent, alert, and violation history with graceful in-memory fallback
- **Reference tab** — built-in glossary covering all terms, tiers, violation types, and a self-hosting quick-start guide

---

## Quick Start

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) and an [Anthropic API key](https://console.anthropic.com/) (only required for the demo agents — the monitor itself runs without one).

```bash
# 1. Clone the repo
git clone https://github.com/kamotuneai-maker/NHI-Dex.git
cd NHI-Dex

# 2. Configure environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Start the full stack
docker compose up -d

# 4. Open the dashboard
open http://localhost:5173
```

That's it. Within 30 seconds you'll see five demo agents populate the dashboard.

To stop and wipe all data:
```bash
docker compose down -v
```

To restart without losing history:
```bash
docker compose down && docker compose up -d
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Environment                     │
│                                                         │
│  [shadow-agent]  [coding-agent]  [enterprise-agent]     │
│  [client-facing-agent]  [infra-agent]  [mcp-tools]     │
│                          │                              │
│          /var/run/docker.sock (read-only)               │
└──────────────────────────┼──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Watcher   │  scans · fingerprints
                    └──────┬──────┘
                           │ POST /api/detect
                    ┌──────▼──────────┐
                    │    Engine       │  classifies · scores
                    │   (FastAPI)     │  violations · alerts
                    └──────┬──────────┘
                    │             │
              ┌─────▼─────┐  SSE stream
              │ PostgreSQL │  /api/events
              └───────────┘       │
                            ┌─────▼──────┐
                            │ Dashboard  │  React · Recharts
                            │ :5173      │  live Dex Cards
                            └────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `engine` | 8000 | FastAPI classification engine, SSE stream, REST API |
| `dashboard` | 5173 (dev) / 3000 (Docker) | React dashboard |
| `mcp-tools` | 3001 | Demo MCP tool server (8 tools) |
| `db` | — | PostgreSQL 16, internal only |
| `watcher` | — | Docker socket observer, no exposed port |

---

## How Detection Works

1. **Watcher** mounts `/var/run/docker.sock` read-only and subscribes to Docker events
2. On each `start` event it calls `docker inspect` and extracts a **SignalFingerprint**: image name, label presence, env var *names* (never values), exposed ports, volume mounts, network config
3. The fingerprint is scored against **signature patterns** (known AI framework image names, env var names) and **behavioral signals** (credential stores, socket mounts, multi-port exposure)
4. The **Engine** runs the fingerprint through the full classification pipeline:
   - Agent type (enterprise, coding, client-facing, infrastructure, personal/shadow)
   - Implementation pattern (framework, library, platform, low-code, custom)
   - Composition pattern (standalone, pipeline, hierarchical, mesh)
   - Autonomy level (supervised, semi-autonomous, autonomous)
   - Adoption Tier (AT0–AT8)
   - Trifecta score and Rule of Two check
   - Violation detection (8 violation types)
   - Alert level (RED / YELLOW / GREEN)
5. Results are stored in Postgres and broadcast via **Server-Sent Events** to the dashboard

---

## Demo Agents

NHI-Dex ships with five demo agents that deliberately exhibit different risk profiles:

| Agent | Tier | Alert | What it demonstrates |
|-------|------|-------|----------------------|
| `shadow-agent` | AT0 | 🔴 RED    | No governance labels, unregistered, direct Claude API calls — classic Shadow AI |
| `coding-agent` | AT4 | 🟡 YELLOW    | GitHub token, code review tools, semi-autonomous |
| `enterprise-agent` | AT5 | 🟢 GREEN    | Fully registered, labeled, OAuth, HITL gate — the gold standard |
| `client-facing-agent` | AT5 | 🔴 RED    | Processes untrusted user input + has external communication → Trifecta violation |
| `infra-agent` | AT6 | 🟡 YELLOW    | AWS + Kubernetes access, can trigger email sends via MCP |

---

## Governing Your Own Agents

To register a real agent with NHI-Dex, add these Docker labels to its container:

```yaml
labels:
  nhi-dex.agent.type: "enterprise"          # enterprise | coding | client-facing | infrastructure | personal
  nhi-dex.agent.name: "my-agent"
  nhi-dex.agent.owner: "platform-team"
  nhi-dex.agent.scope: "readonly"           # readonly | readwrite | admin
  nhi-dex.agent.autonomy: "supervised"      # supervised | semi-autonomous | autonomous
  nhi-dex.agent.registered: "true"
```

Labeled agents are automatically classified as registered, which improves their tier score and reduces alert level.

---

## API

The engine exposes a REST API on port 8000:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health and storage mode |
| `GET /api/agents` | All active classified agents |
| `GET /api/agents/{id}` | Single agent by container ID |
| `GET /api/summary` | Fleet-level counts and tier distribution |
| `GET /api/violations` | All detected violations |
| `GET /api/alerts` | Alert history |
| `GET /api/events` | SSE stream of real-time events |

---

## Contributing

NHI-Dex is a work in progress and community feedback shapes where it goes next. Ideas for contribution:

- Additional image signature patterns for new AI frameworks
- Kubernetes support (read from pod metadata instead of Docker socket)
- New violation detection rules
- Custom sprite submissions for agent types
- Multi-host / fleet aggregation

Please open an issue to discuss before submitting a large PR.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

Built by [KAMO Consulting / KAMO Tune AI, LLC](https://kamotuneai.com).

---

<div align="center">
  <sub>If you find Shadow AI running in your environment, you're welcome.</sub>
</div>
