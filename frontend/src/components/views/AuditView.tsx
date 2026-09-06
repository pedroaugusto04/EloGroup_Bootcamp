import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { RelationalAuditData, OutliersData } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';
import { AlertTriangle, ShieldAlert, CheckCircle2 } from 'lucide-react';
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

export const AuditView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'relational' | 'outliers'>('relational');
  const [loading, setLoading] = useState(true);

  // Relational Audit
  const [relData, setRelData] = useState<RelationalAuditData | null>(null);

  // Outliers
  const [selectedTable, setSelectedTable] = useState('vendas');
  const [selectedMetric, setSelectedMetric] = useState<string | undefined>(undefined);
  const [outliersData, setOutliersData] = useState<OutliersData | null>(null);

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

  const fetchOutliers = async () => {
    try {
      const res = await api.getOutliers(selectedTable, selectedMetric);
      setOutliersData(res);
      if (!selectedMetric && res.selected_metric) {
        setSelectedMetric(res.selected_metric);
      }
    } catch (err) {
      console.error('Erro ao carregar outliers:', err);
    }
  };

  useEffect(() => {
    fetchRelational();
  }, []);

  useEffect(() => {
    fetchOutliers();
  }, [selectedTable, selectedMetric]);

  const outlierColumns: Column<any>[] = [
    { key: 'dimension_value', header: 'Dimensão / Grupo', className: 'font-semibold text-[#f4f4f5]' },
    { key: 'total_records', header: 'Registros', align: 'right', render: r => Number(r.total_records).toLocaleString('pt-BR') },
    { key: 'q1', header: 'Q1 (25%)', align: 'right', render: r => Number(r.q1).toFixed(2) },
    { key: 'median', header: 'Mediana (50%)', align: 'right', render: r => Number(r.median).toFixed(2) },
    { key: 'q3', header: 'Q3 (75%)', align: 'right', render: r => Number(r.q3).toFixed(2) },
    { key: 'iqr', header: 'IQR', align: 'right', render: r => Number(r.iqr).toFixed(2) },
    {
      key: 'outliers_count',
      header: 'Outliers (Tukey)',
      align: 'right',
      render: r => (
        <span className={`font-mono font-bold ${r.outliers_count > 0 ? 'text-amber-400' : 'text-[#71717a]'}`}>
          {r.outliers_count} ({Number(r.outliers_pct).toFixed(1)}%)
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      {/* Sub-tab Switcher */}
      <div className="flex items-center gap-2 border-b border-[#27272a] pb-3">
        <button
          onClick={() => setActiveSubTab('relational')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
            activeSubTab === 'relational'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
          }`}
        >
          Integridade Relacional entre Bases
        </button>
        <button
          onClick={() => setActiveSubTab('outliers')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
            activeSubTab === 'outliers'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
          }`}
        >
          Dispersão & Detecção de Outliers (Tukey IQR)
        </button>
      </div>

      {/* ========================================================================= */}
      {/* SUB-TAB 1: INTEGRIDADE RELACIONAL */}
      {/* ========================================================================= */}
      {activeSubTab === 'relational' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={['vendas', 'marketing', 'estoque', 'clientes', 'atendimento']}
            scope="Cruzamento Relacional Global (5 Bases)"
            devSection="Seção 4: Observações Gerais (Incoerências & Integridade das Bases)"
          />

          {/* Audit Alert Banners */}
          <div className="space-y-2.5">
            {(relData?.audit_findings || []).map((finding, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-[#11131a] border border-[#27272a] flex items-start gap-3 text-xs"
              >
                <div className="mt-0.5">
                  {finding.severity === 'Crítica' ? (
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-semibold text-[#f4f4f5] text-xs">
                      {finding.dimension}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                        finding.severity === 'Crítica'
                          ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                          : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {finding.severity}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 my-1.5 text-[11px] font-mono bg-[#18181b] p-2 rounded border border-[#27272a]">
                    <div>
                      <span className="text-[#71717a] block">Extrato ERP:</span>
                      <span className="text-[#d4d4d8]">{finding.erp_coverage}</span>
                    </div>
                    <div>
                      <span className="text-[#71717a] block">Outras Bases:</span>
                      <span className="text-[#d4d4d8]">{finding.external_coverage}</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-[#a1a1aa] mt-1 font-sans">
                    <strong className="text-[#e4e4e7]">Impacto Analítico:</strong> {finding.impact}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Marketing vs Sales Real Comparison Chart */}
          <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
            <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
              <span>Atribuição de Mídia Declarada vs. Receita Líquida Real do ERP</span>
            </div>
            <div className="h-72 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={relData?.mkt_vs_sales || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                  <XAxis dataKey="ano_mes" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#71717a"
                    fontSize={11}
                    tickFormatter={v => `R$ ${(v / 1e6).toFixed(0)}M`}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                    formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                  <Bar dataKey="investimento_mkt" name="Investimento Mídia (R$)" fill="#94a3b8" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="receita_declarada_mkt" name="Receita Declarada Mídia (R$)" fill="#f59e0b" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="receita_liquida_real" name="Receita Real ERP (R$)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 2: DISPERSÃO & OUTLIERS */}
      {/* ========================================================================= */}
      {activeSubTab === 'outliers' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={[selectedTable]}
            scope="Detecção de Anomalias Estatísticas • Critério Tukey IQR (1.5x)"
            devSection="Seção 2: Outliers e Anomalias (DEVELOPMENT.md)"
          />

          {/* Table & Metric Controls */}
          <div className="flex flex-wrap items-center gap-3 p-3.5 rounded-lg bg-[#11131a] border border-[#27272a]">
            <div className="flex items-center gap-2">
              <span className="text-xs text-[#a1a1aa] font-medium">Tabela:</span>
              <select
                value={selectedTable}
                onChange={e => {
                  setSelectedTable(e.target.value);
                  setSelectedMetric(undefined);
                }}
                className="text-xs bg-[#18181b] border border-[#27272a] rounded px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#38bdf8]"
              >
                {(outliersData?.available_tables || ['vendas', 'estoque', 'clientes', 'atendimento', 'marketing']).map(t => (
                  <option key={t} value={t}>{t.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-[#a1a1aa] font-medium">Métrica Numérica:</span>
              <select
                value={selectedMetric || outliersData?.selected_metric || ''}
                onChange={e => setSelectedMetric(e.target.value)}
                className="text-xs bg-[#18181b] border border-[#27272a] rounded px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#38bdf8]"
              >
                {(outliersData?.available_metrics || []).map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Overall Stats Cards */}
          {outliersData && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <MetricCard
                label="Q1 (25º Percentil)"
                value={Number(outliersData.overall_stats.q1).toFixed(2)}
                subtitle="Limite inferior de dispersão"
              />
              <MetricCard
                label="Mediana (50%)"
                value={Number(outliersData.overall_stats.median).toFixed(2)}
                subtitle="Tendência central robusta"
              />
              <MetricCard
                label="Q3 (75º Percentil)"
                value={Number(outliersData.overall_stats.q3).toFixed(2)}
                subtitle="Limite superior de dispersão"
              />
              <MetricCard
                label="IQR (Q3 - Q1)"
                value={Number(outliersData.overall_stats.iqr).toFixed(2)}
                subtitle="Intervalo Interquartil"
              />
              <MetricCard
                label="Total de Outliers"
                value={`${outliersData.overall_stats.outliers_count}`}
                trend={{
                  value: `${Number(outliersData.overall_stats.outliers_pct).toFixed(1)}%`,
                  isPositive: false,
                }}
                subtitle="Valores além de 1.5x IQR"
                highlight
              />
            </div>
          )}

          {/* Outliers Table by Dimension */}
          <div className="flex flex-col">
            <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
              <span>Dispersão e Quantis por {outliersData?.group_by_dimension?.toUpperCase()}</span>
            </div>
            <DataTable
              columns={outlierColumns}
              data={outliersData?.by_dimension || []}
              searchPlaceholder="Buscar dimensão..."
              searchKey="dimension_value"
            />
          </div>
        </div>
      )}
    </div>
  );
};
