import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { MarketingAnalyticsData, FilterOptions } from '../../types/analytics';
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
} from 'recharts';

interface MarketingViewProps {
  filterOptions?: FilterOptions;
}

export const MarketingView: React.FC<MarketingViewProps> = ({ filterOptions }) => {
  const [loading, setLoading] = useState(true);
  const [mktData, setMktData] = useState<MarketingAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const resMkt = await api.getMarketing([]);
      setMktData(resMkt);
    } catch (err) {
      console.error('Erro ao carregar dados de marketing:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

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

  if (loading) {
    return <div className="text-[#71717a] text-sm">Carregando dados de marketing...</div>;
  }

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['marketing']}
        scope="3.500 campanhas de mídia declaradas • Jan/2023 a Dez/2025"
        devSection="Seção 3: Observações por Tabela (Marketing & ROAS Declarado)"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
        <MetricCard
          label="Investimento Mídia"
          value={`R$ ${((mktData?.kpis.invest_total || 0) / 1e6).toFixed(1)}M`}
          subtitle="Gasto em plataformas"
        />
        <MetricCard
          label="Receita Gerada"
          value={`R$ ${((mktData?.kpis.rec_total || 0) / 1e6).toFixed(1)}M`}
          subtitle="Atribuído pelas redes"
        />
        <MetricCard
          label="ROAS Global"
          value={`${Number(mktData?.kpis.roas_global || 0).toFixed(2)}x`}
          trend={{ value: 'Plataformas', isPositive: true }}
          subtitle="Retorno aparente"
          highlight
        />
        <MetricCard
          label="CAC Médio"
          value={`R$ ${Number(mktData?.kpis.cac_medio || 0).toFixed(2)}`}
          subtitle="Custo de aquisição"
        />
        <div className="col-span-2 sm:col-span-1 lg:col-span-1">
          <MetricCard
            label="Total Conversões"
            value={`${((mktData?.kpis.conv_total || 0) / 1e6).toFixed(1)}M`}
            subtitle="Conversões declaradas"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        <div className="p-3 sm:p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 truncate">
            Investimento vs. Receita por Canal de Mídia
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mktData?.channels || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="canal" stroke="#71717a" fontSize={10} tickLine={false} />
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
                <Bar dataKey="investimento" name="Investimento (R$)" fill="#94a3b8" radius={[3, 3, 0, 0]} />
                <Bar dataKey="receita_gerada" name="Receita Declarada (R$)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-3 sm:p-4 rounded-lg bg-[#11131a] border border-[#27272a]">
          <div className="text-xs font-semibold text-[#f4f4f5] mb-2 truncate">
            Eficiência Relativa: ROAS vs. CAC por Canal
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mktData?.channels || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" opacity={0.6} />
                <XAxis dataKey="canal" stroke="#71717a" fontSize={10} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '6px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="roas" name="ROAS (x)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                <Bar dataKey="cac" name="CAC (R$)" fill="#f59e0b" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

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
  );
};
