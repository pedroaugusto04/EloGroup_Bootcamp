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

import { Sparkles, Mail } from 'lucide-react';

interface InventoryViewProps {
  filterOptions?: FilterOptions;
  onOpenAuditModal?: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  'Descontinuado': '#f43f5e',
  'Estoque Crítico': '#f59e0b',
  'Normal': '#10b981',
  'Excesso': '#38bdf8',
};

export const InventoryView: React.FC<InventoryViewProps> = ({ filterOptions, onOpenAuditModal }) => {
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

  const kpis = data?.kpis;

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
      key: 'deficit_potencial_unidades',
      header: 'Déficit potencial',
      align: 'right',
      render: r => (
        <span className="font-mono text-rose-400 font-semibold">
          {Number(r.deficit_potencial_unidades).toFixed(1)} un
        </span>
      ),
    },
    {
      key: 'lead_time_cadastral_dias',
      header: 'Lead time cadastral',
      align: 'right',
      render: r => `${r.lead_time_cadastral_dias} dias`,
    },
    {
      key: 'margem_potencialmente_exposta',
      header: 'Margem potencialmente exposta',
      align: 'right',
      render: r => `R$ ${Number(r.margem_potencialmente_exposta).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['estoque', 'vendas']}
        scope="Posição operacional fornecida • Tendência histórica de Vendas"
        devSection="Seção 3 & Seção 5: Hipótese 6 (Descompasso de Estoque & Ruptura)"
      />

      <div className="p-3 rounded-lg border border-[#38bdf8]/30 bg-[#38bdf8]/5 text-xs text-[#a1a1aa]">
        {data?.methodology_banner || 'Carregando escopo temporal e metodologia…'}
      </div>

      {/* Autonomous Inventory Audit & Email Dispatch Banner */}
      {onOpenAuditModal && (
        <div className="p-3.5 sm:p-4 rounded-xl bg-gradient-to-r from-[#18181b] via-[#151720] to-[#121624] border border-[#38bdf8]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 sm:p-2.5 rounded-lg bg-[#38bdf8]/15 border border-[#38bdf8]/30 text-[#38bdf8]">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs sm:text-sm font-semibold text-[#f4f4f5]">Análise de estoque sob demanda</h4>
              <p className="text-[11px] sm:text-xs text-[#a1a1aa]">
                Gere fatos reconciliados, cenários de liquidação e, se solicitado, envie o parecer por e-mail.
              </p>
            </div>
          </div>
          <button
            onClick={onOpenAuditModal}
            className="w-full sm:w-auto px-3.5 py-2 rounded-lg bg-[#38bdf8] hover:bg-[#0284c7] text-[#09090b] font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-[#38bdf8]/20 transition-all active:scale-95 whitespace-nowrap"
          >
            <Mail className="w-4 h-4" />
            <span>Gerar Auditoria</span>
          </button>
        </div>
      )}

      {/* Category Filter */}
      {filterOptions?.categories && (
        <div className="flex items-center gap-1.5 sm:gap-2 p-2.5 sm:p-3.5 rounded-lg bg-[#11131a] border border-[#27272a] flex-wrap">
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
                className={`text-[10px] sm:text-[11px] px-2 sm:px-2.5 py-0.5 rounded border transition-colors ${active
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
              className="text-[10px] sm:text-[11px] text-[#71717a] hover:text-[#f4f4f5] ml-1 underline"
            >
              Limpar
            </button>
          )}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
        <MetricCard
          label="Total de SKUs"
          value={kpis ? Number(kpis.total_skus).toLocaleString('pt-BR') : '—'}
          subtitle="Catálogo WMS"
        />
        <MetricCard
          label="SKUs em Ruptura"
          value={kpis ? `${kpis.skus_ruptura} SKUs` : '—'}
          trend={{ value: 'Sem Estoque', isPositive: false }}
          subtitle="Saldo disponível igual a zero"
          highlight
        />
        <MetricCard
          label="No/abaixo do ponto"
          value={kpis ? `${kpis.skus_criticos} SKUs` : '—'}
          trend={{ value: '<= Ponto Pedido', isPositive: false }}
          subtitle="Saldo positivo; sinal operacional"
        />
        <MetricCard
          label="Descontinuados"
          value={kpis?.capital_parado != null ? `R$ ${(kpis.capital_parado / 1e6).toFixed(1)}M` : '—'}
          trend={kpis?.descontinuados_valorados != null ? { value: `${kpis.descontinuados_valorados} valorados`, isPositive: false } : undefined}
          subtitle="Capital disponível coberto em Vendas"
        />
        <div className="col-span-2 sm:col-span-1 lg:col-span-1">
          <MetricCard
            label="Exposição no lead time"
            value={kpis ? `${kpis.skus_precisa_reposicao} SKUs` : '—'}
            subtitle="Cenário baseado em tendência histórica"
          />
        </div>
      </div>

      {/* Key Finding Executive Callout */}
      <div className="p-3 sm:p-3.5 rounded-lg bg-[#18181b] border border-[#27272a] text-xs text-[#d4d4d8] flex items-start gap-2.5 sm:gap-3">
        <div className="w-2 h-2 rounded-full bg-[#38bdf8] mt-1.5 shrink-0" />
        <div className="leading-relaxed">
          <span className="font-semibold text-[#f4f4f5]">Leitura metodológica:</span>{' '}
          Ruptura, ponto de pedido e exposição no lead time são sinais distintos. Alta cobertura requer revisão e não comprova excesso; valores de exposição são cenários, não perdas realizadas.
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        {/* Rupture by Category Stacked */}
        <div className="p-3 sm:p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span className="truncate">Sinais operacionais por categoria</span>
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.categories_rupture || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="categoria" stroke="#71717a" fontSize={10} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="skus_ruptura" name="Ruptura Real (Estoque = 0)" fill="#ef4444" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="skus_estoque_critico" name="Estoque Crítico (<= Ponto Pedido)" fill="#f59e0b" stackId="a" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Capital Breakdown by Status */}
        <div className="p-3 sm:p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span className="truncate">Capital coberto em Vendas por status</span>
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.status_breakdown || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="status_disponibilidade" stroke="#71717a" fontSize={10} tickLine={false} />
                <YAxis
                  stroke="#71717a"
                  fontSize={10}
                  tickFormatter={v => `${(v / 1e6).toFixed(1)}M`}
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
          <span>Prioridades para investigação de exposição no lead time cadastral</span>
        </div>
        <DataTable
          columns={criticalColumns}
          data={data?.critical_skus || []}
          searchPlaceholder="Buscar por SKU ou Nome..."
          searchKey="nome_produto"
          pageSize={8}
        />
      </div>
    </div>
  );
};
