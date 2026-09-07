import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { RoadmapInitiative } from '../../types/analytics';
import { ScopeBadge } from '../common/ScopeBadge';
import { MetricCard } from '../common/MetricCard';

export const RoadmapView: React.FC = () => {
  const [initiatives, setInitiatives] = useState<RoadmapInitiative[]>([]);
  const [roadmapSummary, setRoadmapSummary] = useState<any>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<string>('Todos');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    try {
      setLoading(true);
      const res = await api.getRoadmap();
      setInitiatives(res.initiatives || []);
      setRoadmapSummary(res.summary);
    } catch (err) {
      console.error('Erro ao carregar roadmap:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredInitiatives = initiatives.filter(init => {
    if (selectedHorizon === 'Todos') return true;
    if (selectedHorizon === 'Quick Wins') return init.type.includes('Quick Win');
    return init.horizon === selectedHorizon;
  });

  return (
    <div className="space-y-6 view-enter">
      <ScopeBadge
        tables={['vendas', 'atendimento', 'estoque', 'clientes', 'marketing']}
        scope="Síntese Executiva Transversal • 30 / 60 / 90 Dias"
        devSection="Conclusões & Quick Wins (Hipóteses 4, 5 e 6)"
      />

      {/* Roadmap Macro Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-4">
        <MetricCard
          label="Total de Iniciativas Mapeadas"
          value={`${roadmapSummary?.total_initiatives || 7} Iniciativas`}
          subtitle="Plano estruturado de 90 dias"
        />
        <MetricCard
          label="Quick Wins Imediatos (30 Dias)"
          value={`${roadmapSummary?.quick_wins_count || 2} Ações`}
          trend={{ value: 'R$ 14,9M Potencial', isPositive: true }}
          subtitle="WhatsApp + Liquidação"
          highlight
        />
        <MetricCard
          label="Valor Financeiro Mapeado"
          value={`R$ ${(((roadmapSummary?.total_potential_value || 24000000)) / 1e6).toFixed(1)}M`}
          subtitle="Redução de custos e caixa"
        />
      </div>

      {/* Horizon Filters */}
      <div className="flex items-center gap-1.5 sm:gap-2 p-2.5 sm:p-3.5 rounded-xl bg-[#11131a] border border-[#27272a] overflow-x-auto no-scrollbar touch-pan-x shadow-sm">
        <span className="text-xs text-[#a1a1aa] font-medium mr-1 whitespace-nowrap">Filtrar Horizonte:</span>
        {['Todos', 'Quick Wins', '30 Dias', '60 Dias', '90 Dias'].map(horizon => {
          const active = selectedHorizon === horizon;
          return (
            <button
              key={horizon}
              onClick={() => setSelectedHorizon(horizon)}
              className={`text-xs px-2.5 sm:px-3.5 py-1 sm:py-1.5 rounded-lg border whitespace-nowrap transition-all ${
                active
                  ? 'bg-[#38bdf8]/15 border-[#38bdf8]/60 text-[#38bdf8] font-semibold shadow-sm'
                  : 'bg-[#18181b] border-[#27272a] text-[#a1a1aa] hover:border-[#3f3f46] hover:text-[#f4f4f5]'
              }`}
            >
              {horizon}
            </button>
          );
        })}
      </div>

      {/* Initiative Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
        {filteredInitiatives.map(init => (
          <div
            key={init.id}
            className="p-4 sm:p-5 rounded-xl bg-[#11131a] border border-[#27272a] hover:border-[#38bdf8]/40 transition-all flex flex-col justify-between space-y-3 sm:space-y-4 shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-mono font-semibold px-2 sm:px-2.5 py-0.5 rounded-md bg-[#18181b] border border-[#27272a] text-[#38bdf8]">
                  {init.horizon}
                </span>
                <span
                  className={`text-xs font-mono px-2 sm:px-2.5 py-0.5 rounded-md font-semibold ${
                    init.type.includes('Quick Win')
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-[#18181b] text-[#a1a1aa] border border-[#27272a]'
                  }`}
                >
                  {init.type}
                </span>
              </div>

              <h4 className="text-sm sm:text-base font-bold text-[#f4f4f5] tracking-tight mb-1">
                {init.title}
              </h4>
              <div className="text-[11px] sm:text-xs text-[#71717a] font-mono mb-2">
                {init.hypothesis} • {init.category}
              </div>

              <p className="text-xs text-[#d4d4d8] leading-relaxed">
                {init.description}
              </p>
            </div>

            <div className="pt-3 border-t border-[#27272a] flex items-center justify-between text-xs">
              <div>
                <span className="text-[10px] sm:text-[11px] text-[#71717a] block">Impacto Estimado:</span>
                <span className="font-mono font-bold text-[#38bdf8] text-xs sm:text-sm">
                  {init.financial_impact_label}
                </span>
              </div>

              <div className="text-right">
                <span className="text-[10px] sm:text-[11px] text-[#71717a] block">Prazo:</span>
                <span className="font-mono text-[#f4f4f5] text-xs sm:text-sm">
                  {init.effort_days} dias
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
