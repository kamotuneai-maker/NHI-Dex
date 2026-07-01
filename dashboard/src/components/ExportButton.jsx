function agentsToCSV(agents) {
  const headers = [
    'container_id', 'container_name', 'image_name',
    'adoption_tier', 'agent_type', 'alert_level',
    'detection_mode', 'overall_confidence',
    'autonomy_level', 'is_registered', 'is_labeled',
    'violations_count', 'trifecta_score', 'rule_of_two',
    'asi_risks', 'first_detected', 'last_seen', 'status',
  ];
  const rows = agents.map(a => [
    a.container_id,
    a.container_name,
    a.image_name,
    a.adoption_tier,
    a.agent_type?.value || '',
    a.alert_level,
    a.detection_mode,
    (a.overall_confidence || 0).toFixed(3),
    a.autonomy_level?.value || '',
    a.is_registered,
    a.is_labeled,
    a.violations?.length ?? 0,
    a.trifecta?.score ?? 0,
    a.trifecta?.rule_of_two_violation ?? false,
    (a.asi_risks || []).join('|'),
    a.first_detected,
    a.last_seen,
    a.status,
  ]);
  return [headers, ...rows].map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
}

function download(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function ExportButton({ agents = [] }) {
  const ts = () => new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);

  const exportJSON = () => {
    download(
      `nhi-dex-agents-${ts()}.json`,
      JSON.stringify({ exported_at: new Date().toISOString(), agents }, null, 2),
      'application/json',
    );
  };

  const exportCSV = () => {
    download(`nhi-dex-agents-${ts()}.csv`, agentsToCSV(agents), 'text/csv');
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={exportJSON}
        className="text-xs px-2.5 py-1.5 rounded-lg bg-goldenrod/20 hover:bg-goldenrod/30 text-goldenrod border border-goldenrod/30 transition-colors font-semibold"
        title="Export JSON"
      >
        ↓ JSON
      </button>
      <button
        onClick={exportCSV}
        className="text-xs px-2.5 py-1.5 rounded-lg bg-goldenrod/20 hover:bg-goldenrod/30 text-goldenrod border border-goldenrod/30 transition-colors font-semibold"
        title="Export CSV"
      >
        ↓ CSV
      </button>
    </div>
  );
}
