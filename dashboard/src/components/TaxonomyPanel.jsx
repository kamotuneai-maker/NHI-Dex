function ConfidenceBar({ label, value, reasoning }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs mb-0.5">
        <span className="text-cream/60 uppercase tracking-wide">{label}</span>
        <span className="text-cream/80 font-mono">{pct}%</span>
      </div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      {reasoning && <p className="text-cream/40 text-xs mt-0.5 italic truncate">{reasoning}</p>}
    </div>
  );
}

const SEVERITY_COLOR = {
  critical: 'text-red-400 bg-red-900/30',
  high: 'text-orange-400 bg-orange-900/30',
  medium: 'text-amber-400 bg-amber-900/30',
  low: 'text-cream/60 bg-white/5',
};

export function TaxonomyPanel({ agent }) {
  const at = agent.agent_type || {};
  const impl = agent.implementation_pattern || {};
  const comp = agent.composition_pattern || {};
  const auto = agent.autonomy_level || {};
  const trifecta = agent.trifecta || {};

  return (
    <div
      className="border-t border-white/10 bg-navy/90 p-3 text-xs"
      onClick={e => e.stopPropagation()}
    >
      {/* Taxonomy */}
      <p className="text-goldenrod font-semibold uppercase tracking-widest mb-2 text-xs">Classification</p>
      <ConfidenceBar label={`Type · ${at.value || '—'}`} value={at.confidence} reasoning={at.reasoning} />
      <ConfidenceBar label={`Impl · ${impl.value || '—'}`} value={impl.confidence} reasoning={impl.reasoning} />
      <ConfidenceBar label={`Comp · ${comp.value || '—'}`} value={comp.confidence} reasoning={comp.reasoning} />
      <ConfidenceBar label={`Autonomy · ${auto.value || '—'}`} value={auto.confidence} reasoning={auto.reasoning} />

      {/* Trifecta */}
      <p className="text-goldenrod font-semibold uppercase tracking-widest mt-3 mb-2 text-xs">Lethal Trifecta</p>
      <div className="grid grid-cols-3 gap-1 mb-1">
        {[
          ['Private Data', trifecta.has_private_data_access],
          ['Untrusted Exp.', trifecta.has_untrusted_content_exposure],
          ['External Comms', trifecta.has_external_communication],
        ].map(([label, active]) => (
          <div
            key={label}
            className={`rounded px-1.5 py-1 text-center ${active ? 'bg-red-900/40 text-red-300' : 'bg-white/5 text-cream/30'}`}
          >
            {active ? '⚡' : '○'} {label}
          </div>
        ))}
      </div>
      <p className="text-cream/50 text-xs">
        Score: {trifecta.score}/3
        {trifecta.rule_of_two_violation && (
          <span className="ml-2 text-red-400 font-bold">RULE OF TWO VIOLATED</span>
        )}
      </p>

      {/* Governance */}
      <p className="text-goldenrod font-semibold uppercase tracking-widest mt-3 mb-1 text-xs">Governance</p>
      <div className="flex gap-2 flex-wrap">
        {[
          ['Registered', agent.is_registered],
          ['Labeled', agent.is_labeled],
          ['Has Owner', agent.has_owner],
          ['API Key', agent.has_api_key_env],
          ['OAuth', agent.has_oauth_config],
          ['MCP', agent.has_mcp_config],
        ].map(([label, active]) => (
          <span
            key={label}
            className={`px-1.5 py-0.5 rounded text-xs ${active ? 'bg-green-900/40 text-green-300' : 'bg-white/5 text-cream/30'}`}
          >
            {label}
          </span>
        ))}
      </div>

      {/* Risk codes */}
      {agent.asi_risks?.length > 0 && (
        <>
          <p className="text-goldenrod font-semibold uppercase tracking-widest mt-3 mb-1 text-xs">ASI Risk Codes</p>
          <div className="flex flex-wrap gap-1">
            {agent.asi_risks.map(code => (
              <span
                key={code}
                className="bg-red-900/30 text-red-300 px-1.5 py-0.5 rounded font-mono text-xs"
                title={agent.asi_risk_descriptions?.[code] || ''}
              >
                {code}
              </span>
            ))}
          </div>
        </>
      )}

      {/* Violations */}
      {agent.violations?.length > 0 && (
        <>
          <p className="text-goldenrod font-semibold uppercase tracking-widest mt-3 mb-1 text-xs">Violations</p>
          <div className="space-y-1">
            {agent.violations.map((v, i) => (
              <div
                key={i}
                className={`rounded px-2 py-1 ${SEVERITY_COLOR[v.severity] || 'bg-white/5 text-cream/60'}`}
              >
                <span className="font-semibold font-mono">{v.violation_type}</span>
                <span className="ml-2 text-cream/50">{v.description}</span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Temporal */}
      <div className="mt-3 pt-2 border-t border-white/10 text-cream/30 text-xs flex justify-between">
        <span>First: {agent.first_detected ? new Date(agent.first_detected).toLocaleTimeString() : '—'}</span>
        <span>Last: {agent.last_seen ? new Date(agent.last_seen).toLocaleTimeString() : '—'}</span>
        <span className="font-mono">{agent.container_id?.slice(0, 12)}</span>
      </div>
    </div>
  );
}
