import React from 'react';
import {
  BarChart3,
  Package,
  Users,
  ShieldCheck,
  Bot,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { ViewTab } from '../../types/analytics';

interface SidebarProps {
  activeTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
}

interface NavItem {
  id: ViewTab;
  label: string;
  tag: string;
  icon: React.ElementType;
  description: string;
}

const navItems: NavItem[] = [
  {
    id: 'executive',
    label: 'Visão Executiva & Vendas',
    tag: '01',
    icon: BarChart3,
    description: 'KPIs macro, rentabilidade e decomposição de margem',
  },
  {
    id: 'inventory',
    label: 'Estoque & Suprimentos',
    tag: '02',
    icon: Package,
    description: 'Diagnóstico de ruptura e capital em descontinuados',
  },
  {
    id: 'growth',
    label: 'Growth, Clientes & Suporte',
    tag: '03',
    icon: Users,
    description: 'Eficiência de canais, Pareto RFM e automação IA',
  },
  {
    id: 'audit',
    label: 'Auditoria & Integridade',
    tag: '04',
    icon: ShieldCheck,
    description: 'Incoerências entre bases e análise de outliers IQR',
  },
  {
    id: 'copilot',
    label: 'Copiloto IA & Roadmap',
    tag: '05',
    icon: Bot,
    description: 'Consultor ReAct LangGraph e plano 30/60/90 dias',
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <aside className="w-64 md:w-72 bg-[#121215] border-r border-[#27272a] flex flex-col h-screen shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#27272a] bg-[#0d0d10]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-[#38bdf8]/10 border border-[#38bdf8]/30 flex items-center justify-center text-[#38bdf8]">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight text-[#f4f4f5] flex items-center gap-1.5">
              <span>VÉRTICE</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 bg-[#18181b] border border-[#27272a] text-[#38bdf8] rounded">
                2026
              </span>
            </div>
            <div className="text-[11px] font-mono text-[#71717a]">
              EloGroup Analytics Workbench
            </div>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
        <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-[#71717a]">
          Módulos Analíticos
        </div>

        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full text-left p-2.5 rounded-lg border transition-all duration-150 flex items-start gap-3 group ${
                isActive
                  ? 'bg-[#18181b] border-[#38bdf8]/50 shadow-[0_0_12px_rgba(56,189,248,0.08)]'
                  : 'bg-transparent border-transparent hover:bg-[#18181b]/60 hover:border-[#27272a]'
              }`}
            >
              <div
                className={`mt-0.5 p-1.5 rounded-md transition-colors ${
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
                  <span className="text-[10px] font-mono text-[#71717a]">
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
      </nav>

      {/* Footer Info */}
      <div className="p-3 border-t border-[#27272a] bg-[#0d0d10] text-[11px] font-mono text-[#71717a]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[#a1a1aa]">DuckDB Online</span>
          </div>
          <span>v2.0.0</span>
        </div>
        <div className="mt-1 text-[10px] text-[#52525b]">
          Bootcamp EloGroup • Ano Base 2026
        </div>
      </div>
    </aside>
  );
};
