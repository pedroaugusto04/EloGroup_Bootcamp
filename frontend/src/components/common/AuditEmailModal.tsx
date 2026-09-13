import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { PeriodKey, PeriodMeta } from '../../types/analytics';
import { Mail, CheckCircle2, AlertCircle, Loader2, X, ExternalLink, Sparkles } from 'lucide-react';

interface AuditEmailModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (threadId: string) => void;
}

export const AuditEmailModal: React.FC<AuditEmailModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [toEmail, setToEmail] = useState('');
  const [periodKey, setPeriodKey] = useState<PeriodKey>('full_history');
  const [periods, setPeriods] = useState<PeriodMeta[]>([]);
  const [sendEmail, setSendEmail] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      api.getCopilotPeriods().then(res => setPeriods(res.periods || [])).catch(() => setPeriods([]));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleRunAudit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.runAudit({
        period_key: periodKey,
        send_email: sendEmail,
        to_email: toEmail.trim() ? toEmail.trim() : undefined,
      });

      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Falha ao executar a análise de estoque.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCopilot = () => {
    if (result?.audit_thread_id && onSuccess) {
      onSuccess(result.audit_thread_id);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-lg bg-[#11131a] border border-[#27272a] rounded-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#27272a] bg-[#0d0d10] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#38bdf8]/15 border border-[#38bdf8]/30 flex items-center justify-center text-[#38bdf8]">
              <Mail className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#f4f4f5] tracking-tight">
                Análise de Estoque & E-mail Executivo
              </h3>
              <p className="text-[11px] text-[#71717a]">
                Pacote factual reproduzível, executado sob demanda
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            disabled={loading}
            className="p-1.5 rounded-lg text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b] transition-colors disabled:opacity-50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-5 space-y-4">
          {!result ? (
            <>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                O backend resolverá a janela selecionada, reconciliará fatos e cenários e só publicará o relatório se os checks determinísticos forem aprovados.
              </p>

              <div className="space-y-3 pt-1">
                <div>
                  <label className="block text-xs font-medium text-[#d4d4d8] mb-1">
                    Janela Temporal / Período
                  </label>
                  <select
                    value={periodKey}
                    onChange={e => setPeriodKey(e.target.value as PeriodKey)}
                    disabled={loading}
                    className="w-full text-xs bg-[#18181b] border border-[#27272a] rounded-lg px-3 py-2 text-[#f4f4f5] focus:outline-none focus:border-[#38bdf8]"
                  >
                    {periods.map(period => (
                      <option key={period.period_key} value={period.period_key}>
                        {period.label} · {period.sales_start.split('-').reverse().join('/')}–{period.sales_end.split('-').reverse().join('/')}
                      </option>
                    ))}
                    {periods.length === 0 && <option value="full_history">Histórico completo observado</option>}
                  </select>
                </div>

                <details className="rounded-lg border border-[#27272a] bg-[#18181b] p-3 text-[11px] text-[#a1a1aa]">
                  <summary className="cursor-pointer font-medium text-[#d4d4d8]">Metodologia e limitações</summary>
                  <p className="mt-2 leading-relaxed">Posição de estoque fornecida — data de referência não informada. Vendas representam tendência histórica observada, não previsão. Financeiro vem de Vendas; cenários não são perdas realizadas.</p>
                </details>

                <div>
                  <label className="block text-xs font-medium text-[#d4d4d8] mb-1">
                    Destinatário do E-mail (Opcional)
                  </label>
                  <input
                    type="email"
                    value={toEmail}
                    onChange={e => setToEmail(e.target.value)}
                    placeholder="diretoria@verticeretail.com.br (ou seu e-mail)"
                    disabled={loading}
                    className="w-full text-xs bg-[#18181b] border border-[#27272a] rounded-lg px-3 py-2 text-[#f4f4f5] placeholder-[#71717a] focus:outline-none focus:border-[#38bdf8]"
                  />
                  <span className="text-[10px] text-[#71717a] mt-1 block">
                    Se vazio, usa o e-mail padrão configurado nas variáveis de ambiente.
                  </span>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="sendEmailCheckbox"
                    checked={sendEmail}
                    onChange={e => setSendEmail(e.target.checked)}
                    disabled={loading}
                    className="rounded border-[#27272a] bg-[#18181b] text-[#38bdf8] focus:ring-0"
                  />
                  <label htmlFor="sendEmailCheckbox" className="text-xs text-[#d4d4d8] cursor-pointer select-none">
                    Enviar e-mail
                  </label>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </>
          ) : (
            <div className="space-y-3.5 py-1">
              <div className={`p-3.5 rounded-lg text-xs flex items-start gap-2.5 ${result.analysis_success ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400' : 'bg-rose-500/10 border border-rose-500/30 text-rose-400'}`}>
                {result.analysis_success ? <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" /> : <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />}
                <div className="space-y-1">
                  <div className="font-semibold">{result.analysis_success ? 'Análise executada' : 'Análise não concluída'}</div>
                  <div className="text-[#a1a1aa] leading-relaxed">
                    Consulte abaixo, separadamente, a reconciliação determinística e o processamento do e-mail.
                  </div>
                </div>
              </div>

              <div className="p-3 bg-[#18181b] rounded-lg border border-[#27272a] text-xs space-y-1.5 font-mono">
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>Status do Parecer:</span>
                  <span className={result.deterministic_approved ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                    {result.deterministic_approved ? 'Aprovado' : 'Reprovado'}
                  </span>
                </div>
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>Status E-mail:</span>
                  <span className="text-[#38bdf8] font-semibold">{result.email_status}</span>
                </div>
                {result.email_result?.to && (
                  <div className="flex justify-between text-[#a1a1aa]">
                    <span>Destinatário:</span>
                    <span className="text-[#f4f4f5]">{Array.isArray(result.email_result.to) ? result.email_result.to.join(', ') : result.email_result.to}</span>
                  </div>
                )}
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>Thread ID:</span>
                  <span className="text-[#71717a] truncate max-w-[200px]">{result.audit_thread_id}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 sm:p-5 border-t border-[#27272a] bg-[#0d0d10] flex items-center justify-end gap-2.5">
          {!result ? (
            <>
              <button
                onClick={onClose}
                disabled={loading}
                className="px-3.5 py-2 rounded-lg text-xs font-medium text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b] transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleRunAudit}
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-[#38bdf8] hover:bg-[#38bdf8]/90 text-[#09090b] text-xs font-semibold flex items-center gap-2 transition-all shadow-md active:scale-95 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Executando Auditoria...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Gerar Análise & Enviar</span>
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onClose}
                className="px-3.5 py-2 rounded-lg text-xs font-medium text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b] transition-colors"
              >
                Fechar
              </button>
              {result.audit_thread_id && <button
                onClick={handleOpenCopilot}
                className="px-4 py-2 rounded-lg bg-[#38bdf8] hover:bg-[#38bdf8]/90 text-[#09090b] text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md active:scale-95"
              >
                <span>Abrir Conversa no Copiloto</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
