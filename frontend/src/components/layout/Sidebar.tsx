import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Users,
  Headphones,
  Package,
  ShieldCheck,
  SlidersHorizontal,
  Target,
  Bot,
  Layers,
  ChevronRight,
  X,
} from 'lucide-react';
import { ViewTab } from '../../types/analytics';

interface SidebarProps {
  activeTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  id: ViewTab;
  label: string;
  tag: string;
  icon: React.ElementType;
  description: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: 'ANALYTICS & OPERAÇÃO',
    items: [
      {
        id: 'executive',
        label: 'Visão Executiva & Vendas',
        tag: '01',
        icon: BarChart3,
        description: 'KPIs macro, rentabilidade e margem',
      },
      {
        id: 'marketing',
        label: 'Marketing & Mídia (ROAS)',
        tag: '02',
        icon: TrendingUp,
        description: 'Funil de aquisição, CAC e conversões',
      },
      {
        id: 'customers',
        label: 'Clientes & RFM (Hipótese 5)',
        tag: '03',
        icon: Users,
        description: 'Concentração de Pareto e LTV histórico',
      },
      {
        id: 'support',
        label: 'Atendimento & IA (Hipótese 4)',
        tag: '04',
        icon: Headphones,
        description: 'Causas-raiz, SLA e economia com IA',
      },
      {
        id: 'inventory',
        label: 'Estoque & Suprimentos (Hip. 6)',
        tag: '05',
        icon: Package,
        description: 'Ruptura em Beleza e descontinuados',
      },
    ],
  },
  {
    title: 'GOVERNANÇA & ESTRATÉGIA',
    items: [
      {
        id: 'audit',
        label: 'Auditoria Relacional de Dados',
        tag: '06',
        icon: ShieldCheck,
        description: 'Confronto entre as 5 bases e assimetrias',
      },
      {
        id: 'outliers',
        label: 'Dispersão & Outliers (Tukey IQR)',
        tag: '07',
        icon: SlidersHorizontal,
        description: 'Detecção de anomalias estatísticas',
      },
      {
        id: 'roadmap',
        label: 'Plano Estratégico 30/60/90',
        tag: '08',
        icon: Target,
        description: 'Matriz de esforço x impacto e quick wins',
      },
      {
        id: 'copilot',
        label: 'Copiloto de Estoque IA',
        tag: '09',
        icon: Bot,
        description: 'Consultor inteligente em tempo real',
      },
    ],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  isOpen,
  onClose,
}) => {
  const handleItemClick = (id: ViewTab) => {
    onTabChange(id);
    onClose();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-200"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-72 sm:w-80 lg:w-64 xl:w-72 bg-[#121215] border-r border-[#27272a] flex flex-col h-full shrink-0 select-none transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-[#27272a] bg-[#0d0d10] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-[#38bdf8]/10 border border-[#38bdf8]/30 flex items-center justify-center text-[#38bdf8] shadow-sm">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <div className="text-sm font-bold tracking-tight text-[#f4f4f5] flex items-center gap-1.5">
                <span>VÉRTICE</span>
              </div>
            </div>
          </div>

          {/* Close button on Mobile */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#a1a1aa] hover:text-[#f4f4f5] hover:bg-[#18181b] lg:hidden transition-colors"
            title="Fechar menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation List by Section */}
        <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
          {navSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-1">
              <div className="px-2 py-1 text-[10px] font-mono font-bold tracking-wider text-[#71717a] uppercase">
                {section.title}
              </div>
              <div className="space-y-1">
                {section.items.map(item => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleItemClick(item.id)}
                      className={`w-full text-left p-2.5 rounded-lg border transition-all duration-150 flex items-start gap-3 group ${
                        isActive
                          ? 'bg-[#18181b] border-[#38bdf8]/50 shadow-[0_0_12px_rgba(56,189,248,0.08)]'
                          : 'bg-transparent border-transparent hover:bg-[#18181b]/60 hover:border-[#27272a]'
                      }`}
                    >
                      <div
                        className={`mt-0.5 p-1.5 rounded-md transition-colors shrink-0 ${
                          isActive
                            ? 'bg-[#38bdf8]/15 text-[#38bdf8]'
                            : 'bg-[#18181b] text-[#71717a] group-hover:text-[#a1a1aa]'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-xs font-semibold truncate ${
                              isActive ? 'text-[#f4f4f5]' : 'text-[#d4d4d8] group-hover:text-[#f4f4f5]'
                            }`}
                          >
                            {item.label}
                          </span>
                          <span className="text-[10px] font-mono text-[#71717a] ml-1">
                            {item.tag}
                          </span>
                        </div>
                        <p className="text-[11px] text-[#71717a] truncate mt-0.5 font-sans leading-tight">
                          {item.description}
                        </p>
                      </div>

                      {isActive && (
                        <ChevronRight className="w-3.5 h-3.5 text-[#38bdf8] self-center shrink-0" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer Info */}
        <div className="p-3 border-t border-[#27272a] bg-[#0d0d10] text-[11px] font-mono text-[#71717a]">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              DuckDB Live
            </span>
            <span>v2.0.0</span>
          </div>
          <div className="mt-1 text-[10px] text-[#52525b]">
            Bootcamp EloGroup 2026
          </div>
        </div>
      </aside>
    </>
  );
};
