import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { RelationalAuditData } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { AlertTriangle, ShieldAlert } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

export const AuditRelationalView = () => {
  const [loading, setLoading] = useState(true);
  const [relData, setRelData] = useState<RelationalAuditData | null>(null);

  const fetchRelational = async () => {
    try {
      setLoading(true);
      const res = await api.getRelationalAudit();
      setRelData(res);
    } catch (err) {
      console.error('Erro ao carregar auditoria relacional:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRelational();
  }, []);

  if (loading) {
    return <div className="text-[#71717a] text-sm">Carregando dados de auditoria...</div>;
  }

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['vendas', 'marketing', 'estoque', 'clientes', 'atendimento']}
        scope="Cruzamento Relacional Global (5 Bases)"
        devSection="Seção 4: Incoerências & Integridade das Bases"
      />

      <div className="space-y-2.5">
        {(relData?.audit_findings || []).map((finding, idx) => (
          <div
            key={idx}
            className="p-3 sm:p-3.5 rounded-lg bg-[#11131a] border border-[#27272a] flex items-start gap-2.5 sm:gap-3 text-xs"
          >
            <div className="mt-0.5 shrink-0">
              {finding.severity === 'Crítica' ? (
                <ShieldAlert className="w-4 h-4 text-rose-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-400" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-semibold text-[#f4f4f5] text-xs truncate">
                  {finding.dimension}
                </span>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold shrink-0 ${
                    finding.severity === 'Crítica'
                      ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                      : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {finding.severity}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 my-1.5 text-[11px] font-mono bg-[#18181b] p-2 rounded border border-[#27272a]">
                <div>
                  <span className="text-[#71717a] block">Base Vendas:</span>
                  <span className="text-[#d4d4d8]">{finding.erp_coverage}</span>
                </div>
                <div>
                  <span className="text-[#71717a] block">Outras Bases:</span>
                  <span className="text-[#d4d4d8]">{finding.external_coverage}</span>
                </div>
              </div>

              <p className="text-[11px] text-[#a1a1aa] mt-1 font-sans leading-relaxed">
                <strong className="text-[#e4e4e7]">Impacto Analítico:</strong> {finding.impact}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 sm:p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
        <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
          <span className="truncate">Atribuição de Mídia vs. Receita Real de Vendas</span>
        </div>
        <div className="h-64 sm:h-72 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={relData?.mkt_vs_sales || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
              <XAxis dataKey="ano_mes" stroke="#71717a" fontSize={10} tickLine={false} />
              <YAxis
                stroke="#71717a"
                fontSize={10}
                tickFormatter={v => `${(v / 1e6).toFixed(0)}M`}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Bar dataKey="investimento_mkt" name="Invest. Mídia (R$)" fill="#94a3b8" radius={[3, 3, 0, 0]} />
              <Bar dataKey="receita_declarada_mkt" name="Receita Mídia (R$)" fill="#f59e0b" radius={[3, 3, 0, 0]} />
              <Bar dataKey="receita_liquida_real" name="Receita Real (R$)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
