import { useState, useEffect, useRef, useCallback } from 'react';

const ENGINE_URL = import.meta.env.VITE_ENGINE_URL || 'http://localhost:8000';

export function useAgentData() {
  const [agents, setAgents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [feed, setFeed] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const esRef = useRef(null);
  const reconnectRef = useRef(null);

  const addFeed = useCallback((type, data) => {
    setFeed(prev => [
      { id: `${Date.now()}-${Math.random()}`, type, data, ts: new Date().toISOString() },
      ...prev,
    ].slice(0, 150));
  }, []);

  const fetchSummary = useCallback(() => {
    fetch(`${ENGINE_URL}/api/summary`)
      .then(r => r.json())
      .then(setSummary)
      .catch(() => {});
  }, []);

  const fetchAgents = useCallback(() => {
    fetch(`${ENGINE_URL}/api/agents`)
      .then(r => r.json())
      .then(d => setAgents(d.agents || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchAgents();
    fetchSummary();

    const connectSSE = () => {
      if (esRef.current) esRef.current.close();

      const es = new EventSource(`${ENGINE_URL}/api/events`);
      esRef.current = es;

      es.onopen = () => {
        setConnectionStatus('live');
        if (reconnectRef.current) {
          clearTimeout(reconnectRef.current);
          reconnectRef.current = null;
        }
      };

      es.onerror = () => {
        setConnectionStatus('reconnecting');
        es.close();
        reconnectRef.current = setTimeout(connectSSE, 3000);
      };

      es.addEventListener('agent_classified', e => {
        const agent = JSON.parse(e.data);
        setAgents(prev => {
          const idx = prev.findIndex(a => a.container_id === agent.container_id);
          if (idx >= 0) {
            const next = [...prev];
            next[idx] = agent;
            return next;
          }
          return [...prev, agent];
        });
        addFeed('agent_classified', agent);
        fetchSummary();
      });

      es.addEventListener('agent_removed', e => {
        const data = JSON.parse(e.data);
        setAgents(prev => prev.filter(a => a.container_id !== data.container_id));
        addFeed('agent_removed', data);
        fetchSummary();
      });

      es.addEventListener('alert', e => {
        addFeed('alert', JSON.parse(e.data));
      });

      es.addEventListener('violation', e => {
        addFeed('violation', JSON.parse(e.data));
      });
    };

    connectSSE();
    const interval = setInterval(() => { fetchAgents(); fetchSummary(); }, 30000);

    return () => {
      clearInterval(interval);
      if (esRef.current) esRef.current.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [fetchAgents, fetchSummary, addFeed]);

  return { agents, summary, feed, connectionStatus, refetch: fetchAgents };
}
