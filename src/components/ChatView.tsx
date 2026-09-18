import React, { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import {
  Send,
  Sparkles,
  AlertCircle,
  CornerDownRight,
  ShieldCheck,
  RefreshCcw,
  Zap,
  Info,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Download,
  Database,
  ExternalLink,
} from 'lucide-react';
import { ChatResponse, EnvironmentalState, RecommendationOutput, RetrievalTrace } from '../types';
import { sendChatMessage } from '../api';
import { RecommendationCard } from './RecommendationCard';
import { StateBadge } from './StateBadge';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  clarifyingQuestions?: string[];
  recommendations?: RecommendationOutput[];
  extractedState?: EnvironmentalState;
  stressors?: string[];
  interactions?: string[];
  isComplete?: boolean;
  retrievalTrace?: RetrievalTrace | null;
}

const STARTER_PROMPTS = [
  {
    title: 'Benchmark Semi-Arid Farm',
    prompt:
      'My farm is in semi-arid Karnataka. Soil organic carbon is 0.3%, rainfall is low, and I cultivate wheat in monoculture with synthetic fertilizer.',
  },
  {
    title: 'Sparse Indicator Test',
    prompt: 'I have sandy soil and crop yields are dropping.',
  },
  {
    title: 'Pesticide & Pollinator Concern',
    prompt:
      'We are in Deccan Plateau growing Bt cotton with intense chemical spraying. Honeybee populations have collapsed and topsoil feels like concrete.',
  },
];

interface ChatViewProps {
  conversationId: string | null;
  setConversationId: (id: string | null) => void;
  externalPrompt?: string | null;
  onClearExternalPrompt?: () => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  conversationId,
  setConversationId,
  externalPrompt,
  onClearExternalPrompt,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Welcome to **EcoMind AI**. I am your evidence-grounded biodiversity and ecological intelligence assistant.\n\nDescribe your agricultural parcel, soil indicators (e.g. SOC %, pH, moisture), regional hydrology, and crop practices. I will cross-reference multi-variable interactions, detect ecological stressors, and formulate verified interventions grounded in peer-reviewed FAO, IPCC, and CGIAR literature.',
    },
  ]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentState, setCurrentState] = useState<EnvironmentalState>({
    soil: {},
    land: {},
    biodiversity: { biodiversity_indicators: [] },
    climate: {},
    human_impact: {},
  });
  const [isInformationComplete, setIsInformationComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle external prompt injection (e.g. from the Benchmark button in Header)
  useEffect(() => {
    if (externalPrompt) {
      handleSendMessage(externalPrompt);
      if (onClearExternalPrompt) onClearExternalPrompt();
    }
  }, [externalPrompt]);

  const handleSendMessage = async (textToSend?: string) => {
    const messageText = (textToSend || input).trim();
    if (!messageText || isLoading) return;

    setInput('');
    const userMsgId = 'user-' + Date.now();
    const newMessages: Message[] = [
      ...messages,
      { id: userMsgId, role: 'user', content: messageText },
    ];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response: ChatResponse = await sendChatMessage({
        conversation_id: conversationId,
        message: messageText,
      });

      setConversationId(response.conversation_id);
      setCurrentState(response.extracted_state);
      setIsInformationComplete(response.is_information_complete);

      const assistantMsg: Message = {
        id: 'assistant-' + Date.now(),
        role: 'assistant',
        content: response.message,
        clarifyingQuestions: response.clarifying_questions,
        recommendations: response.recommendations,
        extractedState: response.extracted_state,
        stressors: response.multi_metric_stressors,
        interactions: response.detected_interactions,
        isComplete: response.is_information_complete,
        retrievalTrace: response.retrieval_trace,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: 'err-' + Date.now(),
        role: 'assistant',
        content: `**Error:** ${err.message || 'Unable to communicate with EcoMind reasoning engine.'}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setConversationId(null);
    setMessages([
      {
        id: 'welcome-reset',
        role: 'assistant',
        content:
          'Conversation reset. You can now start with a new land profile or scenario.',
      },
    ]);
    setCurrentState({
      soil: {},
      land: {},
      biodiversity: { biodiversity_indicators: [] },
      climate: {},
      human_impact: {},
    });
    setIsInformationComplete(false);
  };

  const handleExportAudit = () => {
    let report = `# EcoMind AI - Ecological Audit & Intervention Dossier\n\n`;
    report += `**Generated Date:** ${new Date().toISOString()}\n`;
    report += `**Conversation ID:** ${conversationId || 'N/A'}\n\n`;
    report += `## 1. Extracted Environmental Baseline State\n\`\`\`json\n${JSON.stringify(
      currentState,
      null,
      2
    )}\n\`\`\`\n\n`;
    report += `## 2. Conversation Transcript & Scientific Reasoning\n\n`;

    messages.forEach((m, idx) => {
      report += `### ${idx + 1}. [${m.role.toUpperCase()}]\n${m.content}\n\n`;
      if (m.stressors && m.stressors.length > 0) {
        report += `**Identified Stressors:**\n`;
        m.stressors.forEach((s) => (report += `- ${s}\n`));
        report += `\n`;
      }
      if (m.interactions && m.interactions.length > 0) {
        report += `**Cross-Variable Couplings:**\n`;
        m.interactions.forEach((inter) => (report += `- ${inter}\n`));
        report += `\n`;
      }
      if (m.recommendations && m.recommendations.length > 0) {
        report += `**Audited Interventions (${m.recommendations.length}):**\n\n`;
        m.recommendations.forEach((rec, rIdx) => {
          report += `#### ${rIdx + 1}. ${rec.title} (${rec.confidence} Confidence)\n`;
          report += `**Directive:** ${rec.directive}\n\n`;
          report += `**Rationale:** ${rec.scientific_rationale}\n\n`;
          report += `**Time Horizon:** ${rec.time_horizon}\n\n`;
          report += `**Literature Citations:**\n`;
          rec.evidence.forEach((ev) => {
            report += `- **${ev.organization} (${ev.year}):** "${ev.source_title}"\n  ${ev.evidence_text}\n  *Reported Effect:* ${ev.reported_change || 'Documented'}\n`;
          });
          report += `\n`;
        });
      }
    });

    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ecomind-ecological-audit-${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Main Chat Stream (8 cols on lg) */}
      <div className="lg:col-span-8 flex flex-col h-[calc(100vh-140px)] bg-slate-900/60 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
        {/* Chat Header Bar */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold text-slate-200">
              Active Multi-Metric Reasoning Stream
            </span>
            {conversationId && (
              <span className="text-[10px] text-slate-500 font-mono hidden sm:inline">
                ID: {conversationId.slice(0, 8)}...
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportAudit}
              className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 px-2.5 py-1 rounded-lg bg-emerald-950/50 hover:bg-emerald-950 border border-emerald-800/60 transition-all"
              title="Download Audited Scientific Report"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Audit Dossier</span>
            </button>

            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 transition-all"
              title="Start new conversation"
            >
              <RefreshCcw className="w-3.5 h-3.5" />
              <span>Reset Context</span>
            </button>
          </div>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.role === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              {/* Message Bubble */}
              <div
                className={`max-w-3xl rounded-2xl p-4 sm:p-5 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-950/30'
                    : 'bg-slate-900 text-slate-200 rounded-bl-none border border-slate-800 shadow-md'
                }`}
              >
                {/* Assistant Label */}
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2.5 pb-2 border-b border-slate-800/80">
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                      EcoMind Intelligence
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/50 ml-auto">
                      Zero-Hallucination Guarded
                    </span>
                  </div>
                )}

                {/* Message Body Text */}
                {msg.role === 'assistant' ? (
                  <div className="markdown-body">
                    <Markdown>{msg.content}</Markdown>
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                )}

                {/* Detected Stressors Badges */}
                {msg.stressors && msg.stressors.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <div className="text-[11px] font-semibold text-rose-300 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                      Detected Ecological Stressors ({msg.stressors.length}):
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.stressors.map((st, i) => (
                        <span
                          key={i}
                          className="text-xs px-2 py-0.5 rounded-full bg-rose-950/60 text-rose-200 border border-rose-800/50 font-medium"
                        >
                          {st}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Cross-Variable Couplings */}
                {msg.interactions && msg.interactions.length > 0 && (
                  <div className="mt-3">
                    <div className="text-[11px] font-semibold text-teal-300 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <Zap className="w-3.5 h-3.5 text-teal-400" />
                      Cross-Variable Feedback Couplings:
                    </div>
                    <div className="space-y-1">
                      {msg.interactions.map((inter, i) => (
                        <div
                          key={i}
                          className="text-xs px-2.5 py-1 rounded-md bg-teal-950/40 text-teal-200 border border-teal-800/40"
                        >
                          {inter}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Interactive Clarifying Questions Chips */}
                {msg.clarifyingQuestions && msg.clarifyingQuestions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <div className="text-[11px] font-semibold text-amber-300 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                      Missing Parameters (Click to reply):
                    </div>
                    <div className="space-y-1.5">
                      {msg.clarifyingQuestions.map((q, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setInput((prev) =>
                              prev ? `${prev} ${q}` : `Regarding: ${q} `
                            );
                          }}
                          className="w-full text-left text-xs p-2 rounded-lg bg-amber-950/30 hover:bg-amber-950/60 text-amber-200 border border-amber-800/40 flex items-start gap-2 group transition-all"
                        >
                          <CornerDownRight className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0 group-hover:translate-x-0.5 transition-transform" />
                          <span>{q}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* RAG Vector Retrieval Trace */}
                {msg.retrievalTrace && msg.retrievalTrace.sources && msg.retrievalTrace.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800 text-xs">
                    <div className="flex items-center justify-between text-slate-400 mb-2">
                      <span className="font-semibold text-cyan-300 flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
                        <Database className="w-3.5 h-3.5 text-cyan-400" />
                        ChromaDB Vector Retrieval Trace ({msg.retrievalTrace.sources.length} sources)
                      </span>
                      <span className="font-mono text-[10px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-900/60">
                        {msg.retrievalTrace.vector_backend || 'chromadb-in-memory'}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {msg.retrievalTrace.sources.map((src, sIdx) => {
                        const isDoi = src.doi_or_url?.includes('doi.org');
                        return (
                          <div key={sIdx} className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/90 space-y-1.5">
                            <div className="flex flex-wrap items-center justify-between gap-1 text-[11px]">
                              <span className="font-medium text-slate-200">
                                {src.organization} ({src.year}) - {src.source_title}
                              </span>
                              <div className="flex items-center gap-1.5">
                                {src.semantic_similarity != null && (
                                  <span className="font-mono text-[10px] text-cyan-300 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/40">
                                    Sim: {(src.semantic_similarity * 100).toFixed(0)}%
                                  </span>
                                )}
                                <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800/40">
                                  Score: {(src.relevance_score * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>

                            <p className="text-slate-400 text-[11px] italic leading-relaxed">
                              &ldquo;{src.evidence_text}&rdquo;
                            </p>

                            {src.reported_change && (
                              <div className="text-[10px] text-teal-300 flex items-center gap-1">
                                <span className="text-slate-500">Empirical Literature Metric:</span>
                                <span className="font-mono font-medium bg-teal-950/80 px-1.5 py-0.5 rounded">
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
                                  className="text-[10px] text-teal-400 hover:underline flex items-center gap-1"
                                >
                                  {isDoi ? `Verified DOI: ${src.doi_or_url.replace('https://doi.org/', '')}` : 'Official Publication Source'} <ExternalLink className="w-2.5 h-2.5" />
                                </a>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Grounded Recommendations Cards */}
                {msg.recommendations && msg.recommendations.length > 0 && (
                  <div className="mt-5 space-y-4">
                    <div className="flex items-center justify-between border-t border-slate-800 pt-3">
                      <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        Grounded Ecological Interventions ({msg.recommendations.length})
                      </div>
                      <span className="text-[11px] text-slate-400">
                        Peer-Reviewed & Audited
                      </span>
                    </div>

                    <div className="space-y-3">
                      {msg.recommendations.map((rec) => (
                        <RecommendationCard key={rec.id} recommendation={rec} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 text-xs text-emerald-400 p-4 bg-slate-900/90 rounded-2xl border border-slate-800 max-w-md animate-pulse">
              <Sparkles className="w-4 h-4 animate-spin" />
              <span>
                Extracting multi-metric indicators, querying FAO/IPCC corpus & auditing claims...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Starter Prompts Bar (when conversation is fresh) */}
        {messages.length <= 2 && !isLoading && (
          <div className="px-4 py-2 bg-slate-950/60 border-t border-slate-800/60">
            <div className="text-[11px] text-slate-400 mb-1.5 font-medium flex items-center gap-1">
              <Info className="w-3 h-3 text-slate-500" />
              Quick Starters for Benchmark Scenarios:
            </div>
            <div className="flex flex-wrap gap-2">
              {STARTER_PROMPTS.map((starter, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(starter.prompt)}
                  className="text-xs px-2.5 py-1 rounded-md bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-slate-700 transition-all flex items-center gap-1"
                >
                  <span>{starter.title}</span>
                  <ChevronRight className="w-3 h-3 text-slate-400" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="p-4 bg-slate-950 border-t border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-3"
          >
            <input
              id="input-chat-message"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. Soil organic carbon is 0.3%, rain is low, and wheat is grown in monoculture..."
              className="flex-1 bg-slate-900 text-white rounded-xl px-4 py-3 text-sm border border-slate-700 focus:outline-none focus:border-emerald-500 transition-colors placeholder:text-slate-500"
              disabled={isLoading}
            />
            <button
              id="btn-send-chat"
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl font-medium text-sm transition-all flex items-center gap-1.5 shadow-md shadow-emerald-950/40"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="mt-2 text-[11px] text-slate-500 text-center">
            Multi-variable constraint engine + RAG retrieval from FAO, IPCC, ICRAF, and ICRISAT documents.
          </div>
        </div>
      </div>

      {/* Right Sidebar: Extracted Environmental State & Benchmark Insights (4 cols on lg) */}
      <div className="lg:col-span-4 space-y-4">
        <StateBadge state={currentState} isComplete={isInformationComplete} />

        {/* Architecture & Verification Panel */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-4 text-xs space-y-3">
          <h4 className="font-semibold text-slate-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Challenge Architecture Standards
          </h4>
          <div className="space-y-2 text-slate-400 leading-relaxed">
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
              <span>
                <strong className="text-slate-200">Sparse-Data Protocol:</strong> Asks targeted clarifying questions when required soil, hydrology, or land indicators are absent.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0" />
              <span>
                <strong className="text-slate-200">Multi-Metric Coupling:</strong> Evaluates interdependent stressors (e.g. Low SOC × Drought × Monoculture) rather than single-factor recommendations.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
              <span>
                <strong className="text-slate-200">Zero-Hallucination Audit:</strong> Quantified claims must have verified empirical bounds from indexed scientific sources.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
