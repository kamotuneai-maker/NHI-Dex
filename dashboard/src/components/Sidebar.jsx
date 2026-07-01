import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  PieChart, Pie, Legend, ResponsiveContainer,
} from 'recharts';

const TIER_ORDER = ['AT0','AT1','AT2','AT3','AT4','AT5','AT6','AT7','AT8'];
const TIER_FILL = {
  AT0: '#DC2626', AT1: '#6B7280', AT2: '#9CA3AF',
  AT3: '#8B5CF6', AT4: '#3B82F6', AT5: '#16A34A',
  AT6: '#F59E0B', AT7: '#EA580C', AT8: '#B91C1C',
};
const AUTONOMY_FILL = {
  supervised: '#16A34A',
  'semi-autonomous': '#F59E0B',
  autonomous: '#DC2626',
  unknown: '#6B7280',
};

const ASI_RISK_CODES = ['ASI01','ASI02','ASI03','ASI04','ASI05','ASI06','ASI07','ASI08','ASI09','ASI10'];
const ASI_LABELS = {
  ASI01: 'Memory Poisoning',
  ASI02: 'Tool Misuse',
  ASI03: 'Auth Bypass',
  ASI04: 'Prompt Injection',
  ASI05: 'Exfil Risk',
  ASI06: 'Scope Creep',
  ASI07: 'Uncontrolled Exec',
  ASI08: 'Cascading Failure',
  ASI09: 'Shadow AI',
  ASI10: 'Cross-Boundary',
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy border border-goldenrod/30 rounded px-2 py-1 text-xs text-cream">
      <p className="font-bold">{label}</p>
      <p>{payload[0].value} agent{payload[0].value !== 1 ? 's' : ''}</p>
    </div>
  );
};

export function Sidebar({ agents, summary }) {
  // Tier distribution
  const tierData = TIER_ORDER.map(tier => ({
    tier,
    count: agents.filter(a => a.adoption_tier === tier).length,
  })).filter(d => d.count > 0);

  // Autonomy breakdown
  const autoMap = {};
  agents.forEach(a => {
    const v = a.autonomy_level?.value || 'unknown';
    autoMap[v] = (autoMap[v] || 0) + 1;
  });
  const autonomyData = Object.entries(autoMap).map(([name, value]) => ({ name, value }));

  // ASI risk heatmap — count agents per risk code
  const riskCounts = {};
  agents.forEach(a => (a.asi_risks || []).forEach(code => {
    riskCounts[code] = (riskCounts[code] || 0) + 1;
  }));
  const maxRisk = Math.max(1, ...Object.values(riskCounts));

  // Alert breakdown
  const redCount = summary?.red_alerts ?? agents.filter(a => a.alert_level === 'RED').length;
  const yellowCount = summary?.yellow_alerts ?? agents.filter(a => a.alert_level === 'YELLOW').length;
  const greenCount = summary?.green_alerts ?? agents.filter(a => a.alert_level === 'GREEN').length;

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col gap-4 overflow-y-auto pr-1">
      {/* Tier Distribution */}
      <section className="bg-[#162040] rounded-xl border border-cream/10 p-3">
        <h3 className="text-goldenrod text-xs font-bold uppercase tracking-widest mb-2">Tier Distribution</h3>
        {tierData.length === 0 ? (
          <p className="text-cream/30 text-xs text-center py-4">No agents</p>
        ) : (
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={tierData} margin={{ top: 0, right: 0, left: -28, bottom: 0 }}>
              <XAxis dataKey="tier" tick={{ fill: '#F5F2E8', fontSize: 10 }} />
              <YAxis allowDecimals={false} tick={{ fill: '#F5F2E8', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                {tierData.map(d => (
                  <Cell key={d.tier} fill={TIER_FILL[d.tier] || '#6B7280'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      {/* Alert Levels */}
      <section className="bg-[#162040] rounded-xl border border-cream/10 p-3">
        <h3 className="text-goldenrod text-xs font-bold uppercase tracking-widest mb-2">Alert Levels</h3>
        <div className="space-y-2">
          {[
            { label: 'RED', count: redCount, bg: 'bg-red-600' },
            { label: 'YELLOW', count: yellowCount, bg: 'bg-amber-500' },
            { label: 'GREEN', count: greenCount, bg: 'bg-green-600' },
          ].map(({ label, count, bg }) => {
            const total = (redCount + yellowCount + greenCount) || 1;
            const pct = Math.round((count / total) * 100);
            return (
              <div key={label}>
                <div className="flex justify-between text-xs mb-0.5">
                  <span className="text-cream/60">{label}</span>
                  <span className="text-cream/80 font-mono">{count}</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${bg}`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Autonomy Spectrum */}
      <section className="bg-[#162040] rounded-xl border border-cream/10 p-3">
        <h3 className="text-goldenrod text-xs font-bold uppercase tracking-widest mb-2">Autonomy Spectrum</h3>
        {autonomyData.length === 0 ? (
          <p className="text-cream/30 text-xs text-center py-4">No agents</p>
        ) : (
          <ResponsiveContainer width="100%" height={130}>
            <PieChart>
              <Pie data={autonomyData} cx="50%" cy="50%" innerRadius={32} outerRadius={52} dataKey="value" paddingAngle={3}>
                {autonomyData.map(d => (
                  <Cell key={d.name} fill={AUTONOMY_FILL[d.name] || '#6B7280'} />
                ))}
              </Pie>
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(v) => <span style={{ color: '#F5F2E8', fontSize: 10 }}>{v}</span>}
              />
              <Tooltip
                formatter={(v, n) => [v, n]}
                contentStyle={{ background: '#1F2D4E', border: '1px solid #B8860B44', borderRadius: 6, fontSize: 11 }}
                labelStyle={{ color: '#F5F2E8' }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </section>

      {/* ASI Risk Heatmap */}
      <section className="bg-[#162040] rounded-xl border border-cream/10 p-3">
        <h3 className="text-goldenrod text-xs font-bold uppercase tracking-widest mb-2">ASI Risk Heatmap</h3>
        <div className="space-y-1">
          {ASI_RISK_CODES.map(code => {
            const count = riskCounts[code] || 0;
            const intensity = count / maxRisk;
            const bg = count === 0
              ? 'bg-white/5'
              : intensity >= 0.7
              ? 'bg-red-700'
              : intensity >= 0.3
              ? 'bg-amber-600'
              : 'bg-yellow-700/60';
            return (
              <div key={code} className="flex items-center gap-2">
                <span className={`font-mono text-xs w-12 text-center rounded px-1 py-0.5 ${bg} ${count ? 'text-white' : 'text-cream/20'}`}>
                  {code}
                </span>
                <span className="text-cream/40 text-xs truncate flex-1">{ASI_LABELS[code]}</span>
                {count > 0 && <span className="text-red-300 text-xs font-mono">{count}</span>}
              </div>
            );
          })}
        </div>
      </section>
    </aside>
  );
}
