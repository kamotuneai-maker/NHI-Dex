const FEED_STYLES = {
  agent_classified: {
    icon: '◈',
    color: 'text-blue-300',
    bg: 'bg-blue-900/20 border-blue-700/30',
  },
  agent_removed: {
    icon: '✕',
    color: 'text-cream/40',
    bg: 'bg-white/5 border-white/10',
  },
  alert: {
    icon: '⚠',
    color: 'text-amber-300',
    bg: 'bg-amber-900/20 border-amber-700/30',
  },
  violation: {
    icon: '⛔',
    color: 'text-red-300',
    bg: 'bg-red-900/20 border-red-700/30',
  },
};

function feedLabel(item) {
  const { type, data } = item;
  switch (type) {
    case 'agent_classified':
      return `Agent detected: ${data.container_name} [${data.adoption_tier}] — ${data.alert_level}`;
    case 'agent_removed':
      return `Agent removed: ${data.container_name}`;
    case 'alert':
      return `${data.level} alert: ${data.container_name} — ${(data.reasons || []).slice(0, 2).join('; ')}`;
    case 'violation':
      return `${data.violation_type}: ${data.container_name} — ${data.description}`;
    default:
      return JSON.stringify(data).slice(0, 100);
  }
}

export function ViolationFeed({ feed }) {
  if (!feed?.length) {
    return (
      <div className="h-16 border-t border-cream/10 flex items-center justify-center text-cream/20 text-xs">
        Event feed — waiting for activity…
      </div>
    );
  }

  return (
    <div className="border-t border-cream/10 bg-navy/80">
      <div className="flex items-center gap-2 px-4 py-1.5 border-b border-cream/10">
        <span className="text-goldenrod text-xs font-bold uppercase tracking-widest">Live Event Feed</span>
        <span className="text-cream/30 text-xs">{feed.length} events</span>
      </div>
      <div className="flex gap-2 px-3 py-2 overflow-x-auto">
        {feed.slice(0, 20).map(item => {
          const style = FEED_STYLES[item.type] || FEED_STYLES.agent_classified;
          return (
            <div
              key={item.id}
              className={`flex-shrink-0 flex items-start gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs max-w-xs ${style.bg}`}
            >
              <span className={`${style.color} mt-px`}>{style.icon}</span>
              <div>
                <p className={`font-semibold ${style.color}`}>{item.type.replace('_', ' ')}</p>
                <p className="text-cream/50 text-xs leading-snug mt-0.5">{feedLabel(item)}</p>
                <p className="text-cream/20 text-xs mt-0.5">
                  {new Date(item.ts).toLocaleTimeString()}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
