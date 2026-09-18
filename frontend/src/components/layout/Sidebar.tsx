import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Users,
  Headphones,
  Package,
  ShieldCheck,
  SlidersHorizontal,
  Target,
  FileText,
  ChevronRight,
  X,
  Lock,
} from 'lucide-react';
import { ViewTab } from '../../types/analytics';
import { InventoryCopilotIcon } from '../common/InventoryCopilotIcon';
import { MarginRecoveryIcon } from '../common/MarginRecoveryIcon';
import { VerticeLogo } from '../common/VerticeLogo';

interface SidebarProps {
  activeTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  id: ViewTab | 'margin_advisor';
  label: string;
  icon: React.ElementType;
  description?: string;
  disabled?: boolean;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: 'VISÃO OPERACIONAL',
    items: [
      {
        id: 'executive',
        label: 'Visão Executiva & Vendas',
        icon: BarChart3,
      },
      {
        id: 'marketing',
        label: 'Marketing & Mídia (ROAS)',
        icon: TrendingUp,
      },
      {
        id: 'customers',
        label: 'Clientes & RFM',
        icon: Users,
      },
      {
        id: 'support',
        label: 'Atendimento & IA',
        icon: Headphones,
      },
      {
        id: 'inventory',
        label: 'Estoque & Suprimentos',
        icon: Package,
      },
    ],
  },
  {
    title: 'ENTREGÁVEIS',
    items: [
      {
        id: 'roadmap',
        label: 'Plano Estratégico',
        icon: Target,
      },
      {
        id: 'deliverables',
        label: 'Documentos Executivos',
        icon: FileText,
      },
    ],
  },
  {
    title: 'AGENTES & COPILOTOS',
    items: [
      {
        id: 'copilot',
        label: 'Predictive Inventory Advisor',
        icon: InventoryCopilotIcon,
      },
      {
        id: 'margin_advisor',
        label: 'Margin Recovery Advisor',
        icon: MarginRecoveryIcon,
        disabled: true,
      },
    ],
  },
  {
    title: 'GOVERNANÇA & ESTRATÉGIA',
    items: [
      {
        id: 'audit',
        label: 'Auditoria dos Dados',
        icon: ShieldCheck,
      },
      {
        id: 'outliers',
        label: 'Dispersão & Outliers',
        icon: SlidersHorizontal,
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
  const [lockedNotice, setLockedNotice] = useState<string | null>(null);

  const handleItemClick = (item: NavItem) => {
    if (item.disabled) {
      setLockedNotice(
        'Módulo bloqueado • Previsto para a Fase 2 (60 dias)'
      );
      setTimeout(() => setLockedNotice(null), 4500);
      return;
    }
    onTabChange(item.id as ViewTab);
    onClose();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-200"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-72 sm:w-80 lg:w-64 xl:w-72 bg-[#ffffff] dark:bg-[#121024] border-r border-[#e6e5f0] dark:border-[#262046] flex flex-col h-full shrink-0 select-none transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
          }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#0d0b1a] flex items-center justify-between transition-colors">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-[#e8e6ff] dark:bg-[#4200db]/25 border border-[#c4b8ff] dark:border-[#8575ff]/40 flex items-center justify-center text-[#4200db] dark:text-[#8575ff] shadow-sm shadow-[#4200db]/10 dark:shadow-[#4200db]/30">
              <VerticeLogo className="w-4 h-4 text-[#4200db] dark:text-[#8575ff]" size={16} />
            </div>
            <div>
              <div className="text-sm font-bold tracking-tight text-[#131920] dark:text-[#f4f4f5] flex items-center gap-1.5">
                <span>VÉRTICE</span>
              </div>
            </div>
          </div>

          {/* Close button on Mobile */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5] hover:bg-[#f3f2f8] dark:hover:bg-[#181530] lg:hidden transition-colors"
            title="Fechar menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation List by Section */}
        <nav className="flex-1 p-3 space-y-4 overflow-y-auto no-scrollbar">
          {navSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-1">
              {section.title && (
                <div className="px-2 py-1 text-[10px] font-mono font-bold tracking-wider text-[#8e92a0] dark:text-[#71717a] uppercase">
                  {section.title}
                </div>
              )}
              <div className="space-y-1">
                {section.items.map(item => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  const isDisabled = item.disabled;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleItemClick(item)}
                      title={isDisabled ? 'Módulo bloqueado • Previsto para a Fase 2 (60 dias)' : undefined}
                      className={`w-full text-left p-2.5 rounded-lg border transition-all duration-150 flex items-center gap-3 group ${isDisabled
                        ? 'bg-[#ffffff] dark:bg-[#16132b] border-[#e6e5f0] dark:border-[#262046] shadow-xs cursor-pointer opacity-85 hover:opacity-100 hover:border-[#c4b8ff] dark:hover:border-[#8575ff]/40'
                        : isActive
                          ? 'bg-[#e8e6ff]/70 dark:bg-[#181530] border-[#c4b8ff] dark:border-[#8575ff]/50 shadow-sm dark:shadow-[0_0_12px_rgba(133,117,255,0.12)]'
                          : 'bg-transparent border-transparent hover:bg-[#f3f2f8] dark:hover:bg-[#181530]/60 hover:border-[#e6e5f0] dark:hover:border-[#262046]'
                        }`}
                    >
                      <div
                        className={`p-1.5 rounded-md transition-colors shrink-0 ${isDisabled
                          ? 'bg-[#f4f3fa] dark:bg-[#1e1a38] border border-[#e6e5f0] dark:border-[#2b2550] text-[#8e92a0] dark:text-[#a1a1aa] shadow-xs'
                          : isActive
                            ? item.id === 'copilot'
                              ? 'bg-[#ffffff] dark:bg-[#e8e6ff] border border-[#c4b8ff] shadow-sm'
                              : 'bg-[#4200db] text-[#ffffff] dark:bg-[#4200db]/30 dark:text-[#8575ff] dark:border dark:border-[#8575ff]/30 shadow-sm'
                            : 'bg-[#f3f2f8] dark:bg-[#181530] text-[#5e6270] dark:text-[#71717a] group-hover:text-[#131920] dark:group-hover:text-[#a1a1aa]'
                          }`}
                      >
                        <Icon className={item.id === 'copilot' || item.id === 'margin_advisor' ? 'w-5 h-5' : 'w-4 h-4'} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <span
                          className={`text-xs font-semibold truncate block ${isDisabled
                            ? 'text-[#5e6270] dark:text-[#d4d4d8]'
                            : isActive
                              ? 'text-[#4200db] dark:text-[#f4f4f5]'
                              : 'text-[#334155] dark:text-[#d4d4d8] group-hover:text-[#131920] dark:group-hover:text-[#f4f4f5]'
                            }`}
                        >
                          {item.label}
                        </span>
                        {item.description && (
                          <p className="text-[11px] text-[#5e6270] dark:text-[#71717a] truncate mt-0.5 font-sans leading-tight">
                            {item.description}
                          </p>
                        )}
                      </div>

                      {isDisabled ? (
                        <Lock className="w-3.5 h-3.5 text-[#8e92a0] dark:text-[#71717a] shrink-0 self-center" />
                      ) : isActive ? (
                        <ChevronRight className="w-3.5 h-3.5 text-[#4200db] dark:text-[#8575ff] self-center shrink-0" />
                      ) : null}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Locked Feature Toast Notice */}
        {lockedNotice && (
          <div className="p-3 mx-3 mb-2 rounded-xl bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046] text-xs text-[#131920] dark:text-[#f4f4f5] shadow-lg animate-in fade-in slide-in-from-bottom-2 duration-200">
            <div className="flex items-start gap-2.5">
              <Lock className="w-4 h-4 text-[#4200db] dark:text-[#8575ff] shrink-0 mt-0.5" />
              <div className="leading-tight text-[11px] text-[#5e6270] dark:text-[#d4d4d8]">
                {lockedNotice}
              </div>
            </div>
          </div>
        )}

        {/* Footer Info */}
        <div className="p-3 border-t border-[#e6e5f0] dark:border-[#262046] bg-[#f8f7fc] dark:bg-[#0d0b1a] text-[11px] font-mono text-[#5e6270] dark:text-[#71717a] transition-colors">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-[#4200db] dark:text-[#8575ff]">v2.0.0</span>
          </div>
          <div className="mt-1 text-[10px] text-[#8e92a0] dark:text-[#52525b]">
            Bootcamp EloGroup 2026
          </div>
        </div>
      </aside>
    </>
  );
};
