import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { InventoryAnalyticsData, FilterOptions } from '../../types/analytics';
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

interface InventoryViewProps {
  filterOptions?: FilterOptions;
}

const STATUS_COLORS: Record<string, string> = {
  'Descontinuado': '#f43f5e',
  'Estoque Crítico': '#f59e0b',
  'Normal': '#10b981',
  'Excesso': '#38bdf8',
};

export const InventoryView: React.FC<InventoryViewProps> = ({ filterOptions }) => {
  const [loading, setLoading] = useState(true);
  const [selectedCats, setSelectedCats] = useState<string[]>([]);
  const [data, setData] = useState<InventoryAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await api.getInventory(selectedCats);
      setData(res);
    } catch (err) {
      console.error('Erro ao carregar estoque:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCats]);

  const kpis = data?.kpis || {
    total_skus: 5000,
    skus_ruptura: 99,
    skus_criticos: 701,
    skus_precisa_reposicao: 800,
    taxa_ruptura: 2.0,
    capital_parado: 14775347,
    lead_time_medio: 20,
  };

  const criticalColumns: Column<any>[] = [
    {
      key: 'sku_id',
      header: 'SKU',
      className: 'font-mono text-[#38bdf8]',
      render: r => <span className="font-mono text-[#38bdf8]">{r.sku_id}</span>,
    },
    { key: 'nome_produto', header: 'Produto' },
    { key: 'categoria', header: 'Categoria' },
    {
      key: 'estoque_disponivel',
      header: 'Estoque Atual',
      align: 'right',
      render: r => (
        <span className={`font-mono font-bold ${r.estoque_disponivel === 0 ? 'text-rose-400' : 'text-amber-400'}`}>
          {r.estoque_disponivel} un
        </span>
      ),
    },
    {
      key: 'ponto_pedido',
      header: 'Ponto de Pedido',
      align: 'right',
      render: r => `${r.ponto_pedido} un`,
    },
    {
      key: 'deficit_unidades',
      header: 'Déficit (Reposição)',
      align: 'right',
      render: r => (
        <span className="font-mono text-rose-400 font-semibold">
          +{r.deficit_unidades} un
        </span>
      ),
    },
    {
      key: 'lead_time_dias',
      header: 'Lead Time',
      align: 'right',
      render: r => `${r.lead_time_dias} dias`,
    },
    {
      key: 'preco_venda_sugerido',
      header: 'Preço Venda',
      align: 'right',
      render: r => `R$ ${Number(r.preco_venda_sugerido).toFixed(2)}`,
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['estoque']}
        scope="5.000 SKUs (WMS) • Snapshot Jan/2026"
        devSection="Seção 3 & Seção 5: Hipótese 6 (Descompasso de Estoque & Ruptura)"
      />

      {/* Category Filter */}
      {filterOptions?.categories && (
        <div className="flex items-center gap-2 p-3.5 rounded-lg bg-[#11131a] border border-[#27272a] flex-wrap">
          <span className="text-xs text-[#a1a1aa] font-medium mr-1">Filtrar Categoria:</span>
          {filterOptions.categories.map(cat => {
            const active = selectedCats.includes(cat);
            return (
              <button
                key={cat}
                onClick={() => {
                  if (active) {
                    setSelectedCats(selectedCats.filter(c => c !== cat));
                  } else {
                    setSelectedCats([...selectedCats, cat]);
                  }
                }}
                className={`text-[11px] px-2.5 py-0.5 rounded border transition-colors ${active
                    ? 'bg-[#38bdf8]/15 border-[#38bdf8]/60 text-[#38bdf8] font-medium'
                    : 'bg-[#18181b] border-[#27272a] text-[#a1a1aa] hover:border-[#3f3f46]'
                  }`}
              >
                {cat}
              </button>
            );
          })}
          {selectedCats.length > 0 && (
            <button
              onClick={() => setSelectedCats([])}
              className="text-[11px] text-[#71717a] hover:text-[#f4f4f5] ml-1 underline"
            >
              Limpar
            </button>
          )}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <MetricCard
          label="Total de SKUs"
          value={Number(kpis.total_skus || 5000).toLocaleString('pt-BR')}
          subtitle="Catálogo completo WMS"
        />
        <MetricCard
          label="SKUs em Ruptura Real"
          value={`${kpis.skus_ruptura || 99} SKUs`}
          trend={{ value: 'Sem Estoque', isPositive: false }}
          subtitle="96 concentrados em Beleza"
          highlight
        />
        <MetricCard
          label="SKUs em Nível Crítico"
          value={`${kpis.skus_criticos || 701} SKUs`}
          trend={{ value: '<= Ponto Pedido', isPositive: false }}
          subtitle="Risco iminente de falta"
        />
        <MetricCard
          label="Capital em Descontinuados"
          value={`R$ ${((kpis.capital_parado || 14775347) / 1e6).toFixed(1)}M`}
          trend={{ value: '207 SKUs', isPositive: false }}
          subtitle="Imobilizado sem giro (Hipótese 6)"
        />
        <MetricCard
          label="Lead Time Médio"
          value={`${Math.round(kpis.lead_time_medio || 20)} dias`}
          subtitle="Tempo de reposição fabril"
        />
      </div>

      {/* Key Finding Executive Callout */}
      <div className="p-3.5 rounded-lg bg-[#18181b] border border-[#27272a] text-xs text-[#d4d4d8] flex items-start gap-3">
        <div className="w-2 h-2 rounded-full bg-[#38bdf8] mt-1.5 shrink-0" />
        <div>
          <span className="font-semibold text-[#f4f4f5]">Diagnóstico Executivo de Estoque (Hipótese 6):</span>{' '}
          Existe um descompasso estrutural entre excesso e falta. Mais de <span className="font-mono text-[#38bdf8]">R$ 14,7M</span> estão imobilizados em 207 produtos fora de linha (descontinuados), enquanto <span className="font-mono text-rose-400">96 dos 99 SKUs zerados</span> pertencem exclusivamente à categoria <span className="font-semibold text-[#f4f4f5]">Beleza</span>. Recomendação de Quick Win: liquidação imediata para liberar caixa e reabastecimento urgente dos 701 SKUs críticos.
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Rupture by Category Stacked */}
        <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Necessidade de Reposição por Categoria (Severidade)</span>
          </div>
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.categories_rupture || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="categoria" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar dataKey="skus_ruptura" name="Ruptura Real (Estoque = 0)" fill="#ef4444" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="skus_estoque_critico" name="Estoque Crítico (<= Ponto Pedido)" fill="#f59e0b" stackId="a" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Capital Breakdown by Status */}
        <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Capital em Estoque por Status de Disponibilidade (Hipótese 6)</span>
          </div>
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.status_breakdown || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="status_disponibilidade" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#71717a"
                  fontSize={11}
                  tickFormatter={v => `R$ ${(v / 1e6).toFixed(1)}M`}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                  formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
                />
                <Bar dataKey="capital_total_estoque" name="Capital Total (R$)" radius={[3, 3, 0, 0]}>
                  {(data?.status_breakdown || []).map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={STATUS_COLORS[entry.status_disponibilidade] || '#38bdf8'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Critical SKUs Table */}
      <div className="flex flex-col">
        <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
          <span>Tabela de SKUs Críticos & em Ruptura (Ação Prioritária de Compras)</span>
        </div>
        <DataTable
          columns={criticalColumns}
          data={data?.critical_skus || []}
          searchPlaceholder="Buscar por SKU ou Nome do Produto..."
          searchKey="nome_produto"
          pageSize={8}
        />
      </div>
    </div>
  );
};
