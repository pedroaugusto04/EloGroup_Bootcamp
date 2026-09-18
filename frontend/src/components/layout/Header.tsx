import React from 'react';
import { ViewTab } from '../../types/analytics';
import { RefreshCw, Menu, Mail, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

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
  marketing: {
    title: 'Marketing & Eficiência de Mídia (ROAS)',
    subtitle: 'Desempenho do funil de aquisição, ROAS declarado, CAC, CTR e conversões por canal.',
  },
  customers: {
    title: 'Base de Clientes & RFM',
    subtitle: 'Matriz de segmentação RFM, curva de concentração de Pareto e LTV acumulado da base.',
  },
  support: {
    title: 'Atendimento, CX & Automação com IA',
    subtitle: 'Canais de entrada, CSAT, SLA real de resolução e dimensionamento de custos evitáveis com IA.',
  },
  inventory: {
    title: 'Estoque, Suprimentos & Ruptura',
    subtitle: 'Posição operacional de estoque; valores financeiros são reconciliados exclusivamente com Vendas.',
  },
  audit: {
    title: 'Auditoria dos Dados',
    subtitle: 'Diagnóstico de integridade, assimetria temporal e reconciliação entre Vendas, Clientes e Mídia.',
  },
  outliers: {
    title: 'Dispersão & Outliers (Tukey IQR)',
    subtitle: 'Análise estatística de anomalias, limites de quartis e desvios nas 5 tabelas.',
  },
  roadmap: {
    title: 'Plano Estratégico',
    subtitle: 'Business case consolidado, matriz de execução 30/60/90 dias, governança e sequenciamento.',
  },
  copilot: {
    title: 'Predictive Inventory Advisor',
    subtitle: 'Auditoria de compras, simulação de liquidação de descontinuados e inteligência preditiva em DuckDB.',
  },
  deliverables: {
    title: 'Documentos Executivos',
    subtitle: 'Dossiês executivos, relatórios de auditoria, modelagem financeira e artefatos do Bootcamp.',
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
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="h-14 sm:h-16 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff]/95 dark:bg-[#0d0b1a]/95 backdrop-blur px-3 sm:px-6 flex items-center justify-between shrink-0 select-none z-10 transition-colors duration-150">
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        {onOpenSidebar && (
          <button
            onClick={onOpenSidebar}
            className="p-2 -ml-1 rounded-lg text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5] hover:bg-[#f3f2f8] dark:hover:bg-[#181530] lg:hidden transition-colors shrink-0"
            title="Abrir Menu de Navegação"
            aria-label="Abrir Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="min-w-0">
          <h1 className="text-xs sm:text-base font-bold text-[#131920] dark:text-[#f4f4f5] tracking-tight truncate">
            {meta.title}
          </h1>
          <p className="hidden md:block text-xs text-[#5e6270] dark:text-[#71717a] font-sans truncate max-w-xl">
            {meta.subtitle}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md bg-[#f3f2f8] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#4200db]/40 dark:hover:border-[#8575ff]/40 text-[#4200db] dark:text-[#8575ff] transition-all active:scale-95 shadow-sm"
          title={isDark ? 'Alternar para Modo Claro (Padrão Case.html)' : 'Alternar para Modo Escuro'}
          aria-label="Alternar Tema"
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {onOpenAuditModal && (
          <button
            onClick={onOpenAuditModal}
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-md bg-[#e8e6ff] dark:bg-[#8575ff]/15 hover:bg-[#d9d5ff] dark:hover:bg-[#8575ff]/25 border border-[#c4b8ff] dark:border-[#8575ff]/40 text-[#4200db] dark:text-[#8575ff] text-xs font-semibold transition-all shadow-sm active:scale-95"
            title="Executar análise sob demanda e, se solicitado, enviar e-mail executivo"
          >
            <Mail className="w-3.5 h-3.5 text-[#4200db] dark:text-[#8575ff]" />
            <span className="hidden sm:inline">Gerar Auditoria</span>
          </button>
        )}

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-md bg-[#f3f2f8] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#cbd5e1] dark:hover:border-[#4a3f85] text-[#131920] dark:text-[#d4d4d8] text-xs font-medium transition-colors disabled:opacity-50 active:scale-95"
          title="Recarregar dados"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#4200db] dark:text-[#8575ff]' : 'text-[#5e6270] dark:text-[#a1a1aa]'}`} />
          <span className="hidden sm:inline">Atualizar</span>
        </button>
      </div>
    </header>
  );
};
