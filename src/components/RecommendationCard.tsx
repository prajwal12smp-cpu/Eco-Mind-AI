import React, { useState } from 'react';
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  FileText,
  Clock,
  TrendingUp,
  Award,
  Layers,
} from 'lucide-react';
import { RecommendationOutput } from '../types';

interface RecommendationCardProps {
  recommendation: RecommendationOutput;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
}) => {
  const [showEvidence, setShowEvidence] = useState(true);

  const getConfidenceBadge = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'bg-emerald-950/80 text-emerald-300 border-emerald-700/50';
      case 'medium':
        return 'bg-amber-950/80 text-amber-300 border-amber-700/50';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900/90 rounded-xl border border-emerald-900/40 p-5 shadow-lg shadow-black/20 hover:border-emerald-700/60 transition-all">
      {/* Top Header */}
      <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <h4 className="text-base font-semibold text-white tracking-tight">
            {recommendation.title}
          </h4>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`text-xs px-2.5 py-0.5 rounded-full border font-medium flex items-center gap-1 ${getConfidenceBadge(
              recommendation.confidence
            )}`}
          >
            <Award className="w-3 h-3" />
            {recommendation.confidence} Confidence
          </span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-medium flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" />
            {recommendation.time_horizon}
          </span>
        </div>
      </div>

      {/* Actionable Directive */}
      <div className="bg-emerald-950/30 border border-emerald-800/40 rounded-lg p-3 mb-3.5">
        <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 mb-1">
          Operational Directive
        </div>
        <p className="text-sm text-emerald-100/90 leading-relaxed font-normal">
          {recommendation.directive}
        </p>
      </div>

      {/* Scientific Rationale */}
      <div className="mb-3.5 text-sm text-slate-300 leading-relaxed">
        <span className="font-semibold text-slate-200">Scientific Rationale: </span>
        {recommendation.scientific_rationale}
      </div>

      {/* Impacted Environmental Metrics */}
      <div className="mb-4">
        <div className="text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-teal-400" />
          Coupled Environmental Metrics Affected:
        </div>
        <div className="flex flex-wrap gap-1.5">
          {recommendation.environmental_metrics_affected.map((metric, i) => (
            <span
              key={i}
              className="text-xs px-2 py-0.5 rounded-md bg-slate-800/90 text-teal-300 border border-slate-700/80 font-medium"
            >
              {metric}
            </span>
          ))}
        </div>
      </div>

      {/* Why This Recommendation (Deterministic Reasoning Trace) */}
      {recommendation.why_this_recommendation && recommendation.why_this_recommendation.length > 0 && (
        <div className="mb-4 bg-slate-950/60 rounded-lg p-3 border border-slate-800/80 text-xs">
          <div className="font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            Deterministic Reasoning Trace:
          </div>
          <ul className="space-y-1 text-slate-300 list-disc list-inside">
            {recommendation.why_this_recommendation.map((step, idx) => (
              <li key={idx} className="leading-relaxed">
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Evidence & Grounding Citations Accordion */}
      {recommendation.evidence && recommendation.evidence.length > 0 && (
        <div className="border-t border-slate-800/80 pt-3">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="flex items-center justify-between w-full text-xs font-semibold text-slate-300 hover:text-emerald-400 transition-colors py-1"
          >
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              Verified Literature Citations ({recommendation.evidence.length})
            </span>
            {showEvidence ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          {showEvidence && (
            <div className="mt-2.5 space-y-2.5">
              {recommendation.evidence.map((ev, idx) => {
                const isDoi = ev.doi_or_url?.includes('doi.org');
                const doiClean = isDoi ? ev.doi_or_url?.replace('https://doi.org/', '') : null;

                return (
                  <div
                    key={idx}
                    className="bg-slate-950/80 border border-emerald-950 rounded-lg p-3 text-xs space-y-2"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-1.5">
                      <span className="font-semibold text-emerald-300">
                        {ev.organization} ({ev.year})
                      </span>
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {ev.document_type}
                        </span>
                        {ev.semantic_similarity != null && (
                          <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-900/60" title="ChromaDB Cosine Vector Similarity">
                            Vector Match {(ev.semantic_similarity * 100).toFixed(0)}%
                          </span>
                        )}
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-900/60">
                          Rerank {(ev.relevance_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div className="text-slate-400 italic text-[11px]">
                      &ldquo;{ev.source_title}&rdquo;
                    </div>

                    <div className="bg-slate-900/90 rounded p-2 text-slate-300 text-xs border border-slate-800 leading-relaxed">
                      {ev.evidence_text}
                    </div>

                    {ev.reported_change && (
                      <div className="text-emerald-300 font-medium flex items-center gap-1.5 text-[11px] bg-emerald-950/40 p-1.5 rounded border border-emerald-900/50">
                        <span className="text-slate-400 font-normal">Reported Literature Empirical Metric:</span>
                        <span className="text-emerald-300 font-mono font-semibold">
                          {ev.reported_change}
                        </span>
                      </div>
                    )}

                    {ev.doi_or_url && (
                      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-900">
                        {isDoi ? (
                          <span className="text-[10px] text-slate-500 font-mono">
                            DOI: {doiClean}
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-500">
                            Official Institutional Publication
                          </span>
                        )}

                        <a
                          href={ev.doi_or_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] text-teal-400 hover:text-teal-300 flex items-center gap-1 hover:underline ml-auto"
                        >
                          {isDoi ? 'Verified DOI Record' : 'Official Publication Source'}{' '}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
