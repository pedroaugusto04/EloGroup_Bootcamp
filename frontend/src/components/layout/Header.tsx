import React from 'react';
import { ViewTab } from '../../types/analytics';
import { RefreshCw, Menu, Mail } from 'lucide-react';

interface HeaderProps {
  activeTab: ViewTab;
  onRefresh: () => void;
  loading?: boolean;
  onOpenSidebar?: () => void;
  onOpenAuditModal?: () => void;
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
  roadmap: {
    title: 'Plano de Ação Estratégico (30/60/90 Dias)',
    subtitle: 'Síntese executiva transversal, matriz de esforço x impacto e cronograma de quick wins.',
  },
  copilot: {
    title: 'Copiloto Analítico de Estoque IA',
    subtitle: 'Consultor em tempo real para simulações e diagnósticos.',
  },
};

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onRefresh,
  loading,
  onOpenSidebar,
  onOpenAuditModal,
}) => {
  const meta = titles[activeTab];

  return (
    <header className="h-14 sm:h-16 border-b border-[#27272a] bg-[#0d0d10]/95 backdrop-blur px-3 sm:px-6 flex items-center justify-between shrink-0 select-none z-10">
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        {onOpenSidebar && (
          <button
            onClick={onOpenSidebar}
            className="p-2 -ml-1 rounded-lg text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b] lg:hidden transition-colors shrink-0"
            title="Abrir Menu de Navegação"
            aria-label="Abrir Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="min-w-0">
          <h1 className="text-xs sm:text-base font-bold text-[#f4f4f5] tracking-tight truncate">
            {meta.title}
          </h1>
          <p className="hidden md:block text-xs text-[#71717a] font-sans truncate max-w-xl">
            {meta.subtitle}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {onOpenAuditModal && (
          <button
            onClick={onOpenAuditModal}
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-md bg-[#38bdf8]/10 hover:bg-[#38bdf8]/20 border border-[#38bdf8]/40 hover:border-[#38bdf8]/70 text-[#38bdf8] text-xs font-semibold transition-all shadow-sm active:scale-95"
            title="Disparar auditoria autônoma e enviar e-mail executivo à diretoria"
          >
            <Mail className="w-3.5 h-3.5 text-[#38bdf8]" />
            <span className="hidden sm:inline">Gerar Auditoria</span>
          </button>
        )}

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-md bg-[#18181b] border border-[#27272a] hover:border-[#3f3f46] text-[#d4d4d8] text-xs font-medium transition-colors disabled:opacity-50 active:scale-95"
          title="Recarregar dados do DuckDB"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#38bdf8]' : 'text-[#a1a1aa]'}`} />
          <span className="hidden sm:inline">Atualizar</span>
        </button>
      </div>
    </header>
  );
};
