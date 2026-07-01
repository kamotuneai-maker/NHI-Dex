import { useState } from 'react';
import { AgentSprite } from './AgentSprite.jsx';
import { TaxonomyPanel } from './TaxonomyPanel.jsx';

const TIER_COLORS = {
  AT0: 'bg-red-700 text-red-100',
  AT1: 'bg-gray-600 text-gray-100',
  AT2: 'bg-gray-500 text-gray-100',
  AT3: 'bg-purple-700 text-purple-100',
  AT4: 'bg-blue-700 text-blue-100',
  AT5: 'bg-green-700 text-green-100',
  AT6: 'bg-amber-600 text-amber-100',
  AT7: 'bg-orange-700 text-orange-100',
  AT8: 'bg-red-800 text-red-100',
};

const TIER_DESCRIPTIONS = {
  AT0: 'Shadow AI',
  AT1: 'Basic',
  AT2: 'Tooled',
  AT3: 'MCP',
  AT4: 'Coding',
  AT5: 'Enterprise',
  AT6: 'External',
  AT7: 'Advanced',
  AT8: 'Federated',
};

const TYPE_LABELS = {
  enterprise: 'Enterprise',
  coding: 'Coding',
  'client-facing': 'Client-Facing',
  personal: 'Personal',
  infrastructure: 'Infra',
  unknown: '?',
};

function AlertDot({ level }) {
  if (level === 'RED') return <span className="w-3 h-3 rounded-full bg-red-500 pulse-red inline-block" />;
  if (level === 'YELLOW') return <span className="w-3 h-3 rounded-full bg-amber-400 inline-block" />;
  return <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />;
}

export function DexCard({ agent, index }) {
  const [expanded, setExpanded] = useState(false);

  const isAT0 = agent.adoption_tier === 'AT0';
  const isTrifecta = agent.trifecta?.rule_of_two_violation;
  const alertLevel = agent.alert_level;
  const agentType = agent.agent_type?.value || 'unknown';
  const confidence = Math.round((agent.overall_confidence || 0) * 100);

  const cardBg = isAT0
    ? 'bg-red-950 border-red-700'
    : isTrifecta
    ? 'bg-amber-950 border-amber-600'
    : 'bg-[#162040] border-cream/10';

  return (
    <div
      className={`relative rounded-xl border overflow-hidden cursor-pointer select-none
        transition-all duration-200 hover:scale-[1.02] hover:shadow-xl hover:border-goldenrod/50
        ${cardBg}`}
      onClick={() => setExpanded(v => !v)}
    >
      {/* Warning banners */}
      {isAT0 && (
        <div className="bg-red-600 text-white text-xs font-bold text-center py-1 tracking-widest">
          ⚠ SHADOW AI — AT0 UNREGISTERED
        </div>
      )}
      {isTrifecta && !isAT0 && (
        <div className="bg-amber-500 text-navy text-xs font-bold text-center py-1 tracking-widest">
          ⚡ RULE OF TWO VIOLATION
        </div>
      )}

      {/* Card top: sprite + identity */}
      <div className="relative p-3 flex flex-col items-center">
        {/* Card number */}
        <span className="absolute top-2 right-2 text-xs text-cream/25 font-mono">
          #{String(index + 1).padStart(3, '0')}
        </span>

        {/* Alert indicator */}
        <div className="absolute top-2 left-2">
          <AlertDot level={alertLevel} />
        </div>

        {/* Sprite */}
        <div className={`rounded-lg p-2 mt-1 ${isAT0 ? 'bg-red-900/40' : 'bg-navy/50'}`}>
          <AgentSprite type={agentType} size={68} />
        </div>

        {/* Name */}
        <p className="mt-2 font-bold text-cream text-sm text-center leading-tight truncate w-full px-1">
          {agent.container_name}
        </p>
        <p className="text-cream/30 text-xs font-mono text-center truncate w-full px-1">
          {agent.image_name?.split('/').pop()?.split(':')[0] || agent.image_name}
        </p>
      </div>

      {/* Stats grid */}
      <div className="px-3 pb-2 grid grid-cols-2 gap-x-2 gap-y-0.5 text-xs">
        <StatCell label="TIER" value={agent.adoption_tier} extra={TIER_DESCRIPTIONS[agent.adoption_tier]} tierColor={TIER_COLORS[agent.adoption_tier]} />
        <StatCell label="TYPE" value={TYPE_LABELS[agentType] || agentType} />
        <StatCell label="MODE" value={agent.detection_mode} />
        <StatCell label="AUTO" value={agent.autonomy_level?.value || '—'} />
      </div>

      {/* Confidence bar */}
      <div className="px-3 pb-2">
        <div className="flex justify-between text-xs text-cream/30 mb-0.5">
          <span>Detection confidence</span>
          <span className="font-mono">{confidence}%</span>
        </div>
        <div className="h-1 bg-white/10 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${confidence >= 70 ? 'bg-green-500' : confidence >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Violation badge */}
      {agent.violations?.length > 0 && (
        <div className="px-3 pb-2 flex gap-1 flex-wrap">
          <span className="text-xs bg-red-900/60 text-red-300 rounded px-1.5 py-0.5">
            {agent.violations.length} violation{agent.violations.length !== 1 ? 's' : ''}
          </span>
          {agent.trifecta?.score >= 2 && (
            <span className="text-xs bg-amber-900/60 text-amber-300 rounded px-1.5 py-0.5">
              trifecta {agent.trifecta.score}/3
            </span>
          )}
        </div>
      )}

      {/* Expand / collapse */}
      {expanded && <TaxonomyPanel agent={agent} />}

      <div className="text-center pb-1 text-cream/20 text-xs">
        {expanded ? '▲' : '▼'}
      </div>
    </div>
  );
}

function StatCell({ label, value, extra, tierColor }) {
  return (
    <div className="py-0.5">
      <span className="text-cream/30 uppercase tracking-wider text-xs">{label} </span>
      {tierColor ? (
        <span className={`rounded px-1 text-xs font-bold ${tierColor}`}>{value}</span>
      ) : (
        <span className="text-cream/80 font-semibold">{value || '—'}</span>
      )}
      {extra && <span className="text-cream/30 ml-1 text-xs">· {extra}</span>}
    </div>
  );
}
