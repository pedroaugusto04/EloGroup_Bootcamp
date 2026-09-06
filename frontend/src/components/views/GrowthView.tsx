import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import {
  MarketingAnalyticsData,
  CustomerAnalyticsData,
  SupportAnalyticsData,
  FilterOptions,
} from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface GrowthViewProps {
  filterOptions?: FilterOptions;
}

const COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#ec4899'];

export const GrowthView: React.FC<GrowthViewProps> = () => {
  const [activeSubTab, setActiveSubTab] = useState<'mkt' | 'clients' | 'support'>('mkt');
  const [loading, setLoading] = useState(true);

  const [mktData, setMktData] = useState<MarketingAnalyticsData | null>(null);
  const [custData, setCustData] = useState<CustomerAnalyticsData | null>(null);
  const [supData, setSupData] = useState<SupportAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [resMkt, resCust, resSup] = await Promise.all([
        api.getMarketing([]),
        api.getCustomers([]),
        api.getSupport([]),
      ]);
      setMktData(resMkt);
      setCustData(resCust);
      setSupData(resSup);
    } catch (err) {
      console.error('Erro ao carregar dados de growth:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Columns for Marketing
  const mktColumns: Column<any>[] = [
    { key: 'canal', header: 'Canal de Mídia', className: 'font-semibold text-[#f4f4f5]' },
    {
      key: 'investimento',
      header: 'Investimento',
      align: 'right',
      render: r => `R$ ${Number(r.investimento).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'receita_gerada',
      header: 'Receita Declarada',
      align: 'right',
      render: r => `R$ ${Number(r.receita_gerada).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'roas',
      header: 'ROAS',
      align: 'right',
      render: r => (
        <span className="font-mono text-[#38bdf8] font-bold">
          {Number(r.roas).toFixed(2)}x
        </span>
      ),
    },
    {
      key: 'cac',
      header: 'CAC Médio',
      align: 'right',
      render: r => `R$ ${Number(r.cac).toFixed(2)}`,
    },
    {
      key: 'ctr_pct',
      header: 'CTR %',
      align: 'right',
      render: r => `${Number(r.ctr_pct).toFixed(2)}%`,
    },
    {
      key: 'taxa_conversao_pct',
      header: 'Taxa Conv %',
      align: 'right',
      render: r => `${Number(r.taxa_conversao_pct).toFixed(2)}%`,
    },
  ];

  // Columns for Pareto Clientes
  const paretoColumns: Column<any>[] = [
    { key: 'segmento_rfm', header: 'Segmento RFM', className: 'font-semibold text-[#f4f4f5]' },
    {
      key: 'total_clientes',
      header: 'Clientes',
      align: 'right',
      render: r => Number(r.total_clientes).toLocaleString('pt-BR'),
    },
    {
      key: 'pct_base_clientes',
      header: '% Base',
      align: 'right',
      render: r => `${Number(r.pct_base_clientes).toFixed(1)}%`,
    },
    {
      key: 'ltv_total',
      header: 'LTV Acumulado (CRM)',
      align: 'right',
      render: r => `R$ ${((r.ltv_total || 0) / 1e6).toFixed(2)}M`,
    },
    {
      key: 'pct_ltv_total',
      header: '% LTV Total',
      align: 'right',
      render: r => (
        <span className="font-mono font-bold text-emerald-400">
          {Number(r.pct_ltv_total).toFixed(1)}%
        </span>
      ),
    },
    {
      key: 'ticket_medio_segmento',
      header: 'Ticket Médio',
      align: 'right',
      render: r => `R$ ${Number(r.ticket_medio_segmento).toFixed(2)}`,
    },
    {
      key: 'pedidos_medios',
      header: 'Pedidos Médios',
      align: 'right',
      render: r => Number(r.pedidos_medios).toFixed(1),
    },
  ];

  // Columns for AI Support Root Causes
  const aiColumns: Column<any>[] = [
    { key: 'categoria_problema', header: 'Motivo do Chamado', className: 'font-semibold text-[#f4f4f5]' },
    {
      key: 'is_automatizavel',
      header: 'Automação IA',
      align: 'center',
      render: r => (
        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${r.is_automatizavel ? 'bg-[#38bdf8]/15 text-[#38bdf8] border border-[#38bdf8]/30' : 'bg-[#27272a] text-[#71717a]'}`}>
          {r.is_automatizavel ? 'Automatizável (IA)' : 'Atendimento Humano'}
        </span>
      ),
    },
    {
      key: 'total_tickets',
      header: 'Volume Tickets',
      align: 'right',
      render: r => Number(r.total_tickets).toLocaleString('pt-BR'),
    },
    {
      key: 'pct_volume',
      header: '% Volume',
      align: 'right',
      render: r => `${Number(r.pct_volume).toFixed(1)}%`,
    },
    {
      key: 'csat_medio',
      header: 'CSAT Médio',
      align: 'right',
      render: r => `${Number(r.csat_medio).toFixed(2)} / 5.0`,
    },
    {
      key: 'custo_total_categoria',
      header: 'Custo Total',
      align: 'right',
      render: r => `R$ ${Number(r.custo_total_categoria).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'custo_evitavel_automacao',
      header: 'Economia Potencial (IA)',
      align: 'right',
      render: r => (
        <span className={`font-mono font-bold ${r.custo_evitavel_automacao > 0 ? 'text-emerald-400' : 'text-[#71717a]'}`}>
          R$ {Number(r.custo_evitavel_automacao).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      {/* Sub-tab Switcher */}
      <div className="flex items-center gap-2 border-b border-[#27272a] pb-3">
        <button
          onClick={() => setActiveSubTab('mkt')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
            activeSubTab === 'mkt'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
          }`}
        >
          Marketing & Mídia (ROAS)
        </button>
        <button
          onClick={() => setActiveSubTab('clients')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
            activeSubTab === 'clients'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
          }`}
        >
          Clientes & Segmentação RFM (Hipótese 5)
        </button>
        <button
          onClick={() => setActiveSubTab('support')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
            activeSubTab === 'support'
              ? 'bg-[#18181b] border-[#38bdf8]/50 text-[#38bdf8]'
              : 'border-transparent text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b]/50'
          }`}
        >
          Suporte & Automação com IA (Hipótese 4)
        </button>
      </div>

      {/* ========================================================================= */}
      {/* SUB-TAB 1: MARKETING */}
      {/* ========================================================================= */}
      {activeSubTab === 'mkt' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={['marketing']}
            scope="3.500 campanhas de mídia declaradas • Jan/2023 a Dez/2025"
            devSection="Seção 3: Observações por Tabela (Marketing & ROAS Declarado)"
          />

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard
              label="Investimento Total (Mídia)"
              value={`R$ ${((mktData?.kpis.invest_total || 0) / 1e6).toFixed(1)}M`}
              subtitle="Gasto declarado nas plataformas"
            />
            <MetricCard
              label="Receita Gerada (Mídia)"
              value={`R$ ${((mktData?.kpis.rec_total || 0) / 1e6).toFixed(1)}M`}
              subtitle="Retorno atribuído pelas redes"
            />
            <MetricCard
              label="ROAS Declarado Global"
              value={`${Number(mktData?.kpis.roas_global || 0).toFixed(2)}x`}
              trend={{ value: 'Plataformas', isPositive: true }}
              subtitle="Retorno aparente de mídia"
              highlight
            />
            <MetricCard
              label="CAC Médio"
              value={`R$ ${Number(mktData?.kpis.cac_medio || 0).toFixed(2)}`}
              subtitle="Custo médio de aquisição"
            />
            <MetricCard
              label="Total Conversões"
              value={`${((mktData?.kpis.conv_total || 0) / 1e6).toFixed(1)}M`}
              subtitle="Conversões declaradas"
            />
          </div>

          {/* Marketing Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                Investimento vs. Receita por Canal de Mídia
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mktData?.channels || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="canal" stroke="#71717a" fontSize={11} tickLine={false} />
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
                    <Bar dataKey="investimento" name="Investimento (R$)" fill="#94a3b8" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="receita_gerada" name="Receita Declarada (R$)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                Eficiência Relativa: ROAS vs. CAC por Canal
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mktData?.channels || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="canal" stroke="#71717a" fontSize={11} tickLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                    <Bar dataKey="roas" name="ROAS (x)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="cac" name="CAC (R$)" fill="#f59e0b" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Marketing Table */}
          <div className="flex flex-col">
            <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
              Matriz Completa de Desempenho de Mídia
            </div>
            <DataTable
              columns={mktColumns}
              data={mktData?.channels || []}
              searchPlaceholder="Buscar canal..."
              searchKey="canal"
            />
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 2: CLIENTES (HIPÓTESE 5) */}
      {/* ========================================================================= */}
      {activeSubTab === 'clients' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={['clientes']}
            scope="15.000 clientes cadastrados (CRM) • Ano Base 2026"
            devSection="Seção 3 & Seção 5: Hipótese 5 (Segmentos de Clientes & Concentração)"
          />

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard
              label="Total de Clientes"
              value={Number(custData?.kpis.total_clientes || 15000).toLocaleString('pt-BR')}
              subtitle="Base total CRM"
            />
            <MetricCard
              label="LTV Médio"
              value={`R$ ${Number(custData?.kpis.ltv_medio || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
              subtitle="Média histórica declarada"
              highlight
            />
            <MetricCard
              label="Frequência Média"
              value={`${Number(custData?.kpis.frequencia_media || 0).toFixed(1)} pedidos`}
              subtitle="Compras por cliente"
            />
            <MetricCard
              label="Renda Média"
              value={`R$ ${Number(custData?.kpis.renda_media || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
              subtitle="Perfil cadastral"
            />
            <MetricCard
              label="Idade Média"
              value={`${Math.round(custData?.kpis.idade_media || 42)} anos`}
              subtitle="Calculado sobre ano 2026"
            />
          </div>

          {/* Pareto Callout */}
          <div className="p-3.5 rounded-lg bg-[#18181b] border border-[#27272a] text-xs text-[#d4d4d8] flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
            <div>
              <span className="font-semibold text-[#f4f4f5]">Diagnóstico de Concentração de Clientes (Hipótese 5):</span>{' '}
              Clientes dos segmentos <span className="font-semibold text-[#f4f4f5]">Campeões</span> e <span className="font-semibold text-[#f4f4f5]">Fiéis</span> são poucos em volume, mas representam a maior fatia do LTV acumulado. Em contrapartida, <span className="font-mono text-amber-400 font-semibold">46,7% da base</span> está nas faixas de risco (Em Risco, Hibernando e Churn), exigindo réguas automatizadas de retenção e cupons de recompra.
            </div>
          </div>

          {/* RFM Distribution Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                Distribuição de Clientes por Segmento RFM
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={custData?.segments || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="segmento" stroke="#71717a" fontSize={11} tickLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                    />
                    <Bar dataKey="total_clientes" name="Total Clientes" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                LTV Médio por Segmento RFM (R$)
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={custData?.segments || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="segmento" stroke="#71717a" fontSize={11} tickLine={false} />
                    <YAxis
                      stroke="#71717a"
                      fontSize={11}
                      tickFormatter={v => `R$ ${(v / 1e3).toFixed(0)}k`}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                      formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
                    />
                    <Bar dataKey="ltv_medio" name="LTV Médio (R$)" fill="#10b981" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Pareto Table */}
          <div className="flex flex-col">
            <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
              Matriz de Concentração de Pareto & Ticket Médio por Segmento
            </div>
            <DataTable
              columns={paretoColumns}
              data={custData?.pareto_distribution || []}
              searchPlaceholder="Buscar segmento..."
              searchKey="segmento_rfm"
            />
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 3: SUPORTE & IA (HIPÓTESE 4) */}
      {/* ========================================================================= */}
      {activeSubTab === 'support' && (
        <div className="space-y-5">
          <ScopeBadge
            tables={['atendimento']}
            scope="35.840 tickets de suporte • Jan/2023 a Dez/2025"
            devSection="Seção 3 & Seção 5: Hipótese 4 (Causas Raiz & Automação com IA)"
          />

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <MetricCard
              label="Total de Chamados"
              value={Number(supData?.kpis.total_tickets || 35840).toLocaleString('pt-BR')}
              subtitle="Volume total no suporte"
            />
            <MetricCard
              label="CSAT Médio"
              value={`${Number(supData?.kpis.csat_medio || 3.0).toFixed(1)} / 5.0`}
              subtitle="Satisfação geral neutra"
            />
            <MetricCard
              label="Custo Operacional Total"
              value={`R$ ${((supData?.kpis.custo_operacional_total || 537600) / 1e3).toFixed(1)}k`}
              subtitle="Gasto direto com tickets"
            />
            <MetricCard
              label="Economia com IA (Quick Win)"
              value="R$ 238,5k"
              trend={{ value: '44% do custo', isPositive: true }}
              subtitle="Rastreio + Dúvidas Técnicas"
              highlight
            />
            <MetricCard
              label="1ª Resposta Média"
              value={`${Math.round(supData?.kpis.primeira_resposta_minutos || 122)} min`}
              subtitle="SLA médio de atendimento"
            />
          </div>

          {/* Quick Win Callout */}
          <div className="p-3.5 rounded-lg bg-[#18181b] border border-[#27272a] text-xs text-[#d4d4d8] flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-[#38bdf8] mt-1.5 shrink-0" />
            <div>
              <span className="font-semibold text-[#f4f4f5]">Oportunidade Imediata de IA & Notificação (Hipótese 4):</span>{' '}
              O motivo <span className="font-semibold text-[#f4f4f5]">'Onde está meu pedido'</span> responde por <span className="font-mono text-[#38bdf8] font-bold">30% de todo o suporte</span> e gera <span className="font-mono text-emerald-400 font-bold">R$ 159.660,00</span> em custos evitáveis. O prazo de entrega é padrão (8,3 dias), logo o atrito é puramente ansiedade e falta de visibilidade: uma notificação automática via WhatsApp com link de rastreamento resolve o problema com esforço de 15 dias.
            </div>
          </div>

          {/* Support Breakdown Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                Volume de Chamados por Canal de Entrada
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={supData?.channels || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="canal_entrada" stroke="#71717a" fontSize={11} tickLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                    />
                    <Bar dataKey="total_tickets" name="Total Tickets" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
                Distribuição das Notas CSAT (1 a 5)
              </div>
              <div className="h-72 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={supData?.csat_distribution || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                    <XAxis dataKey="nota_csat" stroke="#71717a" fontSize={11} tickLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                    />
                    <Bar dataKey="total_avaliacoes" name="Avaliações" fill="#818cf8" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* AI Root Causes Table */}
          <div className="flex flex-col">
            <div className="text-xs font-semibold text-[#f4f4f5] mb-2">
              Diagnóstico de Causas-Raiz & Custos Evitáveis por Automação IA
            </div>
            <DataTable
              columns={aiColumns}
              data={supData?.root_causes_ai || []}
              searchPlaceholder="Buscar motivo do chamado..."
              searchKey="categoria_problema"
            />
          </div>
        </div>
      )}
    </div>
  );
};
