import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { ExecutiveOverviewData, SalesAnalyticsData, FilterOptions } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
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

interface ExecutiveViewProps {
  filterOptions?: FilterOptions;
}

const COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'];

export const ExecutiveView: React.FC<ExecutiveViewProps> = ({ filterOptions }) => {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('Aprovado');
  const [selectedYear, setSelectedYear] = useState('Todos');
  const [selectedCats, setSelectedCats] = useState<string[]>([]);
  
  const [execData, setExecData] = useState<ExecutiveOverviewData | null>(null);
  const [salesData, setSalesData] = useState<SalesAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [resExec, resSales] = await Promise.all([
        api.getExecutive(status, selectedYear, selectedCats),
        api.getSales([], selectedCats),
      ]);
      setExecData(resExec);
      setSalesData(resSales);
    } catch (err) {
      console.error('Erro ao carregar dados executivos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [status, selectedYear, selectedCats]);

  const kpis = execData?.kpis || {};
  const decomp = salesData?.decomposition || {
    bruta: 0,
    descontos: 0,
    liquida: 0,
    custo_prod: 0,
    custo_frete: 0,
    margem: 0,
  };

  const skuColumns: Column<any>[] = [
    {
      key: 'sku_id',
      header: 'SKU',
      className: 'font-mono text-[#38bdf8]',
      render: r => <span className="font-mono text-[#38bdf8]">{r.sku_id}</span>,
    },
    { key: 'nome_produto', header: 'Produto' },
    { key: 'categoria', header: 'Categoria' },
    {
      key: 'unidades_vendidas',
      header: 'Qtd Vendida',
      align: 'right',
      render: r => Number(r.unidades_vendidas).toLocaleString('pt-BR'),
    },
    {
      key: 'receita_liquida',
      header: 'Receita Líquida',
      align: 'right',
      render: r => `R$ ${Number(r.receita_liquida).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'margem_contribuicao',
      header: 'Margem (R$)',
      align: 'right',
      render: r => `R$ ${Number(r.margem_contribuicao).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'margem_pct',
      header: 'Margem %',
      align: 'right',
      render: r => (
        <span className={`font-mono ${r.margem_pct >= 50 ? 'text-emerald-400' : r.margem_pct > 0 ? 'text-[#a1a1aa]' : 'text-rose-400'}`}>
          {Number(r.margem_pct).toFixed(1)}%
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['vendas']}
        scope="27.753 transações (ERP) • Jan/2023 a 26/Jan/2024"
        devSection="Seção 3: Observações por Tabela (Receita/Margem & Devoluções)"
      />

      {/* Filter Controls */}
      <div className="flex flex-wrap items-center gap-3 p-3.5 rounded-lg bg-[#11131a] border border-[#27272a]">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#a1a1aa] font-medium">Status:</span>
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="text-xs bg-[#18181b] border border-[#27272a] rounded px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#38bdf8]"
          >
            <option value="Aprovado">Aprovado</option>
            <option value="Todos">Todos</option>
            <option value="Aguardando">Aguardando</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[#a1a1aa] font-medium">Ano:</span>
          <select
            value={selectedYear}
            onChange={e => setSelectedYear(e.target.value)}
            className="text-xs bg-[#18181b] border border-[#27272a] rounded px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#38bdf8]"
          >
            <option value="Todos">Todos os Anos</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
          </select>
        </div>

        {filterOptions?.categories && filterOptions.categories.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-[#a1a1aa] font-medium mr-1">Categorias:</span>
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
                  className={`text-[11px] px-2.5 py-0.5 rounded border transition-colors ${
                    active
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
      </div>

      {/* Macro Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <MetricCard
          label="Receita Líquida"
          value={`R$ ${((kpis.liquida || 0) / 1e6).toFixed(2)}M`}
          subtitle="Volume retido em caixa"
          highlight
        />
        <MetricCard
          label="Margem Contribuição"
          value={`R$ ${((kpis.margem || 0) / 1e6).toFixed(2)}M`}
          trend={{
            value: `${(((kpis.margem || 0) / (kpis.liquida || 1)) * 100).toFixed(1)}%`,
            isPositive: true,
          }}
          subtitle="Margem de contribuição efetiva"
        />
        <MetricCard
          label="Total de Pedidos"
          value={Number(kpis.total_pedidos || 0).toLocaleString('pt-BR')}
          subtitle="Volume de transações ERP"
        />
        <MetricCard
          label="Ticket Médio"
          value={`R$ ${Number(kpis.ticket_medio || 0).toFixed(2)}`}
          subtitle="Média por pedido aprovado"
        />
        <MetricCard
          label="Taxa Devolução"
          value={`${Number(kpis.taxa_devolucao || 0).toFixed(1)}%`}
          trend={{
            value: `${Number(kpis.taxa_devolucao || 0).toFixed(1)}%`,
            isPositive: false,
          }}
          subtitle="Impacto de estornos"
        />
      </div>

      {/* Margin Decomposition Mini-Bar */}
      <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
        <div className="text-xs font-semibold text-[#f4f4f5] mb-3 flex items-center justify-between">
          <span>Decomposição da Receita Bruta à Margem Líquida</span>
          <span className="font-mono text-[11px] text-[#71717a]">ERP Vendas 2023/2024</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-2.5 rounded bg-[#18181b] border border-[#27272a]">
            <span className="text-[#a1a1aa] block text-[11px]">Receita Bruta Total</span>
            <span className="font-mono font-bold text-sm text-[#f4f4f5]">
              R$ {((decomp.bruta || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="p-2.5 rounded bg-[#18181b] border border-[#27272a]">
            <span className="text-[#a1a1aa] block text-[11px]">Descontos Concedidos</span>
            <span className="font-mono font-bold text-sm text-rose-400">
              -R$ {((decomp.descontos || 0) / 1e6).toFixed(2)}M ({((decomp.descontos / (decomp.bruta || 1)) * 100).toFixed(1)}%)
            </span>
          </div>
          <div className="p-2.5 rounded bg-[#18181b] border border-[#27272a]">
            <span className="text-[#a1a1aa] block text-[11px]">Custo Produtos (CMV)</span>
            <span className="font-mono font-bold text-sm text-[#e4e4e7]">
              R$ {((decomp.custo_prod || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="p-2.5 rounded bg-[#18181b] border border-[#27272a]">
            <span className="text-[#a1a1aa] block text-[11px]">Custo Total Frete</span>
            <span className="font-mono font-bold text-sm text-[#e4e4e7]">
              R$ {((decomp.custo_frete || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Monthly Trend */}
        <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Evolução Mensal (Receita Líquida vs. Margem de Contribuição)</span>
          </div>
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={execData?.monthly_trend || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="ano_mes" stroke="#71717a" fontSize={11} tickLine={false} />
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
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar dataKey="margem_contribuicao" name="Margem Contribuição" fill="#94a3b8" opacity={0.7} radius={[3, 3, 0, 0]} />
                <Line type="monotone" dataKey="receita_liquida" name="Receita Líquida" stroke="#38bdf8" strokeWidth={2.5} dot={{ r: 3 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Performance */}
        <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Desempenho por Canal de Venda (Receita vs. Margem)</span>
          </div>
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={execData?.channels || []} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="canal" stroke="#71717a" fontSize={11} tickLine={false} />
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
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar dataKey="receita_liquida" name="Receita Líquida" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                <Bar dataKey="margem_contribuicao" name="Margem Contribuição" fill="#94a3b8" radius={[3, 3, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Grid: Returns Impact & Top SKUs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Returns Reasons Pie */}
        <div className="p-4 rounded-lg bg-[#11131a] border border-[#27272a] flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-1">
            Impacto Financeiro por Motivo de Devolução
          </div>
          <div className="text-[11px] text-[#71717a] mb-2">
            Total estornado: R$ {(((salesData?.returns_impact || []).reduce((acc, r) => acc + r.valor_devolvido, 0)) / 1e6).toFixed(2)}M
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={salesData?.returns_impact || []}
                  dataKey="valor_devolvido"
                  nameKey="motivo_devolucao"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {(salesData?.returns_impact || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '11px' }}
                  formatter={(v: any) => `R$ ${Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top SKUs Table */}
        <div className="lg:col-span-2 flex flex-col">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Top 50 Produtos por Faturamento & Margem</span>
          </div>
          <DataTable
            columns={skuColumns}
            data={salesData?.top_skus || []}
            searchPlaceholder="Buscar SKU ou Nome de Produto..."
            searchKey="nome_produto"
            pageSize={7}
          />
        </div>
      </div>
    </div>
  );
};
