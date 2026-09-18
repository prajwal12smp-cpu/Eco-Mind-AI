import React from 'react';
import {
  Leaf,
  Layers,
  Search,
  Sliders,
  Sparkles,
  ShieldCheck,
  BookOpen,
  RefreshCw,
  Database,
} from 'lucide-react';
import { SystemHealth } from '../types';

interface HeaderProps {
  activeTab: 'chat' | 'dashboard' | 'simulator' | 'knowledge';
  setActiveTab: (tab: 'chat' | 'dashboard' | 'simulator' | 'knowledge') => void;
  health: SystemHealth | null;
  onRunBenchmark: () => void;
  isBenchmarkLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  health,
  onRunBenchmark,
  isBenchmarkLoading,
}) => {
  return (
    <header className="border-b border-emerald-900/40 bg-slate-950/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-900/30 ring-1 ring-emerald-400/30">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white">EcoMind AI</span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700/50">
                  Darukaa.Earth
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Evidence-Grounded Biodiversity Intelligence & Multi-Metric Reasoning
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            <button
              id="tab-chat"
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'chat'
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Diagnostic Chat</span>
            </button>

            <button
              id="tab-dashboard"
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Farm Dashboard</span>
            </button>

            <button
              id="tab-simulator"
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'simulator'
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Multi-Metric Simulator</span>
            </button>

            <button
              id="tab-knowledge"
              onClick={() => setActiveTab('knowledge')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'knowledge'
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-900/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>RAG Corpus</span>
            </button>
          </nav>

          {/* Benchmark Action & Engine Status */}
          <div className="flex items-center gap-3">
            <button
              id="btn-run-benchmark"
              onClick={onRunBenchmark}
              disabled={isBenchmarkLoading}
              title="Load standard Darukaa.Earth benchmark farm (Semi-arid Karnataka, 0.3% SOC, Wheat Monoculture)"
              className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 active:scale-95 transition-all disabled:opacity-50"
            >
              {isBenchmarkLoading ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              )}
              <span>Benchmark Case</span>
            </button>

            {/* Health pill */}
            <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>RAG {health?.knowledge_corpus_documents ?? 6} Docs</span>
              <span className="text-slate-500">|</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <Database className="w-3 h-3" />
                Audited
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
