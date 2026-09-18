import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChatView } from './components/ChatView';
import { DashboardView } from './components/DashboardView';
import { SimulatorView } from './components/SimulatorView';
import { KnowledgeView } from './components/KnowledgeView';
import { SystemHealth } from './types';
import { fetchHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'simulator' | 'knowledge'>('chat');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [externalPrompt, setExternalPrompt] = useState<string | null>(null);
  const [isBenchmarkLoading, setIsBenchmarkLoading] = useState(false);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => console.warn('Health check issue:', err));
  }, []);

  const handleRunBenchmark = () => {
    setIsBenchmarkLoading(true);
    setActiveTab('chat');
    // Inject the Darukaa.Earth benchmark farm scenario
    setExternalPrompt(
      'My farm is in semi-arid Karnataka. Soil organic carbon is 0.3%, rainfall is low, and I cultivate wheat in monoculture with synthetic fertilizer.'
    );
    setTimeout(() => {
      setIsBenchmarkLoading(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-white">
      {/* Top Application Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        onRunBenchmark={handleRunBenchmark}
        isBenchmarkLoading={isBenchmarkLoading}
      />

      {/* Main Body View Switching */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <ChatView
            conversationId={conversationId}
            setConversationId={setConversationId}
            externalPrompt={externalPrompt}
            onClearExternalPrompt={() => setExternalPrompt(null)}
          />
        )}

        {activeTab === 'dashboard' && <DashboardView />}

        {activeTab === 'simulator' && <SimulatorView />}

        {activeTab === 'knowledge' && <KnowledgeView />}
      </main>

      {/* Subtle Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <span>
            EcoMind AI • Evidence-Grounded Biodiversity Intelligence for Darukaa.Earth
          </span>
          <div className="flex items-center gap-3">
            <span>Deterministic Multi-Metric Engine</span>
            <span>•</span>
            <span>FAO / IPCC / ICRAF / ICRISAT RAG Corpus</span>
            <span>•</span>
            <span>Zero-Hallucination Claim Guard</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
