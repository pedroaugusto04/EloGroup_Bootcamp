import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../api/client';
import { ChatThread, ChatMessage, PeriodMeta } from '../../types/analytics';
import { InventoryCopilotIcon } from '../common/InventoryCopilotIcon';
import { MermaidDiagram } from '../common/MermaidDiagram';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Plus,
  Trash2,
  User,
  Mail,
} from 'lucide-react';

const SUGGESTED_PROMPTS = [
  'Quais são os SKUs ativos com maior capital imobilizado em sobre-estoque?',
  'Qual o impacto financeiro de liquidar a categoria Moda com 30% de desconto?',
  'Quais categorias e SKUs apresentam maior margem exposta a risco de ruptura?',
  'Quantos SKUs zerados temos e qual a concentração por categoria?',
];

const isMermaidContent = (content: string, className?: string) => {
  if (className && className.includes('language-mermaid')) return true;
  const trimmed = content.trim();
  return (
    /^timeline\b/.test(trimmed) ||
    /^graph\s+/.test(trimmed) ||
    /^flowchart\s+/.test(trimmed) ||
    /^sequenceDiagram\b/.test(trimmed) ||
    /^gantt\b/.test(trimmed) ||
    /^pie\b/.test(trimmed) ||
    /^classDiagram\b/.test(trimmed) ||
    /^erDiagram\b/.test(trimmed) ||
    /^stateDiagram\b/.test(trimmed)
  );
};

interface CopilotViewProps {
  initialThreadId?: string | null;
  onOpenAuditModal?: () => void;
}

export const CopilotView: React.FC<CopilotViewProps> = ({ initialThreadId, onOpenAuditModal }) => {
  // Copilot Chat States
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [periods, setPeriods] = useState<PeriodMeta[]>([]);
  const [showThreadsMobile, setShowThreadsMobile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load threads and automatically resolve thread from URL or Email Deep Link
  useEffect(() => {
    loadThreads();
    api.getCopilotPeriods().then(res => setPeriods(res.periods || [])).catch(() => setPeriods([]));
  }, [initialThreadId]);

  const loadThreads = async () => {
    try {
      const res = await api.listThreads();
      const list = res.threads || [];
      setThreads(list);

      // Determina o thread_id prioritário (da prop, da URL ou do último snapshot se source=email)
      const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
      let targetId = initialThreadId || urlParams?.get('thread_id') || urlParams?.get('thread') || urlParams?.get('threadId');

      if (!targetId && urlParams?.get('source') === 'email') {
        try {
          const auditRes = await api.getLatestAudit();
          if (auditRes?.snapshot?.audit_thread_id) {
            targetId = auditRes.snapshot.audit_thread_id;
          }
        } catch {
          // ignore
        }
      }

      if (targetId) {
        const found = list.find(t => t.id === targetId);
        if (found) {
          selectThread(targetId);
          return;
        }

        // Tenta buscar thread diretamente no backend caso não esteja na lista inicial
        try {
          const directThreadRes = await api.getThread(targetId);
          if (directThreadRes?.thread) {
            setThreads(prev => [directThreadRes.thread, ...prev.filter(t => t.id !== targetId)]);
            setActiveThreadId(targetId);
            setMessages(directThreadRes.thread.messages || []);
            return;
          }
        } catch (err) {
          console.warn(`Thread ${targetId} não encontrada diretamente, fallback para lista padrão.`);
        }
      }

      if (list.length > 0 && !activeThreadId) {
        selectThread(list[0].id);
      } else if (list.length === 0) {
        handleNewThread();
      }
    } catch (err) {
      console.error('Erro ao carregar threads:', err);
    }
  };

  const selectThread = async (id: string) => {
    setActiveThreadId(id);
    setShowThreadsMobile(false);

    // Atualiza a URL com o thread_id ativo sem recarregar a página
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('view', 'copilot');
      url.searchParams.set('thread_id', id);
      window.history.replaceState({}, '', url.toString());
    } catch {
      // ignore
    }

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
      setShowThreadsMobile(false);
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
          content: 'Desculpe, ocorreu um erro ao consultar o agente analítico. Verifique a conexão com o backend.',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const activeThread = threads.find(t => t.id === activeThreadId);

  return (
    <div className="relative flex h-full w-full bg-[#faf9fc] dark:bg-[#0a0914] overflow-hidden">
      {/* Mobile Backdrop for Threads Drawer */}
      {showThreadsMobile && (
        <div
          onClick={() => setShowThreadsMobile(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-30 md:hidden transition-opacity"
        />
      )}

      {/* Threads Sidebar */}
      <div
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 sm:w-80 md:w-64 lg:w-72 shrink-0 border-r border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#121024] flex flex-col h-full select-none transform transition-transform duration-300 ease-in-out ${showThreadsMobile ? 'translate-x-0 shadow-2xl' : '-translate-x-full md:translate-x-0'
          }`}
      >
        <div className="p-3 sm:p-3.5 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#f8f7fc] dark:bg-[#0d0b1a] flex flex-col gap-2">
          <button
            onClick={handleNewThread}
            className="w-full py-2 px-3 rounded-lg bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#4200db]/50 dark:hover:border-[#8575ff]/50 text-[#131920] dark:text-[#f4f4f5] text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm hover:bg-[#f0edff] dark:hover:bg-[#201c3e] active:scale-95"
          >
            <Plus className="w-4 h-4 text-[#4200db] dark:text-[#8575ff]" />
            <span>Nova Conversa</span>
          </button>
          {onOpenAuditModal && (
            <button
              onClick={onOpenAuditModal}
              className="w-full py-1.5 px-3 rounded-lg bg-[#e8e6ff] dark:bg-[#8575ff]/10 border border-[#c4b8ff] dark:border-[#8575ff]/30 hover:bg-[#dedaff] dark:hover:bg-[#8575ff]/20 text-[#4200db] dark:text-[#8575ff] text-xs font-medium flex items-center justify-center gap-2 transition-all shadow-sm active:scale-95"
            >
              <Mail className="w-3.5 h-3.5" />
              <span>Gerar Auditoria</span>
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {threads.map(thread => (
            <div
              key={thread.id}
              onClick={() => selectThread(thread.id)}
              className={`group flex items-center justify-between p-2.5 sm:p-3 rounded-lg cursor-pointer text-xs transition-colors ${activeThreadId === thread.id
                ? 'bg-[#e8e6ff] dark:bg-[#181530] border border-[#c4b8ff] dark:border-[#8575ff]/40 text-[#4200db] dark:text-[#f4f4f5] font-semibold shadow-sm'
                : 'hover:bg-[#f8f7fc] dark:hover:bg-[#181530]/60 text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5] border border-transparent'
                }`}
            >
              <span className="truncate flex-1 font-medium">{thread.title || 'Conversa'}</span>
              <button
                onClick={e => handleDeleteThread(thread.id, e)}
                className="opacity-70 md:opacity-0 group-hover:opacity-100 p-1 rounded hover:text-rose-500 dark:hover:text-rose-400 transition-opacity ml-1"
                title="Excluir conversa"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>

        <div className="p-3 border-t border-[#e6e5f0] dark:border-[#262046] bg-[#f8f7fc] dark:bg-[#0d0b1a] text-[11px] font-mono text-[#5e6270] dark:text-[#71717a] flex items-center justify-between">
          <span className="text-[10px] text-[#5e6270] dark:text-[#52525b]">{threads.length} chats</span>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 min-w-0 flex flex-col h-full bg-[#faf9fc] dark:bg-[#0a0914]">
        <div className="px-3 sm:px-6 py-2 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#e8e6ff]/40 dark:bg-[#8575ff]/5 text-[10px] sm:text-[11px] text-[#5e6270] dark:text-[#a1a1aa] leading-relaxed">
          {periods[0]
            ? `Tendência de vendas observada entre ${periods[0].sales_start.split('-').reverse().join('/')} e ${periods[0].sales_end.split('-').reverse().join('/')}.`
            : ''}
        </div>
        {/* Mobile Top Sub-Header */}
        <div className="md:hidden flex items-center justify-between px-3 py-2 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff]/90 dark:bg-[#0d0b1a]/80 text-xs">
          <button
            onClick={() => setShowThreadsMobile(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-[#4200db] dark:text-[#8575ff] font-medium"
          >
            <span>Conversas ({threads.length})</span>
          </button>
          <span className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] truncate max-w-[180px]">
            {activeThread?.title || 'Chat IA'}
          </span>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto px-3 sm:px-6 md:px-12 py-4 sm:py-8 min-w-0">
          <div className="max-w-4xl mx-auto w-full space-y-6 sm:space-y-8">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-10 sm:py-20 px-2 sm:px-4 space-y-4 sm:space-y-5">
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-[#4200db]/15 to-[#8575ff]/25 dark:from-[#4200db]/30 dark:to-[#8575ff]/30 border border-[#4200db]/30 dark:border-[#8575ff]/50 flex items-center justify-center text-[#4200db] dark:text-[#8575ff] shadow-[0_0_30px_rgba(66,0,219,0.15)] dark:shadow-[0_0_30px_rgba(66,0,219,0.3)]">
                  <InventoryCopilotIcon className="w-12 h-12 sm:w-14 sm:h-14" />
                </div>
                <div>
                  <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5] font-sans tracking-tight">Predictive Inventory Advisor</h3>
                  <p className="text-xs sm:text-sm text-[#5e6270] dark:text-[#71717a] max-w-xl mt-1.5 sm:mt-2 font-sans leading-relaxed">
                    Analisa o histórico de vendas para avaliar a saúde do estoque, antecipar riscos de ruptura ou excesso e sugerir ações de reposição ou liquidação.
                  </p>
                </div>

                {/* Quick Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 w-full max-w-2xl text-left mt-4 sm:mt-6">
                  {SUGGESTED_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="p-3 sm:p-4 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#4200db]/50 dark:hover:border-[#8575ff]/50 text-xs text-[#40434f] dark:text-[#d4d4d8] hover:text-[#131920] dark:hover:text-[#f4f4f5] transition-all hover:bg-[#f8f7fc] dark:hover:bg-[#181530] shadow-sm leading-relaxed text-left active:scale-[0.99]"
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
                    <div className="flex flex-col items-end gap-1 w-full">
                      <div className="flex items-start gap-2 sm:gap-3 max-w-[92%] sm:max-w-[80%]">
                        <div className="rounded-2xl px-3.5 sm:px-5 py-2.5 sm:py-3 bg-[#e8e6ff] dark:bg-[#4200db]/30 border border-[#c4b8ff] dark:border-[#8575ff]/40 text-[#131920] dark:text-[#f4f4f5] text-xs sm:text-[13.5px] leading-relaxed shadow-sm">
                          <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                        </div>
                        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#e8e6ff] dark:bg-[#262046] flex items-center justify-center text-[#4200db] dark:text-[#a1a1aa] shrink-0 mt-0.5 shadow-sm">
                          <User className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2.5 sm:gap-4 w-full min-w-0">
                      <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-gradient-to-br from-[#4200db]/15 to-[#8575ff]/25 dark:from-[#4200db]/30 dark:to-[#8575ff]/30 border border-[#4200db]/30 dark:border-[#8575ff]/50 flex items-center justify-center text-[#4200db] dark:text-[#8575ff] shrink-0 mt-0.5 shadow-[0_0_16px_rgba(66,0,219,0.1)] dark:shadow-[0_0_16px_rgba(133,117,255,0.2)]">
                        <InventoryCopilotIcon className="w-7 h-7 sm:w-8 sm:h-8" />
                      </div>
                      <div className="flex-1 min-w-0 text-xs sm:text-[13.5px] text-[#2d3142] dark:text-[#d4d4d8] leading-relaxed overflow-hidden">
                        <div className="prose dark:prose-invert max-w-none text-xs sm:text-[13.5px]">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h1: ({ node, ...props }) => (
                                <h1 className="text-base sm:text-xl font-bold text-[#4200db] dark:text-[#8575ff] mt-4 sm:mt-6 mb-2 sm:mb-3 pb-1.5 border-b border-[#e6e5f0] dark:border-[#262046] font-sans tracking-tight" {...props} />
                              ),
                              h2: ({ node, ...props }) => (
                                <h2 className="text-sm sm:text-lg font-semibold text-[#131920] dark:text-[#f4f4f5] mt-3 sm:mt-5 mb-2 font-sans tracking-tight" {...props} />
                              ),
                              h3: ({ node, ...props }) => (
                                <h3 className="text-xs sm:text-base font-semibold text-[#4200db] dark:text-[#8575ff]/90 mt-3 sm:mt-4 mb-1.5 font-sans tracking-tight" {...props} />
                              ),
                              h4: ({ node, ...props }) => (
                                <h4 className="text-xs sm:text-sm font-semibold text-[#131920] dark:text-[#e4e4e7] mt-2 sm:mt-3 mb-1 font-sans" {...props} />
                              ),
                              p: ({ node, ...props }) => <p className="mb-2.5 sm:mb-3.5 leading-relaxed text-xs sm:text-[13.5px] text-[#2d3142] dark:text-[#d4d4d8]" {...props} />,
                              ul: ({ node, ...props }) => <ul className="list-disc pl-4 sm:pl-6 my-2 sm:my-3 space-y-1 text-xs sm:text-[13.5px] text-[#2d3142] dark:text-[#d4d4d8]" {...props} />,
                              ol: ({ node, ...props }) => <ol className="list-decimal pl-4 sm:pl-6 my-2 sm:my-3 space-y-1 text-xs sm:text-[13.5px] text-[#2d3142] dark:text-[#d4d4d8]" {...props} />,
                              li: ({ node, ...props }) => <li className="leading-relaxed pl-0.5" {...props} />,
                              strong: ({ node, ...props }) => <strong className="font-semibold text-[#131920] dark:text-[#f4f4f5]" {...props} />,
                              table: ({ node, ...props }) => (
                                <div className="overflow-x-auto my-3 sm:my-4 rounded-xl border border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#131126] shadow-md touch-pan-x">
                                  <table className="w-full text-left text-[11px] sm:text-xs border-collapse min-w-[300px]" {...props} />
                                </div>
                              ),
                              thead: ({ node, ...props }) => (
                                <thead className="bg-[#f8f7fc] dark:bg-[#181530] text-[#131920] dark:text-[#f4f4f5] border-b border-[#e6e5f0] dark:border-[#262046]" {...props} />
                              ),
                              th: ({ node, ...props }) => (
                                <th className="px-2.5 sm:px-3.5 py-2 sm:py-2.5 font-semibold text-[#131920] dark:text-[#f4f4f5] border-b border-[#e6e5f0] dark:border-[#262046]" {...props} />
                              ),
                              td: ({ node, ...props }) => (
                                <td className="px-2.5 sm:px-3.5 py-2 sm:py-2.5 border-b border-[#e6e5f0] dark:border-[#262046]/40 text-[#40434f] dark:text-[#d4d4d8] font-mono text-[11px] sm:text-[12px]" {...props} />
                              ),
                              code: ({ node, inline, className, children, ...props }: any) => {
                                const codeContent = String(children).replace(/\n$/, '');
                                if (!inline && isMermaidContent(codeContent, className)) {
                                  return <MermaidDiagram chart={codeContent} />;
                                }
                                if (inline) {
                                  return (
                                    <code className="bg-[#f8f7fc] dark:bg-[#181530] px-1 py-0.5 rounded text-[#4200db] dark:text-[#8575ff] font-mono text-[11px] sm:text-[12px] border border-[#e6e5f0] dark:border-[#262046]" {...props}>
                                      {children}
                                    </code>
                                  );
                                }
                                return (
                                  <div className="overflow-x-auto my-3 sm:my-4 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] p-3 sm:p-4 shadow-sm">
                                    <code className="font-mono text-[11px] sm:text-xs text-[#4200db] dark:text-[#8575ff] leading-relaxed whitespace-pre-wrap" {...props}>
                                      {children}
                                    </code>
                                  </div>
                                );
                              },
                              blockquote: ({ node, ...props }) => (
                                <blockquote className="border-l-2 border-[#4200db] dark:border-[#8575ff] pl-3 sm:pl-4 py-1.5 my-2.5 text-[#5e6270] dark:text-[#a1a1aa] italic bg-[#e8e6ff]/30 dark:bg-[#8575ff]/5 rounded-r-lg" {...props} />
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
              <div className="flex items-start gap-2.5 sm:gap-4 w-full">
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-gradient-to-br from-[#4200db]/15 to-[#8575ff]/25 dark:from-[#4200db]/30 dark:to-[#8575ff]/30 border border-[#4200db]/30 dark:border-[#8575ff]/50 flex items-center justify-center text-[#4200db] dark:text-[#8575ff] shrink-0 shadow-[0_0_16px_rgba(66,0,219,0.1)] dark:shadow-[0_0_16px_rgba(133,117,255,0.2)]">
                  <InventoryCopilotIcon className="w-7 h-7 sm:w-8 sm:h-8" />
                </div>
                <div className="py-2.5 sm:py-3 px-3.5 sm:px-4 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] text-xs sm:text-[13px] text-[#5e6270] dark:text-[#a1a1aa] flex items-center gap-2.5 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-[#4200db] dark:bg-[#8575ff] animate-ping" />
                  <span>Consultando as bases e gerando raciocínio...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Bar Fixed at Bottom */}
        <div className="p-3 sm:p-4 md:p-5 border-t border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#0d0b1a] shrink-0 shadow-2xl">
          <form
            onSubmit={e => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="max-w-4xl mx-auto flex items-center gap-2 sm:gap-2.5"
          >
            <input
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Pergunte ao Copiloto (ex: liquidar Beleza?)..."
              className="flex-1 bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] rounded-xl px-3.5 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm text-[#131920] dark:text-[#f4f4f5] placeholder-[#71717a] focus:outline-none focus:border-[#4200db] dark:focus:border-[#8575ff]/70 transition-colors shadow-inner"
              disabled={isSending}
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isSending}
              className="px-3.5 sm:px-5 py-2.5 sm:py-3 rounded-xl bg-[#4200db] hover:bg-[#35009e] text-[#ffffff] font-semibold text-xs sm:text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 sm:gap-2 shadow-md shadow-[#4200db]/30 hover:shadow-[0_0_15px_rgba(66,0,219,0.3)] active:scale-95 shrink-0"
            >
              <Send className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Enviar</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
