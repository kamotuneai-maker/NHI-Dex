import { useState } from 'react';
import { useAgentData } from './hooks/useAgentData.js';
import { Header } from './components/Header.jsx';
import { FleetSummary } from './components/FleetSummary.jsx';
import { DexCard } from './components/DexCard.jsx';
import { Sidebar } from './components/Sidebar.jsx';
import { ViolationFeed } from './components/ViolationFeed.jsx';
import { ReferencePage } from './components/ReferencePage.jsx';

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-64 text-cream/25 select-none">
      <div className="text-7xl mb-4 opacity-30">◈</div>
      <p className="text-lg font-semibold tracking-wide">No agents detected</p>
      <p className="text-sm mt-1">Start your Docker containers to begin monitoring</p>
      <p className="text-xs mt-3 font-mono opacity-50">docker compose up -d</p>
    </div>
  );
}

const TABS = [
  { id: 'monitor', label: 'Monitor' },
  { id: 'reference', label: 'Reference' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('monitor');
  const { agents, summary, feed, connectionStatus, refetch } = useAgentData();
  const activeAgents = agents.filter(a => a.status !== 'inactive');

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-navy text-cream">
      <Header connectionStatus={connectionStatus} onRefresh={refetch} agents={activeAgents} />

      {/* Tab bar */}
      <div className="flex gap-1 px-5 pt-2 border-b border-cream/10 bg-navy">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-semibold rounded-t-lg transition-colors -mb-px border-b-2 ${
              activeTab === tab.id
                ? 'text-goldenrod border-goldenrod bg-[#162040]'
                : 'text-cream/40 border-transparent hover:text-cream/70'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'reference' ? (
        <ReferencePage />
      ) : (
        <>
      <FleetSummary summary={summary} />

      {/* Main content */}
      <div className="flex-1 flex gap-4 p-4 overflow-hidden min-h-0">
        {/* Dex card grid */}
        <div className="flex-1 overflow-y-auto min-w-0">
          {activeAgents.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="grid gap-4 grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              {activeAgents.map((agent, i) => (
                <DexCard key={agent.container_id} agent={agent} index={i} />
              ))}
            </div>
          )}
        </div>

        {/* Right sidebar */}
        <Sidebar agents={activeAgents} summary={summary} />
      </div>

      {/* Bottom event feed */}
      <ViolationFeed feed={feed} />
        </>
      )}
    </div>
  );
}
