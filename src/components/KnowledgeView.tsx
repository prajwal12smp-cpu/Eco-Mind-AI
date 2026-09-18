import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  ExternalLink,
  ShieldCheck,
  FileText,
  Building,
  Calendar,
  Sparkles,
  Layers,
  CheckCircle,
} from 'lucide-react';
import { CorpusDocument, RetrievalTrace } from '../types';
import { fetchDocuments, searchKnowledge } from '../api';

export const KnowledgeView: React.FC = () => {
  const [documents, setDocuments] = useState<CorpusDocument[]>([]);
  const [searchQuery, setSearchQuery] = useState('soil organic carbon semi-arid legume intercropping');
  const [targetMetric, setTargetMetric] = useState('');
  const [regionFilter, setRegionFilter] = useState('');
  const [searchResults, setSearchResults] = useState<RetrievalTrace | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);

  useEffect(() => {
    loadDocs();
    handleSearch();
  }, []);

  const loadDocs = async () => {
    setIsLoadingDocs(true);
    try {
      const res = await fetchDocuments();
      setDocuments(res.documents);
    } catch (err) {
      console.error('Failed to load corpus documents:', err);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const trace = await searchKnowledge(
        searchQuery,
        targetMetric || undefined,
        regionFilter || undefined,
        4
      );
      setSearchResults(trace);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">
              Scientific Evidence Base & RAG Retrieval Index
            </h2>
            <p className="text-xs text-slate-400">
              Peer-reviewed guidelines and empirical field trials from FAO, IPCC, ICRAF, and ICRISAT
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Vector Index Active: {documents.length} Core Publications</span>
        </div>
      </div>

      {/* Semantic Search Interface */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 space-y-4">
        <form onSubmit={handleSearch} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search ecological interventions, crop systems, soil rehabilitation..."
                className="w-full bg-slate-950 text-white pl-10 pr-4 py-2.5 rounded-xl border border-slate-700 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="flex gap-2">
              <select
                value={targetMetric}
                onChange={(e) => setTargetMetric(e.target.value)}
                className="bg-slate-950 text-slate-300 text-xs px-3 py-2.5 rounded-xl border border-slate-700 focus:outline-none focus:border-emerald-500"
              >
                <option value="">All Target Metrics</option>
                <option value="Soil organic carbon">Soil Organic Carbon</option>
                <option value="Soil moisture">Soil Moisture</option>
                <option value="Soil erosion">Soil Erosion</option>
                <option value="Plant-available water">Plant-available Water</option>
                <option value="Pollinator abundance">Pollinator Abundance</option>
              </select>

              <select
                value={regionFilter}
                onChange={(e) => setRegionFilter(e.target.value)}
                className="bg-slate-950 text-slate-300 text-xs px-3 py-2.5 rounded-xl border border-slate-700 focus:outline-none focus:border-emerald-500"
              >
                <option value="">All Regions</option>
                <option value="semi-arid">Semi-Arid Tropics</option>
                <option value="sub-humid">Sub-Humid</option>
                <option value="dryland">Global Drylands</option>
              </select>

              <button
                type="submit"
                disabled={isSearching}
                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm shadow-emerald-950/40"
              >
                {isSearching ? (
                  <Sparkles className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Search className="w-3.5 h-3.5" />
                )}
                <span>Search</span>
              </button>
            </div>
          </div>
        </form>

        {/* Search Results Display */}
        {searchResults && (
          <div className="pt-3 border-t border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>
                Retrieved <strong className="text-white">{searchResults.sources.length}</strong> grounded citation chunks
              </span>
              {searchResults.top_score && (
                <span className="font-mono text-emerald-400">
                  Top Relevance: {(searchResults.top_score * 100).toFixed(1)}%
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {searchResults.sources.map((src, i) => (
                <div
                  key={i}
                  className="bg-slate-950 p-4 rounded-xl border border-emerald-950 text-xs space-y-2 hover:border-emerald-800/60 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-emerald-300">
                      {src.organization} ({src.year})
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/60 text-emerald-400 border border-emerald-900/60 font-mono">
                      {(src.relevance_score * 100).toFixed(0)}% Match
                    </span>
                  </div>

                  <h5 className="font-medium text-slate-200">{src.source_title}</h5>

                  <p className="text-slate-400 leading-relaxed bg-slate-900/70 p-2.5 rounded-lg border border-slate-800">
                    &ldquo;{src.evidence_text}&rdquo;
                  </p>

                  {src.reported_change && (
                    <div className="text-[11px] text-teal-300 flex items-center gap-1">
                      <span className="text-slate-500">Verified Empirical Effect:</span>
                      <span className="font-medium bg-teal-950/80 px-1.5 py-0.5 rounded border border-teal-800/40">
                        {src.reported_change}
                      </span>
                    </div>
                  )}

                  {src.doi_or_url && (
                    <div className="flex justify-end pt-1">
                      <a
                        href={src.doi_or_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-teal-400 hover:underline flex items-center gap-1"
                      >
                        Institutional Record <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Indexed Document Corpus Inventory */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          Indexed Institutional Corpus ({documents.length} Publications)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
                  <span className="font-semibold text-emerald-400 flex items-center gap-1">
                    <Building className="w-3.5 h-3.5" />
                    {doc.organization}
                  </span>
                  <span className="flex items-center gap-1 font-mono text-[11px]">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    {doc.year}
                  </span>
                </div>

                <h4 className="text-xs font-semibold text-slate-200 leading-snug mb-2">
                  {doc.title}
                </h4>

                <div className="space-y-1.5">
                  <div className="text-[11px] text-slate-400 flex flex-wrap gap-1">
                    {(doc.target_metrics || doc.metrics || []).map((m, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded bg-slate-800/80 text-teal-300 text-[10px]"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                <span>{doc.document_type}</span>
                <span className="text-emerald-400 font-medium">
                  {doc.quantified_claims_count} Verified Claims
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
