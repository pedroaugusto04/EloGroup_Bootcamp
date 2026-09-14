import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { CustomerAnalyticsData, FilterOptions } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';
import { useTheme } from '../../context/ThemeContext';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface CustomersViewProps {
  filterOptions?: FilterOptions;
}

export const CustomersView: React.FC<CustomersViewProps> = ({ filterOptions }) => {
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [custData, setCustData] = useState<CustomerAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const resCust = await api.getCustomers([]);
      setCustData(resCust);
    } catch (err) {
      console.error('Erro ao carregar dados de clientes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const paretoColumns: Column<any>[] = [
    {
      key: 'segmento_rfm',
      header: 'Segmento RFM',
      className: 'font-semibold text-[#131920] dark:text-[#f4f4f5]',
      render: r => r.segmento_rfm || r.segmento || 'Não Definido',
    },
    {
      key: 'total_clientes',
      header: 'Clientes',
      align: 'right',
      render: r => Number(r.total_clientes || 0).toLocaleString('pt-BR'),
    },
    {
      key: 'pct_base_clientes',
      header: '% Base',
      align: 'right',
      render: r => `${Number(r.pct_base_clientes ?? r.pct_base ?? 0).toFixed(1)}%`,
    },
    {
      key: 'ltv_total',
      header: 'LTV Acumulado',
      align: 'right',
      render: r => `R$ ${((Number(r.ltv_total) || 0) / 1e6).toFixed(2)}M`,
    },
    {
      key: 'pct_ltv_total',
      header: '% LTV Total',
      align: 'right',
      render: r => (
        <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
          {Number(r.pct_ltv_total || 0).toFixed(1)}%
        </span>
      ),
    },
    {
      key: 'ticket_medio_segmento',
      header: 'Ticket Médio',
      align: 'right',
      render: r => `R$ ${Number(r.ticket_medio_segmento ?? r.ticket_medio_historico ?? 0).toFixed(2)}`,
    },
    {
      key: 'pedidos_medios',
      header: 'Pedidos Médios',
      align: 'right',
      render: r => Number(r.pedidos_medios ?? r.media_pedidos ?? 0).toFixed(1),
    },
  ];

  if (loading) {
    return <div className="text-[#5e6270] dark:text-[#71717a] text-sm">Carregando dados de clientes...</div>;
  }

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['clientes']}
        scope="15.000 clientes cadastrados • Ano Base 2026"
        devSection="Seção 3 & Seção 5: Segmentos de Clientes & Concentração"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
        <MetricCard
          label="Total de Clientes"
          value={Number(custData?.kpis.total_clientes || 15000).toLocaleString('pt-BR')}
          subtitle="Base total de clientes"
        />
        <MetricCard
          label="LTV Médio"
          value={`R$ ${Number(custData?.kpis.ltv_medio || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0 })}`}
          subtitle="Média histórica"
          highlight
        />
        <MetricCard
          label="Frequência Média"
          value={`${Number(custData?.kpis.frequencia_media || 0).toFixed(1)} ped.`}
          subtitle="Compras por cliente"
        />
        <MetricCard
          label="Renda Média"
          value={`R$ ${Number(custData?.kpis.renda_media || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0 })}`}
          subtitle="Perfil cadastral"
        />
        <div className="col-span-2 sm:col-span-1 lg:col-span-1">
          <MetricCard
            label="Idade Média"
            value={`${Math.round(custData?.kpis.idade_media || 42)} anos`}
            subtitle="Ano base 2026"
          />
        </div>
      </div>

      <div className="p-3 sm:p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-xs text-[#5e6270] dark:text-[#d4d4d8] flex items-start gap-2.5 sm:gap-3 shadow-sm">
        <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
        <div className="leading-relaxed">
          <span className="font-semibold text-[#131920] dark:text-[#f4f4f5]">Diagnóstico de Concentração de Clientes:</span>{' '}
          Clientes dos segmentos <span className="font-semibold text-[#131920] dark:text-[#f4f4f5]">Campeões</span> e <span className="font-semibold text-[#131920] dark:text-[#f4f4f5]">Fiéis</span> são poucos em volume, mas representam a maior fatia do LTV acumulado. Em contrapartida, <span className="font-mono text-amber-600 dark:text-amber-400 font-semibold">46,7% da base</span> está nas faixas de risco.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 truncate">
            Distribuição de Clientes por Segmento RFM
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={custData?.segments || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="segmento" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
                <YAxis stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#181530' : '#ffffff',
                    borderColor: isDark ? '#262046' : '#e6e5f0',
                    color: isDark ? '#f4f4f5' : '#131920',
                    borderRadius: '8px',
                    fontSize: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }}
                />
                <Bar dataKey="total_clientes" name="Total Clientes" fill={isDark ? '#8575ff' : '#4200db'} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 truncate">
            LTV Médio por Segmento RFM (R$)
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={custData?.segments || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="segmento" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
                <YAxis
                  stroke={isDark ? '#71717a' : '#8e92a0'}
                  fontSize={10}
                  tickFormatter={v => `${(v / 1e3).toFixed(0)}k`}
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
                <Bar dataKey="ltv_medio" name="LTV Médio (R$)" fill="#10b981" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="flex flex-col">
        <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2">
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
  );
};
