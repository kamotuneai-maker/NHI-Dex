import { ExportButton } from './ExportButton.jsx';

const STATUS_COLORS = {
  live: 'bg-green-500',
  reconnecting: 'bg-amber-500 animate-pulse',
  connecting: 'bg-gray-400 animate-pulse',
};

const STATUS_LABELS = {
  live: 'LIVE',
  reconnecting: 'RECONNECTING',
  connecting: 'CONNECTING',
};

export function Header({ connectionStatus, onRefresh, agents }) {
  return (
    <header className="flex items-center justify-between px-5 py-3 bg-navy border-b border-goldenrod/30">
      <div className="flex items-center gap-3">
        <img src="/logo.png" alt="NHI-Dex" className="w-10 h-10 rounded-lg object-contain" />
        <div>
          <h1 className="text-cream font-bold text-lg leading-tight tracking-wide">NHI-Dex</h1>
          <p className="text-cream/40 text-xs leading-tight">Non-Human Identity Monitor</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Connection status badge */}
        <div className="flex items-center gap-2 bg-navy/60 border border-cream/10 rounded-full px-3 py-1">
          <span className={`w-2 h-2 rounded-full ${STATUS_COLORS[connectionStatus] || 'bg-gray-400'}`} />
          <span className="text-xs text-cream/60 font-mono font-semibold tracking-widest">
            {STATUS_LABELS[connectionStatus] || connectionStatus.toUpperCase()}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="text-cream/40 hover:text-goldenrod transition-colors text-sm px-2 py-1 rounded"
          title="Refresh"
        >
          ↺
        </button>

        <ExportButton agents={agents} />
      </div>
    </header>
  );
}
