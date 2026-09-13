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
          value={roadmapSummary ? `${roadmapSummary.total_initiatives} Iniciativas` : '—'}
          subtitle="Plano estruturado de 90 dias"
        />
        <MetricCard
          label="Quick Wins Imediatos (30 Dias)"
          value={roadmapSummary ? `${roadmapSummary.quick_wins_count} Ações` : '—'}
          subtitle="WhatsApp + Liquidação"
          highlight
        />
        <MetricCard
          label="Valor Financeiro Mapeado"
          value={roadmapSummary ? `R$ ${(roadmapSummary.total_potential_value / 1e6).toFixed(1)}M` : '—'}
          subtitle="Redução de custos e caixa"
        />
      </div>

      {/* Horizon Filters */}
      <div className="flex items-center gap-1.5 sm:gap-2 p-2.5 sm:p-3.5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] overflow-x-auto no-scrollbar touch-pan-x shadow-sm">
        <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa] font-medium mr-1 whitespace-nowrap">Filtrar Horizonte:</span>
        {['Todos', 'Quick Wins', '30 Dias', '60 Dias', '90 Dias'].map(horizon => {
          const active = selectedHorizon === horizon;
          return (
            <button
              key={horizon}
              onClick={() => setSelectedHorizon(horizon)}
              className={`text-xs px-2.5 sm:px-3.5 py-1 sm:py-1.5 rounded-lg border whitespace-nowrap transition-all ${
                active
                  ? 'bg-[#e8e6ff] dark:bg-[#8575ff]/20 border-[#c4b8ff] dark:border-[#8575ff]/60 text-[#4200db] dark:text-[#8575ff] font-semibold shadow-sm'
                  : 'bg-[#f8f7fc] dark:bg-[#181530] border-[#e6e5f0] dark:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:border-[#4200db]/40 dark:hover:border-[#4a3f85] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
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
            className="p-4 sm:p-5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#4200db]/40 dark:hover:border-[#8575ff]/50 transition-all flex flex-col justify-between space-y-3 sm:space-y-4 shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-mono font-semibold px-2 sm:px-2.5 py-0.5 rounded-md bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-[#4200db] dark:text-[#8575ff]">
                  {init.horizon}
                </span>
                <span
                  className={`text-xs font-mono px-2 sm:px-2.5 py-0.5 rounded-md font-semibold ${
                    init.type.includes('Quick Win')
                      ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                      : 'bg-[#f8f7fc] dark:bg-[#181530] text-[#5e6270] dark:text-[#a1a1aa] border border-[#e6e5f0] dark:border-[#262046]'
                  }`}
                >
                  {init.type}
                </span>
              </div>

              <h4 className="text-sm sm:text-base font-bold text-[#131920] dark:text-[#f4f4f5] tracking-tight mb-1">
                {init.title}
              </h4>
              <div className="text-[11px] sm:text-xs text-[#5e6270] dark:text-[#71717a] font-mono mb-2">
                {init.hypothesis} • {init.category}
              </div>

              <p className="text-xs text-[#40434f] dark:text-[#d4d4d8] leading-relaxed">
                {init.description}
              </p>
            </div>

            <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] flex items-center justify-between text-xs">
              <div>
                <span className="text-[10px] sm:text-[11px] text-[#5e6270] dark:text-[#71717a] block">Impacto Estimado:</span>
                <span className="font-mono font-bold text-[#4200db] dark:text-[#8575ff] text-xs sm:text-sm">
                  {init.financial_impact_label}
                </span>
              </div>

              <div className="text-right">
                <span className="text-[10px] sm:text-[11px] text-[#5e6270] dark:text-[#71717a] block">Prazo:</span>
                <span className="font-mono text-[#131920] dark:text-[#f4f4f5] text-xs sm:text-sm">
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
