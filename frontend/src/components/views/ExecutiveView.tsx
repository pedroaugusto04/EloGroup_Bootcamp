import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { ExecutiveOverviewData, SalesAnalyticsData, FilterOptions } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';
import { useTheme } from '../../context/ThemeContext';
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

const COLORS = ['#4200db', '#8575ff', '#6366f1', '#a855f7', '#10b981', '#f59e0b', '#ef4444'];

export const ExecutiveView: React.FC<ExecutiveViewProps> = ({ filterOptions }) => {
  const { isDark } = useTheme();
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
      className: 'font-mono text-[#4200db] dark:text-[#8575ff]',
      render: r => <span className="font-mono text-[#4200db] dark:text-[#8575ff]">{r.sku_id}</span>,
    },
    {
      key: 'nome_produto',
      header: 'Produto',
      render: r => r.nome_produto || r.produto || '—',
    },
    { key: 'categoria', header: 'Categoria' },
    {
      key: 'unidades_vendidas',
      header: 'Qtd Vendida',
      align: 'right',
      render: r => Number(r.unidades_vendidas || 0).toLocaleString('pt-BR'),
    },
    {
      key: 'receita_liquida',
      header: 'Receita Líquida',
      align: 'right',
      render: r => `R$ ${Number(r.receita_liquida ?? r.receita_total ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'margem_contribuicao',
      header: 'Margem (R$)',
      align: 'right',
      render: r => `R$ ${Number(r.margem_contribuicao ?? r.margem_total ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'margem_pct',
      header: 'Margem %',
      align: 'right',
      render: r => (
        <span className={`font-mono ${(r.margem_pct ?? 0) >= 50 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : (r.margem_pct ?? 0) > 0 ? 'text-[#5e6270] dark:text-[#a1a1aa]' : 'text-rose-600 dark:text-rose-400 font-bold'}`}>
          {Number(r.margem_pct || 0).toFixed(1)}%
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['vendas']}
        scope="27.758 transações (Vendas) • Jan/2023 a 26/Jan/2024"
        devSection="Seção 3: Observações por Tabela (Receita/Margem & Devoluções)"
      />

      {/* Filter Controls */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3 p-3 sm:p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa] font-medium">Status:</span>
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="text-xs bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] rounded px-2 sm:px-2.5 py-1 text-[#131920] dark:text-[#f4f4f5] focus:outline-none focus:border-[#4200db] dark:focus:border-[#8575ff]"
          >
            <option value="Aprovado">Aprovado</option>
            <option value="Todos">Todos</option>
            <option value="Aguardando">Aguardando</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa] font-medium">Ano:</span>
          <select
            value={selectedYear}
            onChange={e => setSelectedYear(e.target.value)}
            className="text-xs bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] rounded px-2 sm:px-2.5 py-1 text-[#131920] dark:text-[#f4f4f5] focus:outline-none focus:border-[#4200db] dark:focus:border-[#8575ff]"
          >
            <option value="Todos">Todos os Anos</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
          </select>
        </div>

        {filterOptions?.categories && filterOptions.categories.length > 0 && (
          <div className="flex items-center gap-1 sm:gap-1.5 flex-wrap w-full sm:w-auto pt-1 sm:pt-0 border-t sm:border-t-0 border-[#e6e5f0] dark:border-[#262046]/50">
            <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa] font-medium mr-1">Categorias:</span>
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
                      ? 'bg-[#e8e6ff] dark:bg-[#8575ff]/20 border-[#c4b8ff] dark:border-[#8575ff]/60 text-[#4200db] dark:text-[#8575ff] font-medium'
                      : 'bg-[#f8f7fc] dark:bg-[#181530] border-[#e6e5f0] dark:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:border-[#cbd5e1] dark:hover:border-[#4a3f85]'
                    }`}
                >
                  {cat}
                </button>
              );
            })}
            {selectedCats.length > 0 && (
              <button
                onClick={() => setSelectedCats([])}
                className="text-[10px] sm:text-[11px] text-[#8e92a0] dark:text-[#71717a] hover:text-[#4200db] dark:hover:text-[#f4f4f5] ml-1 underline"
              >
                Limpar
              </button>
            )}
          </div>
        )}
      </div>

      {/* Macro Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
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
          subtitle="Margem efetiva"
        />
        <MetricCard
          label="Total de Pedidos"
          value={Number(kpis.total_pedidos || 0).toLocaleString('pt-BR')}
          subtitle="Transações de Vendas"
        />
        <MetricCard
          label="Ticket Médio"
          value={`R$ ${Number(kpis.ticket_medio || 0).toFixed(2)}`}
          subtitle="Média por pedido"
        />
        <div className="col-span-2 sm:col-span-1 lg:col-span-1">
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
      </div>

      {/* Margin Decomposition Mini-Bar */}
      <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
        <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 sm:mb-3 flex items-center justify-between">
          <span>Decomposição da Receita Bruta à Margem Líquida</span>
          <span className="hidden sm:inline font-mono text-[11px] text-[#8e92a0] dark:text-[#71717a]">Tabela Vendas 2023/2024</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 text-xs">
          <div className="p-2 sm:p-2.5 rounded bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
            <span className="text-[#5e6270] dark:text-[#a1a1aa] block text-[10px] sm:text-[11px]">Receita Bruta Total</span>
            <span className="font-mono font-bold text-xs sm:text-sm text-[#131920] dark:text-[#f4f4f5]">
              R$ {((decomp.bruta || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="p-2 sm:p-2.5 rounded bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
            <span className="text-[#5e6270] dark:text-[#a1a1aa] block text-[10px] sm:text-[11px]">Descontos Concedidos</span>
            <span className="font-mono font-bold text-xs sm:text-sm text-rose-600 dark:text-rose-400">
              -R$ {((decomp.descontos || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="p-2 sm:p-2.5 rounded bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
            <span className="text-[#5e6270] dark:text-[#a1a1aa] block text-[10px] sm:text-[11px]">Custo Produtos (CMV)</span>
            <span className="font-mono font-bold text-xs sm:text-sm text-[#334155] dark:text-[#e4e4e7]">
              R$ {((decomp.custo_prod || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="p-2 sm:p-2.5 rounded bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
            <span className="text-[#5e6270] dark:text-[#a1a1aa] block text-[10px] sm:text-[11px]">Custo Total Frete</span>
            <span className="font-mono font-bold text-xs sm:text-sm text-[#334155] dark:text-[#e4e4e7]">
              R$ {((decomp.custo_frete || 0) / 1e6).toFixed(2)}M
            </span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        {/* Monthly Trend */}
        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] flex flex-col shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span className="truncate">Evolução Mensal (Receita vs. Margem)</span>
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={execData?.monthly_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="ano_mes" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
                <YAxis
                  stroke={isDark ? '#71717a' : '#8e92a0'}
                  fontSize={10}
                  tickFormatter={v => `${(v / 1e6).toFixed(1)}M`}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#181530' : '#ffffff',
                    borderColor: isDark ? '#262046' : '#e6e5f0',
                    color: isDark ? '#f4f4f5' : '#131920',
                    borderRadius: '8px',
                    fontSize: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }}
                  formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="margem_contribuicao" name="Margem Contribuição" fill={isDark ? '#94a3b8' : '#cbd5e1'} opacity={0.8} radius={[3, 3, 0, 0]} />
                <Line type="monotone" dataKey="receita_liquida" name="Receita Líquida" stroke={isDark ? '#8575ff' : '#4200db'} strokeWidth={2.5} dot={{ r: 2.5 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Performance */}
        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] flex flex-col shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span className="truncate">Desempenho por Canal de Venda</span>
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={execData?.channels || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="canal" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
                <YAxis
                  stroke={isDark ? '#71717a' : '#8e92a0'}
                  fontSize={10}
                  tickFormatter={v => `${(v / 1e6).toFixed(1)}M`}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#181530' : '#ffffff',
                    borderColor: isDark ? '#262046' : '#e6e5f0',
                    color: isDark ? '#f4f4f5' : '#131920',
                    borderRadius: '8px',
                    fontSize: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }}
                  formatter={(val: any) => [`R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="receita_liquida" name="Receita Líquida" fill={isDark ? '#8575ff' : '#4200db'} radius={[3, 3, 0, 0]} />
                <Bar dataKey="margem_contribuicao" name="Margem Contribuição" fill={isDark ? '#94a3b8' : '#94a3b8'} radius={[3, 3, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Grid: Returns Impact & Top SKUs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4">
        {/* Returns Reasons Pie */}
        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] flex flex-col shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-1">
            Impacto por Motivo de Devolução
          </div>
          <div className="text-[11px] text-[#5e6270] dark:text-[#71717a] mb-2">
            Total estornado: R$ {(((salesData?.returns_impact || []).reduce((acc, r) => acc + r.valor_devolvido, 0)) / 1e6).toFixed(2)}M
          </div>
          <div className="h-56 sm:h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={salesData?.returns_impact || []}
                  dataKey="valor_devolvido"
                  nameKey="motivo_devolucao"
                  cx="50%"
                  cy="50%"
                  innerRadius={38}
                  outerRadius={68}
                  paddingAngle={3}
                >
                  {(salesData?.returns_impact || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#181530' : '#ffffff',
                    borderColor: isDark ? '#262046' : '#e6e5f0',
                    color: isDark ? '#f4f4f5' : '#131920',
                    borderRadius: '8px',
                    fontSize: '11px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }}
                  formatter={(v: any) => `R$ ${Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
                />
                <Legend wrapperStyle={{ fontSize: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top SKUs Table */}
        <div className="lg:col-span-2 flex flex-col">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 flex items-center justify-between">
            <span>Top 50 Produtos por Faturamento & Margem</span>
          </div>
          <DataTable
            columns={skuColumns}
            data={salesData?.top_skus || []}
            searchPlaceholder="Buscar SKU ou Produto..."
            searchKey="nome_produto"
            pageSize={7}
          />
        </div>
      </div>
    </div>
  );
};
