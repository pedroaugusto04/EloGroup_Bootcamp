import React from 'react';
import { ViewTab } from '../../types/analytics';
import { Sparkles, RefreshCw } from 'lucide-react';

interface HeaderProps {
  activeTab: ViewTab;
  onRefresh: () => void;
  loading?: boolean;
}

const titles: Record<ViewTab, { title: string; subtitle: string }> = {
  executive: {
    title: 'Visão Executiva & Rentabilidade',
    subtitle: 'Métricas consolidadas de vendas, margem de contribuição, custos e top produtos.',
  },
  inventory: {
    title: 'Estoque, Suprimentos & Ruptura',
    subtitle: 'Diagnóstico de 99 SKUs zerados, 701 críticos e R$ 14,7M em produtos descontinuados.',
  },
  growth: {
    title: 'Growth, Segmentos RFM & Atendimento',
    subtitle: 'Eficiência de canais de mídia, concentração de receita na base e causas-raiz de suporte.',
  },
  audit: {
    title: 'Auditoria & Integridade de Dados',
    subtitle: 'Auditoria de integridade relacional entre bases e detecção de dispersão e outliers (Tukey IQR).',
  },
  copilot: {
    title: 'Copiloto de Estoque IA & Plano Estratégico',
    subtitle: 'Consultoria conversacional inteligente via LangGraph ReAct e priorização do roadmap 30/60/90.',
  },
};

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onRefresh,
  loading,
}) => {
  const meta = titles[activeTab];

  return (
    <header className="h-16 border-b border-[#27272a] bg-[#0d0d10]/90 backdrop-blur px-6 flex items-center justify-between shrink-0 select-none">
      <div>
        <h1 className="text-base font-bold text-[#f4f4f5] tracking-tight flex items-center gap-2">
          {meta.title}
        </h1>
        <p className="text-xs text-[#71717a] font-sans truncate max-w-xl">
          {meta.subtitle}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#18181b] border border-[#27272a] hover:border-[#3f3f46] text-[#d4d4d8] text-xs font-medium transition-colors disabled:opacity-50"
          title="Recarregar dados do DuckDB"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#38bdf8]' : 'text-[#a1a1aa]'}`} />
          <span>Atualizar</span>
        </button>

        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#38bdf8]/10 border border-[#38bdf8]/25 text-[#38bdf8] text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5" />
          <span>EloGroup Retail Suite</span>
        </div>
      </div>
    </header>
  );
};
