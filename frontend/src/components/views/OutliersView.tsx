import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { OutliersData } from '../../types/analytics';
import { MetricCard } from '../common/MetricCard';
import { ScopeBadge } from '../common/ScopeBadge';
import { DataTable, Column } from '../common/DataTable';

export const OutliersView = () => {
  const [loading, setLoading] = useState(true);
  const [selectedTable, setSelectedTable] = useState('vendas');
  const [selectedMetric, setSelectedMetric] = useState<string | undefined>(undefined);
  const [outliersData, setOutliersData] = useState<OutliersData | null>(null);

  const fetchOutliers = async () => {
    try {
      setLoading(true);
      const res = await api.getOutliers(selectedTable, selectedMetric);
      setOutliersData(res);
      if (!selectedMetric && res.selected_metric) {
        setSelectedMetric(res.selected_metric);
      }
    } catch (err) {
      console.error('Erro ao carregar outliers:', err);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return <div className="text-[#71717a] text-sm">Carregando dados de outliers...</div>;
  }

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={[selectedTable]}
        scope="Detecção de Anomalias Estatísticas • Critério Tukey IQR (1.5x)"
        devSection="Seção 2: Outliers e Anomalias (DEVELOPMENT.md)"
      />

      <div className="flex flex-wrap items-center gap-2 sm:gap-3 p-3 sm:p-3.5 rounded-lg bg-[#131126] border border-[#262046]">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-xs text-[#a1a1aa] font-medium">Tabela:</span>
          <select
            value={selectedTable}
            onChange={e => {
              setSelectedTable(e.target.value);
              setSelectedMetric(undefined);
            }}
            className="text-xs bg-[#181530] border border-[#262046] rounded px-2 sm:px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#8575ff]"
          >
            {(outliersData?.available_tables || ['vendas', 'estoque', 'clientes', 'atendimento', 'marketing']).map(t => (
              <option key={t} value={t}>{t.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-xs text-[#a1a1aa] font-medium">Métrica:</span>
          <select
            value={selectedMetric || outliersData?.selected_metric || ''}
            onChange={e => setSelectedMetric(e.target.value)}
            className="text-xs bg-[#181530] border border-[#262046] rounded px-2 sm:px-2.5 py-1 text-[#f4f4f5] focus:outline-none focus:border-[#8575ff]"
          >
            {(outliersData?.available_metrics || []).map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
      </div>

      {outliersData && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
          <MetricCard
            label="Q1 (25%)"
            value={Number(outliersData.overall_stats.q1).toFixed(1)}
            subtitle="Limite inferior"
          />
          <MetricCard
            label="Mediana (50%)"
            value={Number(outliersData.overall_stats.median).toFixed(1)}
            subtitle="Tendência central"
          />
          <MetricCard
            label="Q3 (75%)"
            value={Number(outliersData.overall_stats.q3).toFixed(1)}
            subtitle="Limite superior"
          />
          <MetricCard
            label="IQR"
            value={Number(outliersData.overall_stats.iqr).toFixed(1)}
            subtitle="Interquartil"
          />
          <div className="col-span-2 sm:col-span-1 lg:col-span-1">
            <MetricCard
              label="Total Outliers"
              value={`${outliersData.overall_stats.outliers_count}`}
              trend={{
                value: `${Number(outliersData.overall_stats.outliers_pct).toFixed(1)}%`,
                isPositive: false,
              }}
              subtitle="Além de 1.5x IQR"
              highlight
            />
          </div>
        </div>
      )}

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
  );
};
