import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../api/client';
import { ChatThread, ChatMessage, RoadmapInitiative } from '../../types/analytics';
import { ScopeBadge } from '../common/ScopeBadge';
import { MetricCard } from '../common/MetricCard';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Plus,
  Trash2,
  Sparkles,
  Bot,
  User,
  Clock,
  Zap,
  Target,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

const SUGGESTED_PROMPTS = [
  'Qual o impacto financeiro de liquidar a categoria Beleza com 40% de desconto?',
  'Quais são os SKUs com maior capital imobilizado em produtos descontinuados?',
  'Quantos SKUs zerados temos e qual a concentração por categoria?',
  'Simule a queima de todo o estoque descontinuado com 30% de margem líquida.',
];

export const CopilotRoadmapView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'copilot' | 'roadmap'>('copilot');

  // Copilot Chat States
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Roadmap States
  const [initiatives, setInitiatives] = useState<RoadmapInitiative[]>([]);
  const [roadmapSummary, setRoadmapSummary] = useState<any>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<string>('Todos');

  // Load threads and roadmap
  useEffect(() => {
    loadThreads();
    loadRoadmap();
  }, []);

  const loadThreads = async () => {
    try {
      const res = await api.listThreads();
      const list = res.threads || [];
      setThreads(list);
      if (list.length > 0 && !activeThreadId) {
        selectThread(list[0].id);
      } else if (list.length === 0) {
        handleNewThread();
      }
    } catch (err) {
      console.error('Erro ao carregar threads:', err);
    }
  };

  const loadRoadmap = async () => {
    try {
      const res = await api.getRoadmap();
      setInitiatives(res.initiatives || []);
      setRoadmapSummary(res.summary);
    } catch (err) {
      console.error('Erro ao carregar roadmap:', err);
    }
  };

  const selectThread = async (id: string) => {
    setActiveThreadId(id);
    try {
      const res = await api.getThread(id);
      setMessages(res.thread.messages || []);
    } catch (err) {
      console.error('Erro ao abrir thread:', err);
    }
  };

  const handleNewThread = async () => {
    try {
      const res = await api.createThread('Nova Conversa');
      const newThread = res.thread;
      setThreads(prev => [newThread, ...prev]);
      setActiveThreadId(newThread.id);
      setMessages([]);
    } catch (err) {
      console.error('Erro ao criar thread:', err);
    }
  };

  const handleDeleteThread = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteThread(id);
      const remaining = threads.filter(t => t.id !== id);
      setThreads(remaining);
      if (activeThreadId === id) {
        if (remaining.length > 0) {
          selectThread(remaining[0].id);
        } else {
          handleNewThread();
        }
      }
    } catch (err) {
      console.error('Erro ao deletar thread:', err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || isSending || !activeThreadId) return;

    const userMsg: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setIsSending(true);

    try {
      const res = await api.sendChatMessage(activeThreadId, text);
      const assistantMsg: ChatMessage = { role: 'assistant', content: res.response };
      setMessages(prev => [...prev, assistantMsg]);
      // Update thread title in sidebar if changed
      if (res.title) {
        setThreads(prev =>
          prev.map(t => (t.id === activeThreadId ? { ...t, title: res.title } : t))
        );
      }
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao se comunicar com o Copiloto de Estoque.',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const filteredInitiatives = initiatives.filter(init => {
    if (selectedHorizon === 'Todos') return true;
    if (selectedHorizon === 'Quick Wins') return init.type.includes('Quick Win');
    return init.horizon === selectedHorizon;
  });

  return (
    <div className="space-y-6 view-enter">
      {/* Sub-tab Switcher */}
      <div className="flex items-center gap-2 border-b border-[#27272a] pb-3">
        <button
          onClick={() => setActiveTab('copilot')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors flex items-center gap-2 ${activeTab === 'copilot'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
            }`}
        >
          <Bot className="w-4 h-4" />
          <span>Copiloto de Estoque IA</span>
        </button>

        <button
          onClick={() => setActiveTab('roadmap')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors flex items-center gap-2 ${activeTab === 'roadmap'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
            }`}
        >
          <Target className="w-4 h-4" />
          <span>Plano de Ação Estratégico (30/60/90 Dias)</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: COPILOTO RE-ACT CHAT */}
      {/* ========================================================================= */}
      {activeTab === 'copilot' && (
        <div className="flex flex-col md:flex-row h-[780px] rounded-xl border border-[#27272a] bg-[#0c0d12] overflow-hidden shadow-2xl">
          {/* Threads Sidebar */}
          <div className="w-full md:w-64 lg:w-72 shrink-0 border-r border-[#27272a] bg-[#11131a] flex flex-col h-full">
            <div className="p-3 border-b border-[#27272a]">
              <button
                onClick={handleNewThread}
                className="w-full py-2 px-3 rounded-lg bg-[#18181b] border border-[#27272a] hover:border-[#38bdf8]/50 text-[#f4f4f5] text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm"
              >
                <Plus className="w-3.5 h-3.5 text-[#38bdf8]" />
                <span>Nova Conversa</span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {threads.map(thread => (
                <div
                  key={thread.id}
                  onClick={() => selectThread(thread.id)}
                  className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer text-xs transition-colors ${activeThreadId === thread.id
                      ? 'bg-[#18181b] border border-[#38bdf8]/40 text-[#f4f4f5]'
                      : 'hover:bg-[#18181b]/60 text-[#a1a1aa] border border-transparent'
                    }`}
                >
                  <span className="truncate flex-1 font-medium">{thread.title || 'Conversa'}</span>
                  <button
                    onClick={e => handleDeleteThread(thread.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:text-rose-400 transition-opacity ml-1"
                    title="Excluir conversa"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            <div className="p-3 border-t border-[#27272a] bg-[#0d0d10] text-[10px] font-mono text-[#71717a] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Memória ReAct • DuckDB Live</span>
            </div>
          </div>

          {/* Chat Window */}
          <div className="flex-1 min-w-0 flex flex-col h-full bg-[#09090b]">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 min-w-0">
              <div className="max-w-4xl mx-auto w-full space-y-6">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center py-16 px-4 space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shadow-[0_0_20px_rgba(56,189,248,0.15)]">
                      <Sparkles className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-[#f4f4f5]">Copiloto de Estoque Vértice Retail</h3>
                      <p className="text-xs text-[#71717a] max-w-md mt-1 font-sans leading-relaxed">
                        Assistente analítico conectado ao banco de dados DuckDB para diagnósticos, simulações de liquidação e investigação de SKUs em tempo real.
                      </p>
                    </div>

                    {/* Quick Prompts */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-xl text-left mt-4">
                      {SUGGESTED_PROMPTS.map((prompt, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendMessage(prompt)}
                          className="p-3 rounded-lg bg-[#121215] border border-[#27272a] hover:border-[#38bdf8]/50 text-xs text-[#d4d4d8] hover:text-[#f4f4f5] transition-all hover:bg-[#18181b]"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx} className="w-full">
                      {msg.role === 'user' ? (
                        <div className="flex flex-col items-end gap-1.5 w-full">
                          <div className="flex items-start gap-2.5 max-w-[85%] md:max-w-[75%]">
                            <div className="rounded-2xl px-4 py-2.5 bg-[#2563eb]/20 border border-[#2563eb]/40 text-[#f4f4f5] text-xs leading-relaxed shadow-sm">
                              <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                            </div>
                            <div className="w-7 h-7 rounded-lg bg-[#27272a] flex items-center justify-center text-[#a1a1aa] shrink-0 mt-0.5">
                              <User className="w-4 h-4" />
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-start gap-3.5 w-full min-w-0">
                          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shrink-0 mt-0.5 shadow-[0_0_12px_rgba(56,189,248,0.12)]">
                            <Bot className="w-4 h-4" />
                          </div>
                          <div className="flex-1 min-w-0 text-xs text-[#e4e4e7] leading-relaxed">
                            <div className="prose prose-invert max-w-none text-xs">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  table: ({ node, ...props }) => (
                                    <div className="overflow-x-auto my-3 rounded-lg border border-[#27272a] bg-[#121215]/90">
                                      <table className="w-full text-left text-xs border-collapse" {...props} />
                                    </div>
                                  ),
                                  thead: ({ node, ...props }) => (
                                    <thead className="bg-[#18181b] text-[#f4f4f5] border-b border-[#27272a]" {...props} />
                                  ),
                                  th: ({ node, ...props }) => (
                                    <th className="px-3 py-2 text-xs font-semibold text-[#f4f4f5] border-b border-[#27272a]" {...props} />
                                  ),
                                  td: ({ node, ...props }) => (
                                    <td className="px-3 py-2 border-b border-[#27272a]/40 text-[#d4d4d8] font-mono text-[11px]" {...props} />
                                  ),
                                  p: ({ node, ...props }) => <p className="mb-2.5 leading-relaxed" {...props} />,
                                  ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2 space-y-1 text-[#d4d4d8]" {...props} />,
                                  ol: ({ node, ...props }) => <ol className="list-decimal pl-5 my-2 space-y-1 text-[#d4d4d8]" {...props} />,
                                  li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />,
                                  strong: ({ node, ...props }) => <strong className="font-semibold text-[#f4f4f5]" {...props} />,
                                  code: ({ node, inline, className, children, ...props }: any) => {
                                    if (inline) {
                                      return (
                                        <code className="bg-[#18181b] px-1.5 py-0.5 rounded text-[#38bdf8] font-mono text-[11px] border border-[#27272a]" {...props}>
                                          {children}
                                        </code>
                                      );
                                    }
                                    return (
                                      <div className="overflow-x-auto my-3 rounded-lg bg-[#121215] border border-[#27272a] p-3">
                                        <code className="font-mono text-[11px] text-[#38bdf8]" {...props}>
                                          {children}
                                        </code>
                                      </div>
                                    );
                                  },
                                  blockquote: ({ node, ...props }) => (
                                    <blockquote className="border-l-2 border-[#38bdf8] pl-3 py-1.5 my-2.5 text-[#a1a1aa] italic bg-[#38bdf8]/5 rounded-r" {...props} />
                                  ),
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}

                {isSending && (
                  <div className="flex items-start gap-3.5 w-full">
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="py-2.5 px-3.5 rounded-lg bg-[#121215] border border-[#27272a] text-xs text-[#a1a1aa] flex items-center gap-2.5">
                      <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping" />
                      <span>Consultando DuckDB e gerando raciocínio analítico...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Bar */}
            <div className="p-3 md:p-4 border-t border-[#27272a] bg-[#0c0d12]">
              <form
                onSubmit={e => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="max-w-4xl mx-auto flex items-center gap-2"
              >
                <input
                  type="text"
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  placeholder="Pergunte ao Copiloto (ex: Qual o impacto de liquidar a categoria Beleza?)..."
                  className="flex-1 bg-[#18181b] border border-[#27272a] rounded-lg px-4 py-2.5 text-xs text-[#f4f4f5] placeholder-[#71717a] focus:outline-none focus:border-[#38bdf8]/70 transition-colors shadow-inner"
                  disabled={isSending}
                />
                <button
                  type="submit"
                  disabled={!inputText.trim() || isSending}
                  className="px-4 py-2.5 rounded-lg bg-[#38bdf8] hover:bg-[#38bdf8]/90 text-[#09090b] font-semibold text-xs transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 shadow-sm"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Enviar</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: ROADMAP ESTRATÉGICO 30/60/90 DIAS */}
      {/* ========================================================================= */}
      {activeTab === 'roadmap' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={['vendas', 'atendimento', 'estoque', 'clientes', 'marketing']}
            scope="Síntese Executiva Transversal • 30 / 60 / 90 Dias"
            devSection="Conclusões & Quick Wins (Hipóteses 4, 5 e 6)"
          />

          {/* Roadmap Macro Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <MetricCard
              label="Total de Iniciativas Mapeadas"
              value={`${roadmapSummary?.total_initiatives || 7} Iniciativas`}
              subtitle="Plano estruturado de 90 dias"
            />
            <MetricCard
              label="Quick Wins Imediatos (30 Dias)"
              value={`${roadmapSummary?.quick_wins_count || 2} Ações de Alto Impacto`}
              trend={{ value: 'R$ 14,9M Potencial', isPositive: true }}
              subtitle="Rastreio WhatsApp + Liquidação Estoque"
              highlight
            />
            <MetricCard
              label="Valor Financeiro Mapeado"
              value={`R$ ${(((roadmapSummary?.total_potential_value || 24000000)) / 1e6).toFixed(1)}M`}
              subtitle="Redução de custos e liberação de caixa"
            />
          </div>

          {/* Horizon Filters */}
          <div className="flex items-center gap-2 p-3 rounded-lg bg-[#11131a] border border-[#27272a] flex-wrap">
            <span className="text-xs text-[#a1a1aa] font-medium mr-1">Filtrar Horizonte:</span>
            {['Todos', 'Quick Wins', '30 Dias', '60 Dias', '90 Dias'].map(horizon => {
              const active = selectedHorizon === horizon;
              return (
                <button
                  key={horizon}
                  onClick={() => setSelectedHorizon(horizon)}
                  className={`text-[11px] px-3 py-1 rounded border transition-colors ${active
                      ? 'bg-[#38bdf8]/15 border-[#38bdf8]/60 text-[#38bdf8] font-semibold'
                      : 'bg-[#18181b] border-[#27272a] text-[#a1a1aa] hover:border-[#3f3f46]'
                    }`}
                >
                  {horizon}
                </button>
              );
            })}
          </div>

          {/* Initiative Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredInitiatives.map(init => (
              <div
                key={init.id}
                className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] hover:border-[#3f3f46] transition-all flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-[#18181b] border border-[#27272a] text-[#38bdf8]">
                      {init.horizon}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${init.type.includes('Quick Win')
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : 'bg-[#18181b] text-[#a1a1aa] border border-[#27272a]'
                        }`}
                    >
                      {init.type}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-[#f4f4f5] tracking-tight mb-1">
                    {init.title}
                  </h4>
                  <div className="text-[11px] text-[#71717a] font-mono mb-2">
                    {init.hypothesis} • {init.category}
                  </div>

                  <p className="text-xs text-[#d4d4d8] leading-relaxed">
                    {init.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-[#27272a] flex items-center justify-between text-xs">
                  <div>
                    <span className="text-[10px] text-[#71717a] block">Impacto Financeiro Estimado:</span>
                    <span className="font-mono font-bold text-[#38bdf8]">
                      {init.financial_impact_label}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-[#71717a] block">Prazo Estimado:</span>
                    <span className="font-mono text-[#f4f4f5]">
                      {init.effort_days} dias
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
