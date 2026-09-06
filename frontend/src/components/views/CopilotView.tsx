import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../api/client';
import { ChatThread, ChatMessage } from '../../types/analytics';
import { MermaidDiagram } from '../common/MermaidDiagram';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Plus,
  Trash2,
  Sparkles,
  Bot,
  User,
} from 'lucide-react';

const SUGGESTED_PROMPTS = [
  'Qual o impacto financeiro de liquidar a categoria Beleza com 40% de desconto?',
  'Quais são os SKUs com maior capital imobilizado em produtos descontinuados?',
  'Quantos SKUs zerados temos e qual a concentração por categoria?',
  'Simule a queima de todo o estoque descontinuado com 30% de margem líquida.',
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

export const CopilotView: React.FC = () => {
  // Copilot Chat States
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load threads
  useEffect(() => {
    loadThreads();
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

  return (
    <div className="flex h-full w-full bg-[#09090b] overflow-hidden">
      {/* Threads Sidebar */}
      <div className="w-64 md:w-72 lg:w-80 shrink-0 border-r border-[#27272a] bg-[#11131a] flex flex-col h-full select-none">
        <div className="p-3.5 border-b border-[#27272a] bg-[#0d0d10]">
          <button
            onClick={handleNewThread}
            className="w-full py-2.5 px-3 rounded-lg bg-[#18181b] border border-[#27272a] hover:border-[#38bdf8]/50 text-[#f4f4f5] text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm hover:bg-[#202025]"
          >
            <Plus className="w-4 h-4 text-[#38bdf8]" />
            <span>Nova Conversa</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {threads.map(thread => (
            <div
              key={thread.id}
              onClick={() => selectThread(thread.id)}
              className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer text-xs transition-colors ${
                activeThreadId === thread.id
                  ? 'bg-[#18181b] border border-[#38bdf8]/40 text-[#f4f4f5] shadow-sm'
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

        <div className="p-3 border-t border-[#27272a] bg-[#0d0d10] text-[11px] font-mono text-[#71717a] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Memória ReAct • DuckDB Live</span>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 min-w-0 flex flex-col h-full bg-[#09090b]">
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-12 py-8 min-w-0">
          <div className="max-w-4xl mx-auto w-full space-y-8">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-20 px-4 space-y-5">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shadow-[0_0_30px_rgba(56,189,248,0.25)]">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-[#f4f4f5] font-sans tracking-tight">Copiloto de Estoque Vértice Retail</h3>
                  <p className="text-xs md:text-sm text-[#71717a] max-w-xl mt-2 font-sans leading-relaxed">
                    Assistente analítico conectado diretamente ao banco de dados DuckDB para diagnósticos, simulações de liquidação, investigação de SKUs e geração de cronogramas executivos.
                  </p>
                </div>

                {/* Quick Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl text-left mt-6">
                  {SUGGESTED_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="p-4 rounded-xl bg-[#121215] border border-[#27272a] hover:border-[#38bdf8]/50 text-xs text-[#d4d4d8] hover:text-[#f4f4f5] transition-all hover:bg-[#18181b] shadow-sm leading-relaxed"
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
                      <div className="flex items-start gap-3 max-w-[85%] md:max-w-[75%]">
                        <div className="rounded-2xl px-5 py-3 bg-[#2563eb]/20 border border-[#2563eb]/40 text-[#f4f4f5] text-[13.5px] leading-relaxed shadow-sm">
                          <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                        </div>
                        <div className="w-8 h-8 rounded-xl bg-[#27272a] flex items-center justify-center text-[#a1a1aa] shrink-0 mt-0.5 shadow-sm">
                          <User className="w-4 h-4" />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-4 w-full min-w-0">
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shrink-0 mt-0.5 shadow-[0_0_16px_rgba(56,189,248,0.15)]">
                        <Bot className="w-4.5 h-4.5" />
                      </div>
                      <div className="flex-1 min-w-0 text-[13.5px] text-[#d4d4d8] leading-relaxed">
                        <div className="prose prose-invert max-w-none text-[13.5px]">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h1: ({ node, ...props }) => (
                                <h1 className="text-lg md:text-xl font-bold text-[#38bdf8] mt-6 mb-3 pb-2 border-b border-[#27272a] font-sans tracking-tight" {...props} />
                              ),
                              h2: ({ node, ...props }) => (
                                <h2 className="text-base md:text-lg font-semibold text-[#f4f4f5] mt-5 mb-2.5 font-sans tracking-tight" {...props} />
                              ),
                              h3: ({ node, ...props }) => (
                                <h3 className="text-sm md:text-base font-semibold text-[#38bdf8]/90 mt-4 mb-2 font-sans tracking-tight" {...props} />
                              ),
                              h4: ({ node, ...props }) => (
                                <h4 className="text-xs md:text-sm font-semibold text-[#e4e4e7] mt-3 mb-1.5 font-sans" {...props} />
                              ),
                              p: ({ node, ...props }) => <p className="mb-3.5 leading-relaxed text-[13.5px] text-[#d4d4d8]" {...props} />,
                              ul: ({ node, ...props }) => <ul className="list-disc pl-6 my-3 space-y-1.5 text-[13.5px] text-[#d4d4d8]" {...props} />,
                              ol: ({ node, ...props }) => <ol className="list-decimal pl-6 my-3 space-y-1.5 text-[13.5px] text-[#d4d4d8]" {...props} />,
                              li: ({ node, ...props }) => <li className="leading-relaxed pl-1" {...props} />,
                              strong: ({ node, ...props }) => <strong className="font-semibold text-[#f4f4f5]" {...props} />,
                              table: ({ node, ...props }) => (
                                <div className="overflow-x-auto my-4 rounded-xl border border-[#27272a] bg-[#11131a] shadow-md">
                                  <table className="w-full text-left text-xs border-collapse" {...props} />
                                </div>
                              ),
                              thead: ({ node, ...props }) => (
                                <thead className="bg-[#18181b] text-[#f4f4f5] border-b border-[#27272a]" {...props} />
                              ),
                              th: ({ node, ...props }) => (
                                <th className="px-3.5 py-2.5 text-xs font-semibold text-[#f4f4f5] border-b border-[#27272a]" {...props} />
                              ),
                              td: ({ node, ...props }) => (
                                <td className="px-3.5 py-2.5 border-b border-[#27272a]/40 text-[#d4d4d8] font-mono text-[12px]" {...props} />
                              ),
                              code: ({ node, inline, className, children, ...props }: any) => {
                                const codeContent = String(children).replace(/\n$/, '');
                                if (!inline && isMermaidContent(codeContent, className)) {
                                  return <MermaidDiagram chart={codeContent} />;
                                }
                                if (inline) {
                                  return (
                                    <code className="bg-[#18181b] px-1.5 py-0.5 rounded-md text-[#38bdf8] font-mono text-[12px] border border-[#27272a]" {...props}>
                                      {children}
                                    </code>
                                  );
                                }
                                return (
                                  <div className="overflow-x-auto my-4 rounded-xl bg-[#11131a] border border-[#27272a] p-4 shadow-sm">
                                    <code className="font-mono text-xs text-[#38bdf8] leading-relaxed whitespace-pre-wrap" {...props}>
                                      {children}
                                    </code>
                                  </div>
                                );
                              },
                              blockquote: ({ node, ...props }) => (
                                <blockquote className="border-l-2 border-[#38bdf8] pl-4 py-2 my-3 text-[#a1a1aa] italic bg-[#38bdf8]/5 rounded-r-lg" {...props} />
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
              <div className="flex items-start gap-4 w-full">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#38bdf8]/20 to-[#818cf8]/20 border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8] shrink-0 shadow-[0_0_16px_rgba(56,189,248,0.15)]">
                  <Bot className="w-4.5 h-4.5" />
                </div>
                <div className="py-3 px-4 rounded-xl bg-[#121215] border border-[#27272a] text-xs md:text-[13px] text-[#a1a1aa] flex items-center gap-3 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping" />
                  <span>Consultando DuckDB e gerando raciocínio analítico...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Bar Fixed at Bottom */}
        <div className="p-4 md:p-5 border-t border-[#27272a] bg-[#0c0d12] shrink-0 shadow-2xl">
          <form
            onSubmit={e => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="max-w-4xl mx-auto flex items-center gap-2.5"
          >
            <input
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Pergunte ao Copiloto (ex: Qual o impacto de liquidar a categoria Beleza?)..."
              className="flex-1 bg-[#18181b] border border-[#27272a] rounded-xl px-4 py-3 text-sm text-[#f4f4f5] placeholder-[#71717a] focus:outline-none focus:border-[#38bdf8]/70 transition-colors shadow-inner"
              disabled={isSending}
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isSending}
              className="px-5 py-3 rounded-xl bg-[#38bdf8] hover:bg-[#38bdf8]/90 text-[#09090b] font-semibold text-xs md:text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 shadow-md hover:shadow-[0_0_15px_rgba(56,189,248,0.3)]"
            >
              <Send className="w-4 h-4" />
              <span>Enviar</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
