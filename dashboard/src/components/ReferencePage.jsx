function Section({ title, children }) {
  return (
    <div className="mb-8">
      <h2 className="text-goldenrod font-bold text-base uppercase tracking-widest mb-4 border-b border-goldenrod/20 pb-2">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Card({ children, className = '' }) {
  return (
    <div className={`bg-[#162040] border border-cream/10 rounded-xl p-4 ${className}`}>
      {children}
    </div>
  );
}

function TierRow({ tier, name, description, color }) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-cream/5 last:border-0">
      <span className={`font-mono font-bold text-xs px-2 py-1 rounded flex-shrink-0 ${color}`}>{tier}</span>
      <div>
        <span className="text-cream font-semibold text-sm">{name}</span>
        <p className="text-cream/50 text-xs mt-0.5">{description}</p>
      </div>
    </div>
  );
}

function ViolationRow({ code, label, description }) {
  return (
    <div className="py-2 border-b border-cream/5 last:border-0">
      <div className="flex items-center gap-2 mb-0.5">
        <span className="font-mono text-xs bg-red-900/40 text-red-300 px-1.5 py-0.5 rounded">{code}</span>
        <span className="text-cream font-semibold text-sm">{label}</span>
      </div>
      <p className="text-cream/50 text-xs">{description}</p>
    </div>
  );
}

function AsiRow({ code, name, description }) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-cream/5 last:border-0">
      <span className="font-mono text-xs bg-red-900/30 text-red-300 px-1.5 py-0.5 rounded flex-shrink-0">{code}</span>
      <div>
        <span className="text-cream font-semibold text-sm">{name}</span>
        <p className="text-cream/50 text-xs mt-0.5">{description}</p>
      </div>
    </div>
  );
}

export function ReferencePage() {
  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">

        {/* How it works */}
        <Section title="How NHI-Dex Works">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Card>
              <div className="text-2xl mb-2">🐳</div>
              <h3 className="text-cream font-bold mb-1">1. Hooks into Docker</h3>
              <p className="text-cream/50 text-sm">NHI-Dex mounts the Docker socket in read-only mode. It can see every running container on your host — it reads metadata only, never file contents or environment variable values.</p>
            </Card>
            <Card>
              <div className="text-2xl mb-2">🔍</div>
              <h3 className="text-cream font-bold mb-1">2. Fingerprints Each Agent</h3>
              <p className="text-cream/50 text-sm">For each container it extracts signals: image name, labels, env var names (names only — never values), exposed ports, volume mounts, and network configuration.</p>
            </Card>
            <Card>
              <div className="text-2xl mb-2">📊</div>
              <h3 className="text-cream font-bold mb-1">3. Classifies & Alerts</h3>
              <p className="text-cream/50 text-sm">The classification engine runs the fingerprint through the OWASP Agentic AI taxonomy, assigns an adoption tier, scores the Lethal Trifecta, detects violations, and streams results here in real time.</p>
            </Card>
          </div>
          <Card className="bg-navy border-goldenrod/20">
            <p className="text-cream/70 text-sm leading-relaxed">
              <span className="text-goldenrod font-semibold">Privacy guarantee:</span> NHI-Dex never reads environment variable values, file contents, or network traffic. It only observes container metadata — the same information visible in <code className="bg-white/10 px-1 rounded text-xs">docker inspect</code>. No data leaves your machine.
            </p>
          </Card>
        </Section>

        {/* Quick Start */}
        <Section title="Quick Start — Run It Yourself">
          <Card>
            <p className="text-cream/60 text-sm mb-4">NHI-Dex runs entirely in Docker. You need Docker Desktop installed and an Anthropic API key (only required if you want the demo agents to make real Claude calls — the monitor itself works without one).</p>
            <div className="space-y-3">
              {[
                { step: '1', label: 'Clone the repo', code: 'git clone https://github.com/your-org/nhi-dex.git && cd nhi-dex' },
                { step: '2', label: 'Add your API key', code: 'cp .env.example .env\n# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...' },
                { step: '3', label: 'Start the stack', code: 'docker compose up -d' },
                { step: '4', label: 'Open the dashboard', code: 'open http://localhost:5173' },
              ].map(({ step, label, code }) => (
                <div key={step} className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-goldenrod text-navy font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{step}</div>
                  <div className="flex-1">
                    <p className="text-cream font-semibold text-sm mb-1">{label}</p>
                    <pre className="bg-navy rounded p-2 text-xs text-cream/70 font-mono overflow-x-auto whitespace-pre-wrap">{code}</pre>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-cream/40 text-xs mt-4">Works on any machine running Docker — local Mac/Windows/Linux or a cloud VM. The dashboard is served at <code className="bg-white/10 px-1 rounded">localhost:5173</code> by default.</p>
          </Card>
        </Section>

        {/* Adoption Tiers */}
        <Section title="Adoption Tiers (AT0 – AT8)">
          <Card>
            <p className="text-cream/50 text-sm mb-4">Tiers classify how deeply an AI agent is integrated into your environment and how much risk it introduces. AT0 is the most dangerous (unregistered shadow AI), AT8 is the most complex (cross-boundary federated agents).</p>
            <TierRow tier="AT0" color="bg-red-700 text-red-100" name="Shadow AI" description="Unregistered agent with no governance labels. Detected purely by behavioral signals. Immediate RED alert." />
            <TierRow tier="AT1" color="bg-gray-600 text-gray-100" name="Basic LLM Integration" description="Simple API call to an LLM. No tools, no memory, minimal risk surface." />
            <TierRow tier="AT2" color="bg-gray-500 text-gray-100" name="Tooled Agent" description="Uses external tools or APIs. Risk increases with scope of tools available." />
            <TierRow tier="AT3" color="bg-purple-700 text-purple-100" name="MCP-Connected Agent" description="Uses the Model Context Protocol for structured tool access. Defined interface reduces some risk." />
            <TierRow tier="AT4" color="bg-blue-700 text-blue-100" name="Coding / Dev Agent" description="Has code execution or repository access. High capability, should be sandboxed." />
            <TierRow tier="AT5" color="bg-green-700 text-green-100" name="Registered Enterprise Agent" description="Properly labeled, registered, governed. Has owner, scope, and audit trail." />
            <TierRow tier="AT6" color="bg-amber-600 text-amber-100" name="External-Access Agent" description="Communicates with systems outside its environment (webhooks, cloud APIs, email). Requires scoped controls." />
            <TierRow tier="AT7" color="bg-orange-700 text-orange-100" name="Advanced / Orchestrating Agent" description="Spawns or directs other agents. Hierarchical risk — a compromise here cascades down." />
            <TierRow tier="AT8" color="bg-red-800 text-red-100" name="Federated / Cross-Boundary" description="Operates across trust boundaries or organizations. Highest complexity and regulatory surface." />
          </Card>
        </Section>

        {/* Lethal Trifecta */}
        <Section title="The Lethal Trifecta & Rule of Two">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <h3 className="text-cream font-bold mb-3">The Three Conditions</h3>
              <p className="text-cream/50 text-sm mb-3">An agent hits the Lethal Trifecta when it has all three of the following simultaneously:</p>
              <div className="space-y-2">
                <div className="flex gap-2 items-start">
                  <span className="text-red-400 mt-0.5">⚡</span>
                  <div>
                    <p className="text-cream font-semibold text-sm">Private Data Access</p>
                    <p className="text-cream/50 text-xs">Has API keys, credential stores, or database connections in its environment.</p>
                  </div>
                </div>
                <div className="flex gap-2 items-start">
                  <span className="text-red-400 mt-0.5">⚡</span>
                  <div>
                    <p className="text-cream font-semibold text-sm">Untrusted Content Exposure</p>
                    <p className="text-cream/50 text-xs">Processes input from external or user-controlled sources (webhooks, customer queries, web content).</p>
                  </div>
                </div>
                <div className="flex gap-2 items-start">
                  <span className="text-red-400 mt-0.5">⚡</span>
                  <div>
                    <p className="text-cream font-semibold text-sm">External Communication</p>
                    <p className="text-cream/50 text-xs">Can send data out of the environment (email, webhooks, cloud APIs, external HTTP calls).</p>
                  </div>
                </div>
              </div>
            </Card>
            <Card>
              <h3 className="text-cream font-bold mb-3">Rule of Two Violation</h3>
              <p className="text-cream/50 text-sm mb-3">A <span className="text-amber-400 font-semibold">Rule of Two Violation</span> triggers when:</p>
              <div className="bg-amber-900/20 border border-amber-600/30 rounded-lg p-3 mb-3">
                <p className="text-amber-200 text-sm font-semibold">Trifecta score = 3/3</p>
                <p className="text-amber-200/70 text-xs mt-1">AND</p>
                <p className="text-amber-200 text-sm font-semibold">Autonomy = semi-autonomous or autonomous</p>
              </div>
              <p className="text-cream/50 text-sm">This means the agent can access sensitive data, process adversarial input, exfiltrate externally — and it does so without meaningful human oversight. This is the highest-risk combination NHI-Dex detects.</p>
            </Card>
          </div>
        </Section>

        {/* Alert Levels */}
        <Section title="Alert Levels">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-red-700/40">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full bg-red-500 pulse-red inline-block" />
                <span className="text-red-400 font-bold">RED — Immediate Action</span>
              </div>
              <p className="text-cream/50 text-sm">AT0 shadow AI, Rule of Two violation, Docker socket access, static credentials at high tiers, or critical violations. Requires immediate review.</p>
            </Card>
            <Card className="border-amber-600/40">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full bg-amber-400 inline-block" />
                <span className="text-amber-400 font-bold">YELLOW — Review Needed</span>
              </div>
              <p className="text-cream/50 text-sm">Behavioral-only detection (low confidence), partial trifecta score (2/3), API key without OAuth, medium/high severity violations, or incomplete registration.</p>
            </Card>
            <Card className="border-green-700/40">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
                <span className="text-green-400 font-bold">GREEN — Compliant</span>
              </div>
              <p className="text-cream/50 text-sm">Agent is registered, labeled, governed, and no critical signals detected. Continue to monitor for changes.</p>
            </Card>
          </div>
        </Section>

        {/* Detection Modes */}
        <Section title="Detection Modes">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <p className="text-goldenrod font-bold mb-1">SIGNATURE</p>
              <p className="text-cream/50 text-sm">Pattern matching against known AI framework image names, labels, and environment variable names. High confidence when matched. Examples: <code className="bg-white/10 px-1 rounded text-xs">langchain</code>, <code className="bg-white/10 px-1 rounded text-xs">openai</code>, <code className="bg-white/10 px-1 rounded text-xs">ANTHROPIC_API_KEY</code>.</p>
            </Card>
            <Card>
              <p className="text-goldenrod font-bold mb-1">BEHAVIORAL</p>
              <p className="text-cream/50 text-sm">Inference from observable behavior: network configuration, port exposure, volume mounts, credential store access. Used when no direct signature match exists. Medium confidence.</p>
            </Card>
            <Card>
              <p className="text-goldenrod font-bold mb-1">HYBRID</p>
              <p className="text-cream/50 text-sm">Both signature and behavioral signals detected. Highest confidence classification. Most agents in a real environment will fall here once they have both a known image and runtime signals.</p>
            </Card>
          </div>
        </Section>

        {/* Violation Types */}
        <Section title="Violation Types">
          <Card>
            <ViolationRow code="UNREGISTERED_AGENT" label="Unregistered Agent" description="Container has no nhi-dex governance labels. Any AI agent running without registration is a governance gap — you don't know what it has access to." />
            <ViolationRow code="DOCKER_SOCKET_ACCESS" label="Docker Socket Access" description="Agent has mounted /var/run/docker.sock. This gives it the ability to control other containers on the host — a significant privilege escalation vector." />
            <ViolationRow code="TRIFECTA_VIOLATION" label="Lethal Trifecta Violation" description="All three trifecta conditions met with semi/autonomous execution. The highest-risk configuration NHI-Dex can detect." />
            <ViolationRow code="STATIC_CREDENTIALS" label="Static Credentials" description="Agent at AT5+ has hardcoded API keys or credentials without OAuth. Static credentials don't rotate and can't be scoped." />
            <ViolationRow code="EXTERNAL_COMM_UNSCOPED" label="External Communication Unscoped" description="Agent has external communication capability but is marked as read-only scope. Scope and capability are mismatched." />
            <ViolationRow code="PRIVILEGE_ESCALATION" label="Privilege Escalation" description="Agent has capabilities that exceed its declared scope or tier — e.g. a personal agent with infrastructure access." />
            <ViolationRow code="SCOPE_EXCEEDED" label="Scope Exceeded" description="Agent is operating outside its declared operational boundary based on tool access and environment signals." />
            <ViolationRow code="CROSS_ENVIRONMENT" label="Cross-Environment Access" description="Agent is accessing resources across environment boundaries (e.g. dev agent touching prod credentials)." />
          </Card>
        </Section>

        {/* ASI Risk Codes */}
        <Section title="ASI Risk Codes (OWASP Agentic AI)">
          <Card>
            <p className="text-cream/50 text-sm mb-4">Risk codes from the OWASP Agentic AI Security Initiative. Each adoption tier maps to a set of applicable codes. The heatmap on the monitor tab shows which codes are active across your fleet.</p>
            <AsiRow code="ASI01" name="Memory Poisoning" description="Adversarial content injected into agent memory or context window persists across sessions and influences future decisions." />
            <AsiRow code="ASI02" name="Tool Misuse" description="Agent uses legitimate tools in unintended ways, exceeding authorized scope or chaining tools to produce unauthorized outcomes." />
            <AsiRow code="ASI03" name="Authentication Bypass" description="Agent exploits identity or credential weaknesses to gain access beyond its authorized permissions." />
            <AsiRow code="ASI04" name="Prompt Injection" description="Untrusted content in the agent's input manipulates its behavior — the AI equivalent of SQL injection." />
            <AsiRow code="ASI05" name="Data Exfiltration" description="Agent leaks sensitive data through covert channels, encoded outputs, or unauthorized external calls." />
            <AsiRow code="ASI06" name="Scope Creep" description="Agent progressively acquires resources, permissions, or capabilities beyond what its task requires." />
            <AsiRow code="ASI07" name="Uncontrolled Execution" description="Agent takes irreversible real-world actions (sends emails, modifies files, calls APIs) without human review." />
            <AsiRow code="ASI08" name="Cascading Failure" description="In multi-agent systems, one compromised or misbehaving agent propagates failures to downstream agents." />
            <AsiRow code="ASI09" name="Shadow AI" description="Unsanctioned AI agents operating outside organizational awareness, governance, or security controls." />
            <AsiRow code="ASI10" name="Cross-Boundary Operation" description="Agent operates across organizational or trust boundaries without appropriate authorization and audit trails." />
          </Card>
        </Section>

        {/* Glossary */}
        <Section title="Key Terms">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { term: 'NHI (Non-Human Identity)', def: 'Any credential, token, API key, or service account used by a machine rather than a person. AI agents are a new and fast-growing class of NHI.' },
              { term: 'MCP (Model Context Protocol)', def: 'An open standard by Anthropic for connecting AI models to external tools and data sources in a structured, auditable way.' },
              { term: 'SSE (Server-Sent Events)', def: 'How the dashboard receives live updates from the engine. A persistent HTTP connection where the server pushes events as they happen — no polling needed.' },
              { term: 'OWASP', def: 'Open Worldwide Application Security Project. The Agentic AI Security Initiative (ASI) is their framework for classifying risks specific to AI agents.' },
              { term: 'Docker Socket', def: '/var/run/docker.sock — the Unix socket that gives a process control over the Docker daemon. Mounting it in a container is a high-privilege operation.' },
              { term: 'Governance Labels', def: 'Docker labels prefixed with nhi-dex.agent.* that identify a container as a known, registered AI agent with declared scope, owner, and type.' },
              { term: 'Adoption Tier', def: 'NHI-Dex\'s classification scale (AT0–AT8) measuring how deeply an AI agent is integrated into your environment and what risk surface it presents.' },
              { term: 'Fingerprint', def: 'The set of observable signals NHI-Dex extracts from a container: image name, labels, env var names, ports, mounts. The raw input to classification.' },
            ].map(({ term, def }) => (
              <Card key={term}>
                <p className="text-goldenrod font-semibold text-sm mb-1">{term}</p>
                <p className="text-cream/50 text-sm">{def}</p>
              </Card>
            ))}
          </div>
        </Section>

        <div className="text-center text-cream/20 text-xs pb-8">
          NHI-Dex · KAMO Consulting / KAMO Tune AI, LLC · Apache 2.0 License
        </div>

      </div>
    </div>
  );
}
