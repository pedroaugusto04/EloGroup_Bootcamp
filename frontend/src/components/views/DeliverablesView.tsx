import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  Eye,
  Edit3,
  Columns,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  BookOpen,
  Copy,
  Check,
  Download,
  Archive,
  ChevronRight,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { api } from '../../api/client';
import { DeliverableMeta, DeliverableDetail } from '../../types/analytics';
import { ScopeBadge } from '../common/ScopeBadge';

const arvoreHipotesesSvg = new URL('../../assets/arvore_hipoteses.svg', import.meta.url).href;

type ViewMode = 'preview' | 'edit' | 'split';

export const DeliverablesView: React.FC = () => {
  const [deliverables, setDeliverables] = useState<DeliverableMeta[]>([]);
  const [selectedId, setSelectedId] = useState<string>('01_relatorio_diagnostico_estrategico');
  const [currentDetail, setCurrentDetail] = useState<DeliverableDetail | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('preview');
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDoc, setLoadingDoc] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const isDirty = editedContent !== originalContent;

  useEffect(() => {
    loadDeliverablesList();
  }, []);

  useEffect(() => {
    if (selectedId) {
      loadDeliverableContent(selectedId);
    }
  }, [selectedId]);

  const loadDeliverablesList = async () => {
    try {
      setLoadingList(true);
      const list = await api.getDeliverables();
      setDeliverables(list);
      if (list.length > 0 && (!selectedId || !list.some(d => d.id === selectedId))) {
        setSelectedId(list[0].id);
      }
    } catch (err) {
      console.error('Erro ao carregar lista de entregáveis:', err);
      showToast('error', 'Não foi possível carregar os entregáveis.');
    } finally {
      setLoadingList(false);
    }
  };

  const loadDeliverableContent = async (id: string) => {
    try {
      setLoadingDoc(true);
      const doc = await api.getDeliverable(id);
      setCurrentDetail(doc);
      setEditedContent(doc.content);
      setOriginalContent(doc.content);
    } catch (err) {
      console.error(`Erro ao carregar entregável ${id}:`, err);
      showToast('error', 'Erro ao carregar o conteúdo do documento.');
    } finally {
      setLoadingDoc(false);
    }
  };

  const handleSave = async () => {
    if (!selectedId || saving || !isDirty) return;
    try {
      setSaving(true);
      const updated = await api.updateDeliverable(selectedId, editedContent);
      setCurrentDetail(updated);
      setOriginalContent(updated.content);
      setEditedContent(updated.content);
      setDeliverables(prev =>
        prev.map(item => (item.id === selectedId ? { ...item, word_count: updated.word_count, updated_at: updated.updated_at } : item))
      );
      showToast('success', `Documento "${updated.title}" salvo com sucesso!`);
    } catch (err) {
      console.error('Erro ao salvar documento:', err);
      showToast('error', 'Falha ao salvar as alterações.');
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setEditedContent(originalContent);
    showToast('success', 'Alterações descartadas.');
  };

  const handleDownloadSingle = (docId: string, filename?: string) => {
    if (docId === selectedId && isDirty && editedContent) {
      const blob = new Blob([editedContent], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `${docId}.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToast('success', `Download de ${filename || docId} concluído.`);
      return;
    }

    const link = document.createElement('a');
    link.href = api.getDeliverableDownloadUrl(docId);
    link.download = filename || `${docId}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('success', `Download de ${filename || docId} iniciado.`);
  };

  const handleDownloadZip = () => {
    const link = document.createElement('a');
    link.href = api.getDeliverablesZipUrl();
    link.download = 'vertice-documentos-executivos.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('success', 'Download do pacote .ZIP iniciado.');
  };

  const showToast = (type: 'success' | 'error', text: string) => {
    setToastMessage({ type, text });
    setTimeout(() => {
      setToastMessage(null);
    }, 3500);
  };

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (isDirty) {
          handleSave();
        }
      }
    },
    [isDirty, editedContent, selectedId]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleEditorKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = textarea.value;
      const newValue = value.substring(0, start) + '  ' + value.substring(end);
      setEditedContent(newValue);
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    }
  };

  const wordCount = editedContent.trim() ? editedContent.trim().split(/\s+/).length : 0;
  const charCount = editedContent.length;

  if (loadingList) {
    return (
      <div className="space-y-6 view-enter animate-pulse">
        <div className="h-10 bg-[#e6e5f0]/60 dark:bg-[#262046]/60 rounded-xl w-full" />
        <div className="h-14 bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] rounded-2xl w-full" />
        <div className="h-96 rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046]" />
      </div>
    );
  }

  return (
    <div className="space-y-6 view-enter">
      {/* ScopeBadge and Global ZIP Download Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <ScopeBadge
          tables={['vendas', 'estoque', 'atendimento', 'marketing', 'clientes']}
          scope="Documentos de Entrega do Case"
          devSection=""
        />
        <button
          onClick={handleDownloadZip}
          className="inline-flex items-center justify-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#f4f2ff] hover:bg-[#e8e4fd] dark:bg-[#8575ff]/15 dark:hover:bg-[#8575ff]/25 border border-[#4200db]/30 dark:border-[#8575ff]/40 text-[#4200db] dark:text-[#8575ff] text-xs font-bold transition-all shadow-xs shrink-0 self-start sm:self-auto"
          title="Baixar todos os documentos em arquivo .ZIP"
        >
          <Archive className="w-4 h-4" />
          <span>Baixar Todos (.ZIP)</span>
        </button>
      </div>

      {toastMessage && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg border text-sm font-medium transition-all duration-300 animate-fadeIn ${toastMessage.type === 'success'
            ? 'bg-[#f4f2ff] dark:bg-[#1f193d] border-[#4200db]/30 dark:border-[#8575ff]/40 text-[#4200db] dark:text-[#8575ff]'
            : 'bg-red-50 dark:bg-red-950/80 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300'
            }`}
        >
          {toastMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-[#4200db] dark:text-[#8575ff]" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600 dark:text-red-400" />
          )}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Tabs Navigation for Deliverables */}
      <div className="p-1.5 sm:p-2 rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
        <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar">
          {deliverables.map(doc => {
            const isSelected = selectedId === doc.id;
            return (
              <div
                key={doc.id}
                onClick={() => {
                  if (isDirty) {
                    if (window.confirm('Existem alterações não salvas. Deseja trocar de documento e descartar?')) {
                      setSelectedId(doc.id);
                    }
                  } else {
                    setSelectedId(doc.id);
                  }
                }}
                className={`flex-1 min-w-[200px] sm:min-w-[230px] p-2.5 sm:p-3 rounded-xl border text-left transition-all duration-200 cursor-pointer ${isSelected
                  ? 'bg-[#f4f2ff] dark:bg-[#1a1636] border-[#4200db]/40 dark:border-[#8575ff]/50 shadow-sm'
                  : 'bg-transparent border-transparent hover:bg-[#faf9fe] dark:hover:bg-[#181530] text-[#5e6270] dark:text-[#a1a1aa]'
                  }`}
              >
                <div className="flex items-center justify-between gap-1.5 mb-1">
                  <span
                    className={`text-xs font-bold truncate ${isSelected ? 'text-[#4200db] dark:text-[#8575ff]' : 'text-[#131920] dark:text-[#f4f4f5]'
                      }`}
                  >
                    {doc.title}
                  </span>
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownloadSingle(doc.id, doc.filename);
                      }}
                      className="p-1 rounded-md hover:bg-slate-200/80 dark:hover:bg-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#4200db] dark:hover:text-[#8575ff] transition-colors"
                      title={`Baixar ${doc.filename}`}
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${isSelected
                        ? 'bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] border-[#4200db]/30 dark:border-[#8575ff]/40 font-bold'
                        : 'bg-[#e6e5f0]/50 dark:bg-[#262046]/50 text-[#5e6270] dark:text-[#71717a] border-transparent'
                        }`}
                    >
                      {doc.tag}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-[#5e6270] dark:text-[#71717a]">
                  <span className="line-clamp-1 truncate max-w-[150px]">{doc.subtitle}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Workspace Card */}
      <div className="rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm flex flex-col min-h-[600px] overflow-hidden">
        {/* Workspace Toolbar */}
        <div className="p-4 sm:p-5 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#faf9fe]/60 dark:bg-[#15122b]/60 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] font-bold">
                {currentDetail?.tag || 'Doc'}
              </span>
              <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5] truncate">
                {currentDetail?.title || 'Carregando...'}
              </h3>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-[#5e6270] dark:text-[#a1a1aa]">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {currentDetail ? new Date(currentDetail.updated_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '-'}
              </span>
              <span>•</span>
              <span>{wordCount} palavras</span>
              {isDirty && (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-800">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                  Não salvo
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => handleDownloadSingle(currentDetail?.id || selectedId, currentDetail?.filename)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-xl border border-[#e6e5f0] dark:border-[#262046] text-[#4200db] dark:text-[#8575ff] bg-[#ffffff] dark:bg-[#181530] hover:bg-[#f4f2ff] dark:hover:bg-[#251f47] font-semibold transition-all shadow-xs"
              title="Baixar arquivo Markdown (.md)"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Baixar (.md)</span>
            </button>

            <div className="inline-flex p-1 rounded-xl bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
              <button
                onClick={() => setViewMode('preview')}
                className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg font-semibold transition-all ${viewMode === 'preview'
                  ? 'bg-[#f4f2ff] dark:bg-[#251f47] text-[#4200db] dark:text-[#8575ff] shadow-xs'
                  : 'text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                  }`}
                title="Modo de Leitura"
              >
                <Eye className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Visualizar</span>
              </button>
              <button
                onClick={() => setViewMode('edit')}
                className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg font-semibold transition-all ${viewMode === 'edit'
                  ? 'bg-[#f4f2ff] dark:bg-[#251f47] text-[#4200db] dark:text-[#8575ff] shadow-xs'
                  : 'text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                  }`}
                title="Modo de Edição"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Editar</span>
              </button>
              <button
                onClick={() => setViewMode('split')}
                className={`hidden lg:flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg font-semibold transition-all ${viewMode === 'split'
                  ? 'bg-[#f4f2ff] dark:bg-[#251f47] text-[#4200db] dark:text-[#8575ff] shadow-xs'
                  : 'text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                  }`}
                title="Lado a Lado"
              >
                <Columns className="w-3.5 h-3.5" />
                <span>Lado a Lado</span>
              </button>
            </div>

            {isDirty && (
              <button
                onClick={handleDiscard}
                disabled={saving}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-xl border border-[#e6e5f0] dark:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
                title="Descartar alterações"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Descartar</span>
              </button>
            )}

            <button
              onClick={handleSave}
              disabled={!isDirty || saving}
              className={`flex items-center gap-1.5 text-xs px-3.5 py-1.5 rounded-xl font-bold transition-all shadow-sm ${isDirty
                ? 'bg-[#4200db] hover:bg-[#3400b0] text-white active:scale-95 cursor-pointer shadow-[#4200db]/20'
                : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed'
                }`}
              title="Salvar alterações (Ctrl+S)"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{saving ? 'Salvando...' : 'Salvar'}</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 min-h-[500px] flex flex-col">
          {loadingDoc ? (
            <div className="p-8 space-y-4 animate-pulse">
              <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-2/3" />
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/2" />
              <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded w-full mt-6" />
            </div>
          ) : (
            <div className="flex-1 flex flex-col lg:flex-row min-h-0">
              {/* Editor Pane */}
              {(viewMode === 'edit' || viewMode === 'split') && (
                <div
                  className={`flex flex-col border-b lg:border-b-0 border-[#e6e5f0] dark:border-[#262046] ${viewMode === 'split' ? 'w-full lg:w-1/2 lg:border-r' : 'w-full flex-1'
                    }`}
                >
                  <div className="px-4 py-2 bg-[#f8f7fc] dark:bg-[#100e21] border-b border-[#e6e5f0] dark:border-[#262046] flex items-center justify-between text-[11px] text-[#5e6270] dark:text-[#71717a]">
                    <span className="font-mono font-semibold uppercase">Editor Markdown</span>
                    <span className="font-mono">Tab (2 espaços) • Ctrl+S salva</span>
                  </div>
                  <textarea
                    value={editedContent}
                    onChange={e => setEditedContent(e.target.value)}
                    onKeyDown={handleEditorKeyDown}
                    placeholder="Digite o conteúdo em Markdown..."
                    spellCheck={false}
                    className="flex-1 w-full p-4 sm:p-6 font-mono text-xs sm:text-sm bg-[#faf9fe] dark:bg-[#0c0a1a] text-[#131920] dark:text-[#f4f4f5] focus:outline-hidden resize-none leading-relaxed min-h-[500px]"
                  />
                  <div className="px-4 py-2 border-t border-[#e6e5f0] dark:border-[#262046] bg-[#f8f7fc] dark:bg-[#100e21] flex items-center justify-between text-[11px] font-mono text-[#5e6270] dark:text-[#71717a]">
                    <span>Linhas: {editedContent.split('\n').length}</span>
                    <span>Caracteres: {charCount}</span>
                  </div>
                </div>
              )}

              {/* Preview Pane */}
              {(viewMode === 'preview' || viewMode === 'split') && (
                <div
                  className={`flex-1 overflow-y-auto p-5 sm:p-8 md:p-10 bg-[#ffffff] dark:bg-[#131126] ${viewMode === 'split' ? 'w-full lg:w-1/2' : 'w-full'
                    }`}
                >
                  <div className="max-w-4xl mx-auto space-y-4">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        h1: ({ node, ...props }) => (
                          <h1
                            className="text-xl sm:text-2xl md:text-3xl font-extrabold text-[#131920] dark:text-[#f4f4f5] pb-3 mb-4 border-b border-[#e6e5f0] dark:border-[#262046] tracking-tight"
                            {...props}
                          />
                        ),
                        h2: ({ node, ...props }) => (
                          <h2
                            className="text-base sm:text-xl font-bold text-[#4200db] dark:text-[#8575ff] mt-6 sm:mt-8 mb-3 pb-1 border-b border-[#e6e5f0]/60 dark:border-[#262046]/60 tracking-tight"
                            {...props}
                          />
                        ),
                        h3: ({ node, ...props }) => (
                          <h3
                            className="text-sm sm:text-base font-bold text-[#131920] dark:text-[#e4e4e7] mt-4 sm:mt-6 mb-2 tracking-tight"
                            {...props}
                          />
                        ),
                        h4: ({ node, ...props }) => (
                          <h4
                            className="text-xs sm:text-sm font-semibold text-[#5e6270] dark:text-[#a1a1aa] mt-3 mb-1 uppercase tracking-wider"
                            {...props}
                          />
                        ),
                        p: ({ node, ...props }) => (
                          <p className="mb-3 leading-relaxed text-xs sm:text-sm text-[#3b4050] dark:text-[#d4d4d8]" {...props} />
                        ),
                        ul: ({ node, ...props }) => (
                          <ul className="list-disc pl-5 my-3 space-y-1 text-xs sm:text-sm text-[#3b4050] dark:text-[#d4d4d8]" {...props} />
                        ),
                        ol: ({ node, ...props }) => (
                          <ol
                            className="list-decimal pl-5 my-3 space-y-1 text-xs sm:text-sm text-[#3b4050] dark:text-[#d4d4d8]"
                            {...props}
                          />
                        ),
                        li: ({ node, ...props }) => <li className="leading-relaxed pl-1" {...props} />,
                        strong: ({ node, ...props }) => (
                          <strong className="font-bold text-[#131920] dark:text-[#ffffff]" {...props} />
                        ),
                        blockquote: ({ node, ...props }) => (
                          <blockquote
                            className="border-l-4 border-[#4200db] dark:border-[#8575ff] pl-4 py-1.5 my-3 bg-[#faf9fe] dark:bg-[#181530] text-xs sm:text-sm italic text-[#5e6270] dark:text-[#a1a1aa] rounded-r-lg"
                            {...props}
                          />
                        ),
                        hr: ({ node, ...props }) => (
                          <hr className="my-6 border-[#e6e5f0] dark:border-[#262046]" {...props} />
                        ),
                        table: ({ node, ...props }) => (
                          <div className="overflow-x-auto my-4 rounded-xl border border-[#e6e5f0] dark:border-[#262046] shadow-2xs">
                            <table className="w-full text-left text-xs border-collapse min-w-[500px]" {...props} />
                          </div>
                        ),
                        thead: ({ node, ...props }) => (
                          <thead className="bg-[#f8f7fc] dark:bg-[#181530] text-[#131920] dark:text-[#f4f4f5] border-b border-[#e6e5f0] dark:border-[#262046]" {...props} />
                        ),
                        th: ({ node, ...props }) => (
                          <th className="px-3.5 py-2.5 font-bold text-[#131920] dark:text-[#f4f4f5] border-b border-[#e6e5f0] dark:border-[#262046]" {...props} />
                        ),
                        td: ({ node, ...props }) => (
                          <td className="px-3.5 py-2.5 border-b border-[#e6e5f0]/60 dark:border-[#262046]/60 text-[#40434f] dark:text-[#d4d4d8]" {...props} />
                        ),
                        img: ({ node, src, alt, ...props }: any) => {
                          let resolvedSrc = src || '';
                          if (resolvedSrc.includes('arvore_hipoteses')) {
                            resolvedSrc = arvoreHipotesesSvg;
                          } else if (resolvedSrc.startsWith('../assets/')) {
                            resolvedSrc = resolvedSrc.replace('../assets/', '/assets/');
                          }
                          return (
                            <div className="my-6 rounded-2xl overflow-hidden border border-[#e6e5f0] dark:border-[#262046] bg-[#faf9fe] dark:bg-[#110d21] p-4 sm:p-6 shadow-sm flex flex-col items-center">
                              <img
                                src={resolvedSrc}
                                alt={alt || 'Imagem'}
                                className="w-full h-auto rounded-lg max-h-[600px] object-contain shadow-xs"
                                {...props}
                              />
                              {alt && <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa] mt-2 italic font-sans">{alt}</span>}
                            </div>
                          );
                        },
                        details: ({ node, children, ...props }: any) => (
                          <details
                            className="group my-3.5 rounded-xl border border-[#e6e5f0] dark:border-[#262046] bg-[#faf9fe] dark:bg-[#15122b] overflow-hidden shadow-2xs transition-all open:bg-white dark:open:bg-[#131126] open:border-[#4200db]/30 dark:open:border-[#8575ff]/40"
                            {...props}
                          >
                            {children}
                          </details>
                        ),
                        summary: ({ node, children, ...props }: any) => (
                          <summary
                            className="cursor-pointer font-semibold text-xs sm:text-sm text-[#131920] dark:text-[#f4f4f5] hover:text-[#4200db] dark:hover:text-[#8575ff] select-none list-none flex items-center justify-between p-3.5 sm:p-4 bg-[#faf9fe] dark:bg-[#15122b] group-open:bg-[#f4f2ff]/60 dark:group-open:bg-[#1f193d]/60 group-open:border-b group-open:border-[#e6e5f0]/80 dark:group-open:border-[#262046]/80 transition-all [&::-webkit-details-marker]:hidden"
                            {...props}
                          >
                            <div className="flex items-center gap-2.5 min-w-0 pr-2">
                              <span className="w-2 h-2 rounded-full bg-[#4200db] dark:bg-[#8575ff] shrink-0 group-open:scale-110 transition-transform" />
                              <span className="leading-relaxed break-words">{children}</span>
                            </div>
                            <ChevronRight className="w-4 h-4 text-[#5e6270] dark:text-[#a1a1aa] shrink-0 transition-transform duration-200 group-open:rotate-90 group-open:text-[#4200db] dark:group-open:text-[#8575ff]" />
                          </summary>
                        ),
                        code: ({ node, inline, className, children, ...props }: any) => {
                          const codeString = String(children).replace(/\n$/, '');
                          if (inline) {
                            return (
                              <code
                                className="px-1.5 py-0.5 rounded bg-[#f4f2ff] dark:bg-[#251f47] text-[#4200db] dark:text-[#a599ff] font-mono text-[11px] sm:text-xs font-semibold"
                                {...props}
                              >
                                {children}
                              </code>
                            );
                          }
                          return (
                            <div className="relative group my-3 rounded-xl overflow-hidden border border-[#e6e5f0] dark:border-[#262046] bg-[#faf9fe] dark:bg-[#0c0a1a]">
                              <div className="flex items-center justify-between px-3.5 py-1.5 bg-[#f0eff8] dark:bg-[#16132e] border-b border-[#e6e5f0] dark:border-[#262046] text-[10px] font-mono text-[#5e6270] dark:text-[#71717a]">
                                <span>Código / Consulta SQL</span>
                                <button
                                  onClick={() => copyToClipboard(codeString, codeString.substring(0, 10))}
                                  className="flex items-center gap-1 hover:text-[#4200db] dark:hover:text-[#8575ff] transition-colors cursor-pointer"
                                >
                                  {copiedCode === codeString.substring(0, 10) ? (
                                    <>
                                      <Check className="w-3 h-3 text-emerald-600" />
                                      <span className="text-emerald-600 font-sans">Copiado</span>
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="w-3 h-3" />
                                      <span className="font-sans">Copiar</span>
                                    </>
                                  )}
                                </button>
                              </div>
                              <pre className="p-4 overflow-x-auto text-xs font-mono leading-relaxed text-[#131920] dark:text-[#f4f4f5]">
                                <code>{children}</code>
                              </pre>
                            </div>
                          );
                        },
                      }}
                    >
                      {editedContent}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
