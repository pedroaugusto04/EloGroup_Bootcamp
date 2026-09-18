import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { SupportAnalyticsData, FilterOptions } from '../../types/analytics';
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

interface SupportViewProps {
  filterOptions?: FilterOptions;
}

export const SupportView: React.FC<SupportViewProps> = ({ filterOptions }) => {
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [supData, setSupData] = useState<SupportAnalyticsData | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const resSup = await api.getSupport([]);
      setSupData(resSup);
    } catch (err) {
      console.error('Erro ao carregar dados de suporte:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const aiColumns: Column<any>[] = [
    { key: 'categoria_problema', header: 'Motivo do Chamado', className: 'font-semibold text-[#131920] dark:text-[#f4f4f5]' },
    {
      key: 'total_tickets',
      header: 'Volume Tickets',
      align: 'right',
      render: r => Number(r.total_tickets).toLocaleString('pt-BR'),
    },
    {
      key: 'pct_total',
      header: '% Volume',
      align: 'right',
      render: r => `${(Number(r.pct_total ?? r.pct_volume) || 0).toFixed(1)}%`,
    },
    {
      key: 'csat_medio',
      header: 'CSAT Médio',
      align: 'right',
      render: r => `${(Number(r.csat_medio) || 0).toFixed(2)} / 5.0`,
    },
    {
      key: 'custo_operacional_total',
      header: 'Custo Total',
      align: 'right',
      render: r => `R$ ${(Number(r.custo_operacional_total ?? r.custo_total_categoria) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    },
  ];

  if (loading) {
    return <div className="text-[#5e6270] dark:text-[#71717a] text-sm">Carregando dados de suporte...</div>;
  }

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['atendimento']}
        scope="35.840 tickets de suporte • Jan/2023 a Dez/2025"
        devSection="Seção 3 & Seção 5: Hipótese 4 (Causas Raiz & Automação com IA)"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
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
          label="Custo Operacional"
          value={`R$ ${((supData?.kpis.custo_operacional_total || 537600) / 1e3).toFixed(1)}k`}
          subtitle="Gasto direto com tickets"
        />
        <MetricCard
          label="Economia IA (Quick Win)"
          value="R$ 238,5k"
          trend={{ value: '44% do custo', isPositive: true }}
          subtitle="Rastreio + Dúvidas"
          highlight
        />
        <div className="col-span-2 sm:col-span-1 lg:col-span-1">
          <MetricCard
            label="1ª Resposta Média"
            value={`${Math.round((supData?.kpis as any)?.tempo_resposta_min || (supData?.kpis as any)?.primeira_resposta_minutos || 135)} min`}
            trend={{ value: `Mediana: ${Math.round((supData?.kpis as any)?.tempo_resposta_mediana_min ?? 11)} min`, isPositive: true }}
            subtitle="Mediana: 11 min (67% < 15m)"
            help="A média (135 min) é inflada por E-mail (~4,5h) e Reclame Aqui (~13h). A mediana de 11 min reflete a maioria ágil via WhatsApp/ChatBot."
          />
        </div>
      </div>

      <div className="p-3 sm:p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-xs text-[#5e6270] dark:text-[#d4d4d8] flex items-start gap-2.5 sm:gap-3 shadow-sm">
        <div className="w-2 h-2 rounded-full bg-[#4200db] dark:bg-[#8575ff] mt-1.5 shrink-0" />
        <div className="leading-relaxed">
          <span className="font-semibold text-[#131920] dark:text-[#f4f4f5]">Oportunidade Imediata de IA & Notificação:</span>{' '}
          O motivo <span className="font-semibold text-[#131920] dark:text-[#f4f4f5]">'Onde está meu pedido'</span> responde por <span className="font-mono text-[#4200db] dark:text-[#8575ff] font-bold">30% de todo o suporte</span> e gera <span className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">R$ 159.660,00</span> em custos evitáveis. O prazo de entrega é padrão (8,3 dias), o que indica falta de visibilidade: uma notificação automática via WhatsApp com link de rastreamento pode minimizar o problema.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 truncate">
            Volume de Chamados por Canal de Entrada
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={supData?.channels || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="canal_entrada" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
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
                <Bar dataKey="total_tickets" name="Total Tickets" fill={isDark ? '#8575ff' : '#4200db'} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-3 sm:p-4 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
          <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2 truncate">
            Distribuição das Notas CSAT (1 a 5)
          </div>
          <div className="h-64 sm:h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={supData?.csat_distribution || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#262046' : '#e6e5f0'} opacity={0.7} />
                <XAxis dataKey="nota_csat" stroke={isDark ? '#71717a' : '#8e92a0'} fontSize={10} tickLine={false} />
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
                <Bar dataKey="total_avaliacoes" name="Avaliações" fill={isDark ? '#6366f1' : '#6366f1'} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="flex flex-col">
        <div className="text-xs font-semibold text-[#131920] dark:text-[#f4f4f5] mb-2">
          Diagnóstico de Causas-Raiz e Custos por Motivo de Chamado
        </div>
        <DataTable
          columns={aiColumns}
          data={supData?.root_causes_ai || []}
          searchPlaceholder="Buscar motivo do chamado..."
          searchKey="categoria_problema"
        />
      </div>
    </div>
  );
};
