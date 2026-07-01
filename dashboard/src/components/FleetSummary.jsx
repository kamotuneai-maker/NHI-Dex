function Stat({ label, value, color = 'text-cream', sub }) {
  return (
    <div className="flex flex-col items-center px-4 py-2 border-r border-cream/10 last:border-0">
      <span className={`text-2xl font-bold font-mono ${color}`}>{value ?? '—'}</span>
      <span className="text-xs text-cream/50 uppercase tracking-wider mt-0.5 whitespace-nowrap">{label}</span>
      {sub && <span className="text-xs text-cream/30 mt-0.5">{sub}</span>}
    </div>
  );
}

export function FleetSummary({ summary }) {
  const s = summary || {};
  return (
    <div className="flex items-center bg-navy/80 border-b border-cream/10 overflow-x-auto">
      <Stat label="Agents" value={s.total_agents ?? 0} />
      <Stat
        label="Shadow AI (AT0)"
        value={s.shadow_ai_count ?? 0}
        color={(s.shadow_ai_count ?? 0) > 0 ? 'text-red-400' : 'text-cream'}
      />
      <Stat
        label="RED Alerts"
        value={s.red_alerts ?? 0}
        color={(s.red_alerts ?? 0) > 0 ? 'text-red-400' : 'text-cream'}
      />
      <Stat
        label="Yellow"
        value={s.yellow_alerts ?? 0}
        color={(s.yellow_alerts ?? 0) > 0 ? 'text-amber-400' : 'text-cream'}
      />
      <Stat label="Green" value={s.green_alerts ?? 0} color="text-green-400" />
      <Stat
        label="Violations"
        value={s.active_violations ?? 0}
        color={(s.active_violations ?? 0) > 0 ? 'text-amber-400' : 'text-cream'}
      />
      <Stat
        label="Trifecta (Rule of Two)"
        value={s.trifecta_violations ?? 0}
        color={(s.trifecta_violations ?? 0) > 0 ? 'text-red-400' : 'text-cream'}
      />
      <div className="ml-auto px-4 text-xs text-cream/30 whitespace-nowrap">
        {s.storage ? `storage: ${s.storage}` : ''}
      </div>
    </div>
  );
}
