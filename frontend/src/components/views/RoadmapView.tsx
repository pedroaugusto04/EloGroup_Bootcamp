import React, { useState, useEffect } from 'react';
import {
  CalendarRange,
  TrendingUp,
  ShieldAlert,
  SlidersHorizontal,
  ListChecks,
  Package,
  Headphones,
  LayoutGrid,
  Columns3,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  AlertTriangle,
  Info,
} from 'lucide-react';
import { api } from '../../api/client';
import { RoadmapData, RoadmapInitiative } from '../../types/analytics';
import { ScopeBadge } from '../common/ScopeBadge';
import { MetricCard } from '../common/MetricCard';

interface SlideGanttBlock {
  id: string;
  title: string;
  colSpan: number;
  variant: 'solid' | 'light';
  horizonLabel: string;
  agentLabel: string;
  squad: string;
  scope: string;
  criteria: string;
}

interface SlideGanttRow {
  agentId: string;
  agentLabel: string;
  blocks: SlideGanttBlock[];
}

const slideGanttRows: SlideGanttRow[] = [
  {
    agentId: 'agente1',
    agentLabel: 'Agente 1 • Estoque',
    blocks: [
      {
        id: 'agente1-dia30',
        title: 'Piloto operacional',
        colSpan: 1,
        variant: 'solid',
        horizonLabel: 'Dia 30 (Dados + Supply)',
        agentLabel: 'Agente 1 • Estoque',
        squad: 'Equipe de Dados e Operações',
        scope: 'Piloto de liquidação dos 206 SKUs descontinuados com meta de 50% de sell-through e trava para novas compras no ERP.',
        criteria: '≥90% de recomendações acatadas, liquidação sem margem negativa e zero recompra de itens bloqueados.',
      },
      {
        id: 'agente1-dia60_90',
        title: 'Manutenção + calibração',
        colSpan: 2,
        variant: 'solid',
        horizonLabel: 'Dia 60 a 90 (Logística, CX e IA)',
        agentLabel: 'Agente 1 • Estoque',
        squad: 'Equipe de Estoque e Compras',
        scope: 'Ajuste contínuo do ponto de pedido e lead time para os 701 SKUs ativos e rotina automatizada de auditoria de compras.',
        criteria: 'Estoque mantido nos limites de segurança, ausência de rupturas evitáveis e relatórios automáticos em produção.',
      },
    ],
  },
  {
    agentId: 'agente2',
    agentLabel: 'Agente 2 • Desconto',
    blocks: [
      {
        id: 'agente2-dia30',
        title: 'Preparar integração',
        colSpan: 1,
        variant: 'light',
        horizonLabel: 'Dia 30 (Dados + Supply)',
        agentLabel: 'Agente 2 • Desconto',
        squad: 'Equipe Comercial e Dados',
        scope: 'Parametrização de tetos de desconto por SKU a partir de custo histórico (CMV), frete e taxa real de devoluções.',
        criteria: 'Margem real validada por categoria e regras de teto registradas no motor de precificação.',
      },
      {
        id: 'agente2-dia60',
        title: 'Piloto operacional',
        colSpan: 1,
        variant: 'solid',
        horizonLabel: 'Dia 60 (Logística + CX)',
        agentLabel: 'Agente 2 • Desconto',
        squad: 'Equipe Comercial e Growth',
        scope: 'Teste piloto limitando descontos ao teto de 15% com grupo de controle para proteger a margem sem perda de volume.',
        criteria: 'Redução de 50% nos descontos acima de 20%, com impacto negativo no volume de vendas inferior a 5%.',
      },
      {
        id: 'agente2-dia90',
        title: 'Manutenção',
        colSpan: 1,
        variant: 'solid',
        horizonLabel: 'Dia 90 (IA + Atendimento)',
        agentLabel: 'Agente 2 • Desconto',
        squad: 'Equipe Comercial',
        scope: 'Expansão definitiva das regras de teto de desconto de 15% para 100% do catálogo de produtos ativos.',
        criteria: 'Aplicação contínua no checkout e monitoramento de margem bruta preservada mês a mês.',
      },
    ],
  },
  {
    agentId: 'agente3',
    agentLabel: 'Rastreio + Agente 3 • N1',
    blocks: [
      {
        id: 'agente3-dia30',
        title: 'Preparar base N1',
        colSpan: 1,
        variant: 'light',
        horizonLabel: 'Dia 30 (Dados + Supply)',
        agentLabel: 'Rastreio + Agente 3 • N1',
        squad: 'Equipe de CX e Logística',
        scope: 'Montagem da base de dúvidas técnicas de produtos e integração com os eventos de rastreio das transportadoras.',
        criteria: 'Top 50 dúvidas frequentes catalogadas e webhooks das transportadoras ativos no ambiente.',
      },
      {
        id: 'agente3-dia60',
        title: 'Piloto operacional',
        colSpan: 1,
        variant: 'solid',
        horizonLabel: 'Dia 60 (Logística + CX)',
        agentLabel: 'Rastreio + Agente 3 • N1',
        squad: 'Equipe de CX',
        scope: 'Disparo proativo de notificações de entrega por WhatsApp e e-mail e piloto supervisionado de suporte N1.',
        criteria: 'Queda de 30% nos chamados sobre localização de pedidos em 30 dias e zero erros de notificação.',
      },
      {
        id: 'agente3-dia90',
        title: 'Manutenção + calibração',
        colSpan: 1,
        variant: 'solid',
        horizonLabel: 'Dia 90 (IA + Atendimento)',
        agentLabel: 'Rastreio + Agente 3 • N1',
        squad: 'Equipe de CX e IA',
        scope: 'Autoatendimento com IA para dúvidas técnicas e transbordo qualificado para a equipe humana sob demanda.',
        criteria: 'Mais de 60% de chamados resolvidos sem recontato em 7 dias com satisfação do cliente preservada.',
      },
    ],
  },
];

type StrategicTab = 'timeline' | 'business_case' | 'risks' | 'sequencing' | 'initiatives';

export const RoadmapView: React.FC = () => {
  const [data, setData] = useState<RoadmapData | null>(null);
  const [activeTab, setActiveTab] = useState<StrategicTab>('timeline');
  const [timelineLayout, setTimelineLayout] = useState<'gantt' | 'matrix'>('gantt');
  const [selectedHorizon, setSelectedHorizon] = useState<string>('Todos');
  const [selectedBlockId, setSelectedBlockId] = useState<string>('agente1-dia30');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    try {
      setLoading(true);
      const res = await api.getRoadmap();
      setData(res);
    } catch (err) {
      console.error('Erro ao carregar roadmap:', err);
    } finally {
      setLoading(false);
    }
  };

  const initiatives: RoadmapInitiative[] = data?.initiatives || [];
  const filteredInitiatives = initiatives.filter(init => {
    if (selectedHorizon === 'Todos') return true;
    if (selectedHorizon === 'Quick Wins') return init.type.includes('Quick Win');
    return init.horizon === selectedHorizon;
  });

  const bCase = data?.business_case;
  const timeline = data?.timeline || [];
  const riskMatrix = data?.risk_matrix || [];
  const sequencing = data?.sequencing_rationale;

  const allSlideBlocks = slideGanttRows.flatMap(row => row.blocks);
  const selectedBlock = allSlideBlocks.find(b => b.id === selectedBlockId) || allSlideBlocks[0];

  // Tabs metadata
  const tabs = [
    {
      id: 'timeline' as StrategicTab,
      label: 'Execução 30 / 60 / 90',
      slideTag: 'Slide 12',
      icon: CalendarRange,
      description: 'Cronograma e frentes',
    },
    {
      id: 'business_case' as StrategicTab,
      label: 'Business Case e ROI',
      slideTag: 'Slide 11.1',
      icon: TrendingUp,
      description: 'Investimento e retorno',
    },
    {
      id: 'risks' as StrategicTab,
      label: 'Governança e Riscos',
      slideTag: 'Slide 13',
      icon: ShieldAlert,
      description: 'Metas e contingência',
    },
    {
      id: 'sequencing' as StrategicTab,
      label: 'Sequenciamento',
      slideTag: 'Slide A4',
      icon: SlidersHorizontal,
      description: 'Marketing e CRM',
    },
    {
      id: 'initiatives' as StrategicTab,
      label: 'Catálogo de Ações',
      slideTag: `${initiatives.length} ações`,
      icon: ListChecks,
      description: 'Ações detalhadas por prazo',
    },
  ];

  // Agentes do Slide 12 para montagem da matriz de cruzamento
  const agentRows = [
    {
      id: 'stock',
      title: 'Agente 1: Estoque Preditivo',
      department: 'Estoque e Compras',
      icon: Package,
      accent: 'text-[#4200db] dark:text-[#8575ff] bg-[#f4f2ff] dark:bg-[#8575ff]/10 border-[#e6e5f0] dark:border-[#262046]',
      matchAgent: (agentName: string) => agentName.includes('1') || agentName.includes('Estoque') || agentName.includes('Stock'),
    },
    {
      id: 'margin',
      title: 'Agente 2: Recuperação de Margem',
      department: 'Preço e Descontos',
      icon: TrendingUp,
      accent: 'text-[#4200db] dark:text-[#8575ff] bg-[#f4f2ff] dark:bg-[#8575ff]/10 border-[#e6e5f0] dark:border-[#262046]',
      matchAgent: (agentName: string) => agentName.includes('2') || agentName.includes('Margem') || agentName.includes('Margin'),
    },
    {
      id: 'support',
      title: 'Agente 3: Rastreio e Suporte',
      department: 'Logística e Atendimento',
      icon: Headphones,
      accent: 'text-[#4200db] dark:text-[#8575ff] bg-[#f4f2ff] dark:bg-[#8575ff]/10 border-[#e6e5f0] dark:border-[#262046]',
      matchAgent: (agentName: string) =>
        agentName.includes('3') || agentName.includes('Atendimento') || agentName.includes('Rastreio') || agentName.includes('Suporte'),
    },
  ];

  const getBadgeStyle = (badgeText: string) => {
    const text = badgeText.toLowerCase();
    if (text.includes('piloto')) {
      return 'bg-[#f4f2ff] dark:bg-[#8575ff]/15 text-[#4200db] dark:text-[#8575ff] border-[#4200db]/30 dark:border-[#8575ff]/40';
    }
    if (text.includes('prepar') || text.includes('integra')) {
      return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
    if (text.includes('manuten') || text.includes('calibra')) {
      return 'bg-slate-50 dark:bg-slate-900/60 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-slate-800';
    }
    return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700';
  };

  if (loading) {
    return (
      <div className="space-y-6 view-enter animate-pulse">
        <div className="h-10 bg-[#e6e5f0]/60 dark:bg-[#262046]/60 rounded-xl w-full" />
        <div className="h-14 bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] rounded-2xl w-full" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046]"
            />
          ))}
        </div>
        <div className="h-96 rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046]" />
      </div>
    );
  }

  return (
    <div className="space-y-6 view-enter">
      {/* Scope Badge */}
      <ScopeBadge
        tables={['vendas', 'estoque', 'atendimento', 'marketing', 'clientes']}
        scope="Plano Estratégico: Business Case e Governança"
        devSection="Alinhado aos Slides Executivos (Slides 06 a 13 e Slides Auxiliares A1-A4)"
      />

      {/* Main Tab Navigation Bar */}
      <div className="p-1.5 sm:p-2 rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
        <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 min-w-[170px] sm:min-w-[190px] p-2.5 sm:p-3 rounded-xl border text-left transition-all duration-200 ${isActive
                  ? 'bg-[#f4f2ff] dark:bg-[#8575ff]/15 border-[#4200db]/40 dark:border-[#8575ff]/50 shadow-sm'
                  : 'bg-[#faf9fe] dark:bg-[#181530]/60 border-transparent hover:border-[#e6e5f0] dark:hover:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                  }`}
              >
                <div className="flex items-center justify-between gap-1 mb-1">
                  <div className="flex items-center gap-2">
                    <Icon
                      className={`w-4 h-4 ${isActive ? 'text-[#4200db] dark:text-[#8575ff]' : 'text-[#5e6270] dark:text-[#a1a1aa]'
                        }`}
                    />
                    <span
                      className={`text-xs sm:text-sm font-bold ${isActive ? 'text-[#131920] dark:text-[#f4f4f5]' : 'text-[#40434f] dark:text-[#d4d4d8]'
                        }`}
                    >
                      {tab.label}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] sm:text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border whitespace-nowrap ${isActive
                      ? 'bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] border-[#4200db]/30 dark:border-[#8575ff]/40'
                      : 'bg-[#e6e5f0]/50 dark:bg-[#262046]/50 text-[#5e6270] dark:text-[#71717a] border-transparent'
                      }`}
                  >
                    {tab.slideTag}
                  </span>
                </div>
                <p className="text-[11px] text-[#5e6270] dark:text-[#71717a] line-clamp-1">
                  {tab.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: EXECUÇÃO 30 / 60 / 90 DIAS (SLIDE 12)
          ========================================================================= */}
      {activeTab === 'timeline' && (
        <div className="space-y-6">
          {/* Header com Toggle de Visualização (Slide 12 Matrix vs Cards) */}
          <div className="rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] p-5 sm:p-6 shadow-sm space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#e6e5f0] dark:border-[#262046] pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] font-bold">
                    Slide 12: Execução
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5]">
                    Cronograma de execução (30, 60 e 90 dias)
                  </h3>
                </div>
                <p className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                  Sequência de entregas por frente de trabalho e equipe responsável no período de 90 dias.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] font-medium mr-1 hidden md:inline">
                  Visualização:
                </span>
                <div className="inline-flex p-1 rounded-xl bg-[#faf9fe] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046]">
                  <button
                    onClick={() => setTimelineLayout('gantt')}
                    className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-lg font-semibold transition-all ${timelineLayout === 'gantt'
                      ? 'bg-[#ffffff] dark:bg-[#131126] text-[#4200db] dark:text-[#8575ff] shadow-sm border border-[#e6e5f0] dark:border-[#262046]'
                      : 'text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                      }`}
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                    <span>Gantt Slide 12</span>
                  </button>
                  <button
                    onClick={() => setTimelineLayout('matrix')}
                    className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-lg font-semibold transition-all ${timelineLayout === 'matrix'
                      ? 'bg-[#ffffff] dark:bg-[#131126] text-[#4200db] dark:text-[#8575ff] shadow-sm border border-[#e6e5f0] dark:border-[#262046]'
                      : 'text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                      }`}
                  >
                    <LayoutGrid className="w-3.5 h-3.5" />
                    <span>Matriz de Governança</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Visualização 1: SLIDE 12 GANTT EXECUTIVO (CRONOGRAMA 30 / 60 / 90) */}
            {timelineLayout === 'gantt' && (
              <div className="space-y-6">
                {/* Slide Frame */}
                <div className="rounded-2xl border border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#110d21] p-6 sm:p-8 shadow-sm space-y-6">
                  {/* Slide Top Bar */}
                  <div className="flex items-center justify-between border-b border-[#f1f0f7] dark:border-[#1e1938] pb-4">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-1 bg-[#a21caf] dark:bg-[#c084fc] rounded-full inline-block" />
                      <span className="text-xs sm:text-sm font-bold tracking-wider text-[#581c87] dark:text-[#d8b4fe]">
                        12 / ROADMAP
                      </span>
                    </div>
                    <span className="text-xs sm:text-sm font-black tracking-widest text-[#131920] dark:text-[#f4f4f5]">
                      VÉRTICE
                    </span>
                  </div>

                  {/* Slide Title */}
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-[#1a0526] dark:text-[#faf5ff] tracking-tight">
                    RoadMap
                  </h2>

                  {/* Gantt Grid Container */}
                  <div className="overflow-x-auto">
                    <div className="min-w-[680px] space-y-4">
                      {/* Columns Header */}
                      <div className="flex items-end gap-3 pb-3 border-b border-[#f1f0f7] dark:border-[#1e1938]">
                        <div className="w-52 sm:w-64 shrink-0" />
                        <div className="grid grid-cols-3 gap-3 sm:gap-4 flex-1">
                          <div className="text-left">
                            <span className="text-lg sm:text-2xl font-black text-[#2e0854] dark:text-[#e9d5ff] block leading-tight">
                              DIA 30
                            </span>
                            <span className="text-xs sm:text-sm text-[#5e6270] dark:text-[#a1a1aa] font-medium">
                              Dados + Supply
                            </span>
                          </div>
                          <div className="text-left">
                            <span className="text-lg sm:text-2xl font-black text-[#2e0854] dark:text-[#e9d5ff] block leading-tight">
                              DIA 60
                            </span>
                            <span className="text-xs sm:text-sm text-[#5e6270] dark:text-[#a1a1aa] font-medium">
                              Logística + CX
                            </span>
                          </div>
                          <div className="text-left">
                            <span className="text-lg sm:text-2xl font-black text-[#2e0854] dark:text-[#e9d5ff] block leading-tight">
                              DIA 90
                            </span>
                            <span className="text-xs sm:text-sm text-[#5e6270] dark:text-[#a1a1aa] font-medium">
                              IA + Atendimento
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Rows */}
                      {slideGanttRows.map(row => (
                        <div key={row.agentId} className="flex items-center gap-3">
                          {/* Row Label */}
                          <div className="w-52 sm:w-64 shrink-0 font-bold text-sm sm:text-base text-[#131920] dark:text-[#f4f4f5] pr-2">
                            {row.agentLabel}
                          </div>

                          {/* Row Bars */}
                          <div className="grid grid-cols-3 gap-3 sm:gap-4 flex-1">
                            {row.blocks.map(block => {
                              const isSelected = selectedBlockId === block.id;
                              const isSolid = block.variant === 'solid';
                              const colSpanClass = block.colSpan === 2 ? 'col-span-2' : 'col-span-1';

                              return (
                                <button
                                  key={block.id}
                                  type="button"
                                  onClick={() => setSelectedBlockId(block.id)}
                                  className={`${colSpanClass} h-12 sm:h-14 px-4 sm:px-5 rounded-md sm:rounded-lg font-bold text-xs sm:text-sm flex items-center justify-start text-left transition-all duration-150 cursor-pointer ${isSolid
                                    ? 'bg-[#38034e] hover:bg-[#4d0768] dark:bg-[#4d0768] dark:hover:bg-[#600982] text-white shadow-xs'
                                    : 'bg-[#f6effb] hover:bg-[#ede0fc] dark:bg-[#2b123d] dark:hover:bg-[#391952] text-[#38034e] dark:text-[#f3e8ff] shadow-xs'
                                    } ${isSelected
                                      ? 'ring-2 ring-offset-2 ring-[#a21caf] dark:ring-offset-[#110d21] shadow-md scale-[1.01]'
                                      : 'hover:scale-[1.005]'
                                    }`}
                                >
                                  <span className="truncate">{block.title}</span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ))}

                      {/* Slide Footer */}
                      <div className="flex justify-end pt-4">
                        <span className="text-xs font-bold font-mono text-[#5e6270] dark:text-[#71717a]">
                          12
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Detail Inspection Card below Slide */}
                {selectedBlock && (
                  <div className="rounded-xl border border-[#4200db]/30 dark:border-[#8575ff]/40 bg-[#faf9fe] dark:bg-[#181432] p-5 shadow-sm space-y-3 transition-all">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e6e5f0] dark:border-[#262046] pb-3">
                      <div className="flex items-center gap-2.5">
                        <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded bg-[#4200db]/10 dark:bg-[#8575ff]/20 text-[#4200db] dark:text-[#8575ff]">
                          {selectedBlock.horizonLabel}
                        </span>
                        <h4 className="text-sm sm:text-base font-bold text-[#131920] dark:text-[#f4f4f5]">
                          {selectedBlock.agentLabel}:{' '}
                          <span className="font-semibold text-[#4200db] dark:text-[#8575ff]">
                            {selectedBlock.title}
                          </span>
                        </h4>
                      </div>
                      <span className="text-[11px] font-mono text-[#5e6270] dark:text-[#a1a1aa]">
                        Clique em outra barra para inspecionar
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                      <div className="p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[#5e6270] dark:text-[#a1a1aa] font-bold block">
                          Escopo Operacional
                        </span>
                        <p className="text-xs text-[#131920] dark:text-[#e4e4e7] leading-relaxed">
                          {selectedBlock.scope}
                        </p>
                      </div>
                      <div className="p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[#5e6270] dark:text-[#a1a1aa] font-bold block">
                          Equipe Responsável
                        </span>
                        <p className="text-xs text-[#131920] dark:text-[#e4e4e7] leading-relaxed font-semibold">
                          {selectedBlock.squad}
                        </p>
                      </div>
                      <div className="p-3.5 rounded-lg bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[#5e6270] dark:text-[#a1a1aa] font-bold block">
                          Critério de Sucesso e Gate
                        </span>
                        <p className="text-xs text-[#131920] dark:text-[#e4e4e7] leading-relaxed">
                          {selectedBlock.criteria}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Gates & Milestones no Rodapé do Gantt */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1 shadow-xs">
                    <span className="font-mono text-[11px] font-bold text-[#4200db] dark:text-[#8575ff] block">
                      GATE 1 • DIA 30
                    </span>
                    <p className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa]">
                      Validação do sell-through de 50%, liquidação sem margem negativa e trava ativa no ERP contra recompras indevidas.
                    </p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1 shadow-xs">
                    <span className="font-mono text-[11px] font-bold text-[#4200db] dark:text-[#8575ff] block">
                      GATE 2 • DIA 60
                    </span>
                    <p className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa]">
                      Avaliação do teste A/B com teto de 15% de desconto e queda imediata de 30% nos chamados sobre status de entrega.
                    </p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] space-y-1 shadow-xs">
                    <span className="font-mono text-[11px] font-bold text-[#4200db] dark:text-[#8575ff] block">
                      GATE 3 • DIA 90
                    </span>
                    <p className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa]">
                      Escala para 100% do catálogo ativo, autoatendimento com IA homologado e rotinas contínuas de governança.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Visualização 2: MATRIZ EXECUTIVA DO SLIDE 12 */}
            {timelineLayout === 'matrix' && (
              <div className="space-y-4">
                {/* Timeline Progress Ribbon para a Matriz */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {timeline.map((phase, idx) => {
                    return (
                      <div
                        key={phase.phase}
                        className="p-3.5 rounded-xl border border-[#e6e5f0] dark:border-[#262046] bg-[#faf9fe] dark:bg-[#15122b] flex items-start gap-3"
                      >
                        <div className="flex flex-col items-center">
                          <span className="w-2.5 h-2.5 rounded-full bg-[#4200db] dark:bg-[#8575ff] mt-1.5" />
                          {idx < 2 && <div className="w-0.5 h-full bg-slate-300 dark:bg-slate-700 my-1 hidden md:block" />}
                        </div>
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded border bg-[#f4f2ff] dark:bg-[#8575ff]/15 text-[#4200db] dark:text-[#8575ff] border-[#4200db]/30 dark:border-[#8575ff]/40">
                              {phase.phase.toUpperCase()}
                            </span>
                            <span className="text-xs font-bold text-[#131920] dark:text-[#f4f4f5]">
                              {phase.title}
                            </span>
                          </div>
                          <p className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] leading-tight line-clamp-2">
                            {phase.focus}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="overflow-x-auto rounded-xl border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
                <table className="w-full text-left border-collapse min-w-[760px]">
                  <thead>
                    <tr className="bg-[#f4f3fa] dark:bg-[#110f22] border-b border-[#e6e5f0] dark:border-[#262046]">
                      <th className="p-3.5 text-xs font-bold font-mono text-[#5e6270] dark:text-[#a1a1aa] uppercase tracking-wider w-[240px]">
                        Frente e Agente
                      </th>
                      {timeline.map((phase) => (
                        <th
                          key={phase.phase}
                          className="p-3.5 text-xs font-bold text-[#131920] dark:text-[#f4f4f5] border-l border-[#e6e5f0] dark:border-[#262046]"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-mono text-[11px] text-[#4200db] dark:text-[#8575ff] font-bold">
                              {phase.phase.toUpperCase()}
                            </span>
                            <span className="text-xs font-semibold text-[#5e6270] dark:text-[#a1a1aa]">
                              {phase.title}
                            </span>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#e6e5f0] dark:divide-[#262046]">
                    {agentRows.map(row => {
                      const Icon = row.icon;
                      return (
                        <tr
                          key={row.id}
                          className="bg-[#ffffff] dark:bg-[#131126] hover:bg-[#faf9fe] dark:hover:bg-[#15122b] transition-colors"
                        >
                          {/* Coluna da Frente / Agente */}
                          <td className="p-3.5 align-top bg-[#faf9fe]/60 dark:bg-[#15122b]/60">
                            <div className="flex items-start gap-2.5">
                              <div className={`p-1.5 rounded-lg border ${row.accent} shrink-0 mt-0.5`}>
                                <Icon className="w-3.5 h-3.5" />
                              </div>
                              <div>
                                <span className="text-xs font-bold text-[#131920] dark:text-[#f4f4f5] block leading-snug">
                                  {row.title}
                                </span>
                                <span className="text-[10px] text-[#5e6270] dark:text-[#71717a] font-mono">
                                  {row.department}
                                </span>
                              </div>
                            </div>
                          </td>

                          {/* Células da Matriz para cada Fase (Dia 30, 60, 90) */}
                          {timeline.map(phase => {
                            const deliverable = phase.deliverables.find(d => row.matchAgent(d.agent));
                            if (!deliverable) {
                              return (
                                <td
                                  key={phase.phase}
                                  className="p-3.5 align-top border-l border-[#e6e5f0] dark:border-[#262046] text-xs text-[#5e6270] dark:text-[#71717a]"
                                >
                                  -
                                </td>
                              );
                            }

                            return (
                              <td
                                key={phase.phase}
                                className="p-3.5 align-top border-l border-[#e6e5f0] dark:border-[#262046] space-y-2"
                              >
                                <span
                                  className={`inline-block text-[10px] font-mono font-bold px-2 py-0.5 rounded-md border ${getBadgeStyle(
                                    deliverable.badge,
                                  )}`}
                                >
                                  {deliverable.badge}
                                </span>
                                <p className="text-[11px] sm:text-xs text-[#40434f] dark:text-[#d4d4d8] leading-relaxed">
                                  {deliverable.scope}
                                </p>
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                  {/* Rodapé da Matriz com Equipe e Critério */}
                  <tfoot>
                    <tr className="bg-[#f4f3fa] dark:bg-[#110f22] border-t border-[#e6e5f0] dark:border-[#262046] text-[11px]">
                      <td className="p-3.5 font-mono text-[#5e6270] dark:text-[#a1a1aa] font-bold">
                        Governança da fase
                      </td>
                      {timeline.map(phase => (
                        <td
                          key={phase.phase}
                          className="p-3.5 border-l border-[#e6e5f0] dark:border-[#262046] space-y-1"
                        >
                          <div className="text-[#5e6270] dark:text-[#a1a1aa]">
                            <strong className="text-[#131920] dark:text-[#f4f4f5]">Equipe:</strong> {phase.squad}
                          </div>
                          <div className="text-[#5e6270] dark:text-[#a1a1aa]">
                            <strong className="text-[#131920] dark:text-[#f4f4f5]">Critério:</strong>{' '}
                            {phase.tracking_criteria}
                          </div>
                        </td>
                      ))}
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: BUSINESS CASE & RETORNO ECONÔMICO (SLIDE 11.1)
          ========================================================================= */}
      {activeTab === 'business_case' && (
        <div className="space-y-6">
          {/* Top Financial Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
            <MetricCard
              label="Investimento Total (Ano 1)"
              value={bCase ? bCase.investimento_total_label : 'R$ 350 mil'}
              subtitle="Equipe, nuvem e mensagens"
            />
            <MetricCard
              label="Payback Estimado"
              value={bCase ? `${bCase.payback_meses.toFixed(1).replace('.', ',')} meses` : '2,3 meses'}
              subtitle="Recuperação no 1º trimestre"
              highlight
            />
            <MetricCard
              label="ROI Líquido (Ano 1)"
              value={bCase ? `${bCase.roi_liquido_ano_1.toFixed(1).replace('.', ',')}x` : '4,3x'}
              subtitle="Retorno sobre o capital"
              highlight
            />
            <MetricCard
              label="Benefício Anual Recorrente"
              value={bCase ? bCase.beneficio_anual_recorrente_label : 'R$ 1,86M/ano'}
              subtitle="Descontos e suporte N1"
            />
            <MetricCard
              label="Liquidação Descontinuados"
              value={bCase ? bCase.receita_liquidacao_central_label : 'R$ 4,14M'}
              subtitle="50% de venda (caixa imediato)"
            />
          </div>

          {/* Estrutura em Três Colunas do Slide 11.1 */}
          <div className="rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] p-5 sm:p-6 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e6e5f0] dark:border-[#262046] pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] font-bold">
                    Slide 11.1: Business Case
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5]">
                    Business case e retorno econômico
                  </h3>
                </div>
                <p className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                  O projeto se autofinancia no primeiro trimestre com a venda de itens parados e o controle de descontos.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Coluna 1: Onde Capturamos Valor */}
              <div className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 flex flex-col justify-between">
                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#4200db] dark:text-[#8575ff] mb-2">
                    01. Onde capturamos valor
                  </div>
                  <ul className="space-y-3 text-xs text-[#40434f] dark:text-[#d4d4d8]">
                    <li className="p-2.5 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <strong className="text-[#131920] dark:text-[#f4f4f5] block">
                        Liquidação de descontinuados:
                      </strong>
                      <span>
                        +R$ 4,14M em receita líquida no cenário central (50% de venda e R$ 969k de margem de contribuição).
                      </span>
                    </li>
                    <li className="p-2.5 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <strong className="text-[#131920] dark:text-[#f4f4f5] block">
                        Teto de descontos (15%):
                      </strong>
                      <span>
                        +R$ 1,80M ao ano em margem recuperada sem perda observada no volume vendido.
                      </span>
                    </li>
                    <li className="p-2.5 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <strong className="text-[#131920] dark:text-[#f4f4f5] block">
                        Automação de suporte e rastreio:
                      </strong>
                      <span>
                        +R$ 55,7 mil ao ano em chamados evitados (80% em rastreio e 50% em dúvidas técnicas).
                      </span>
                    </li>
                  </ul>
                </div>
                <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] text-[11px] text-[#5e6270] dark:text-[#a1a1aa] italic">
                  * A receita de liquidação é reforço imediato de caixa e não se repete nos anos seguintes.
                </div>
              </div>

              {/* Coluna 2: Investimento do Projeto */}
              <div className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 flex flex-col justify-between">
                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#4200db] dark:text-[#8575ff] mb-2">
                    02. Investimento previsto (Ano 1)
                  </div>
                  <div className="text-2xl font-bold font-mono text-[#131920] dark:text-[#f4f4f5] mb-3">
                    R$ 350.000,00
                  </div>

                  {/* Visual Bar Breakdown */}
                  <div className="space-y-3">
                    {bCase?.breakdown_investimento?.map((item, idx) => {
                      const colors = [
                        'bg-[#4200db] dark:bg-[#8575ff]',
                        'bg-[#4200db]/80 dark:bg-[#8575ff]/80',
                        'bg-[#4200db]/60 dark:bg-[#8575ff]/60',
                      ];
                      return (
                        <div
                          key={idx}
                          className="p-2.5 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046] space-y-1.5"
                        >
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-[#40434f] dark:text-[#d4d4d8] font-medium">{item.item}</span>
                            <span className="font-mono font-bold text-[#131920] dark:text-[#f4f4f5]">
                              R$ {(item.valor / 1000).toFixed(0)}k ({item.percentual.toFixed(0)}%)
                            </span>
                          </div>
                          <div className="w-full bg-[#e6e5f0] dark:bg-[#262046] rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-1.5 rounded-full ${colors[idx % colors.length]}`}
                              style={{ width: `${item.percentual}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] text-[11px] text-[#5e6270] dark:text-[#a1a1aa]">
                  Estrutura enxuta com foco em DuckDB in-memory, automações e regras de segurança.
                </div>
              </div>

              {/* Coluna 3: Métricas de Retorno */}
              <div className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 flex flex-col justify-between">
                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#4200db] dark:text-[#8575ff] mb-2">
                    03. Indicadores de retorno
                  </div>
                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <span className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] block font-semibold">
                        Payback estimado:
                      </span>
                      <span className="text-2xl font-bold font-mono text-[#131920] dark:text-[#f4f4f5]">
                        2,3 meses
                      </span>
                      <span className="text-[10px] text-[#5e6270] dark:text-[#71717a] block mt-0.5 font-mono">
                        (Cenário conservador: 4,5 meses)
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <span className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] block font-semibold">
                        ROI líquido no Ano 1:
                      </span>
                      <span className="text-2xl font-bold font-mono text-[#4200db] dark:text-[#8575ff]">
                        4,3x o capital investido
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046]">
                      <span className="text-[11px] text-[#5e6270] dark:text-[#a1a1aa] block font-semibold">
                        Resultado financeiro líquido (Ano 1):
                      </span>
                      <span className="text-xl font-bold font-mono text-[#131920] dark:text-[#f4f4f5]">
                        +R$ 1,51M
                      </span>
                    </div>
                  </div>
                </div>
                <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] text-[11px] text-[#5e6270] dark:text-[#a1a1aa]">
                  Mesmo no cenário conservador (25% de liquidação e 25% de desconto capturado), o payback é de 4,5 meses.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: GOVERNANÇA & RISCOS (SLIDE 13)
          ========================================================================= */}
      {activeTab === 'risks' && (
        <div className="space-y-6">
          <div className="rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] p-5 sm:p-6 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e6e5f0] dark:border-[#262046] pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] font-bold">
                    Slide 13: Riscos e Governança
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5]">
                    Riscos, metas e planos de contingência
                  </h3>
                </div>
                <p className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                  Ajuste de parâmetros e regras de segurança antes de expandir para o restante da operação.
                </p>
              </div>
              <span className="text-xs font-mono px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-semibold self-start sm:self-center">
                Regras de segurança
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {riskMatrix.map((item, rIdx) => (
                <div
                  key={rIdx}
                  className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 shadow-sm hover:border-[#4200db]/30 transition-all"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs sm:text-sm font-bold text-[#131920] dark:text-[#f4f4f5]">
                      {item.front}
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-semibold">
                      Gatilho e ação
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046] text-xs">
                    <span className="text-[#5e6270] dark:text-[#a1a1aa] block font-semibold mb-0.5">
                      Meta de controle:
                    </span>
                    <span className="font-mono text-[#4200db] dark:text-[#8575ff] font-bold">
                      {item.kpi_target}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#ffffff] dark:bg-[#1a1636] border border-[#e6e5f0] dark:border-[#262046] text-xs">
                    <span className="text-rose-600 dark:text-rose-400 block font-semibold mb-0.5">
                      Plano de contingência:
                    </span>
                    <span className="text-[#40434f] dark:text-[#d4d4d8]">
                      {item.mitigation_action}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-xl bg-[#f4f3fa] dark:bg-[#110f22] border border-[#e6e5f0] dark:border-[#262046] flex items-start gap-3 text-xs text-[#5e6270] dark:text-[#a1a1aa]">
              <Info className="w-4 h-4 text-[#4200db] dark:text-[#8575ff] shrink-0 mt-0.5" />
              <p>
                <strong>Aprovações:</strong> Alterações em compras e preços passam por validação antes de entrarem no ar.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: RACIONAL DE SEQUENCIAMENTO (SLIDE A4)
          ========================================================================= */}
      {activeTab === 'sequencing' && sequencing && (
        <div className="space-y-6">
          <div className="rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] p-5 sm:p-6 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e6e5f0] dark:border-[#262046] pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-[#4200db]/10 text-[#4200db] dark:bg-[#8575ff]/20 dark:text-[#8575ff] font-bold">
                    Slide A4: Sequenciamento
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-[#131920] dark:text-[#f4f4f5]">
                    {sequencing.title}
                  </h3>
                </div>
                <p className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                  {sequencing.subtitle}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Marketing */}
              <div className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 flex flex-col justify-between shadow-sm">
                <div className="space-y-2">
                  <span className="text-xs font-bold text-[#131920] dark:text-[#f4f4f5]">
                    {sequencing.marketing.title}
                  </span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-[#4200db] dark:text-[#8575ff]">
                      {sequencing.marketing.highlight_number}
                    </span>
                    <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                      {sequencing.marketing.highlight_label}
                    </span>
                  </div>
                  <p className="text-xs text-[#40434f] dark:text-[#d4d4d8] leading-relaxed">
                    {sequencing.marketing.divergence}
                  </p>
                </div>
                <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] text-xs">
                  <strong className="text-[#4200db] dark:text-[#8575ff] block mb-0.5">
                    Próximo passo (60 dias):
                  </strong>
                  <span className="text-[#5e6270] dark:text-[#a1a1aa]">
                    {sequencing.marketing.next_step}
                  </span>
                </div>
              </div>

              {/* CRM */}
              <div className="p-4 sm:p-5 rounded-xl bg-[#faf9fe] dark:bg-[#15122b] border border-[#e6e5f0] dark:border-[#262046] space-y-3 flex flex-col justify-between shadow-sm">
                <div className="space-y-2">
                  <span className="text-xs font-bold text-[#131920] dark:text-[#f4f4f5]">
                    {sequencing.crm.title}
                  </span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-[#4200db] dark:text-[#8575ff]">
                      {sequencing.crm.highlight_number}
                    </span>
                    <span className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                      {sequencing.crm.highlight_label}
                    </span>
                  </div>
                  <p className="text-xs text-[#40434f] dark:text-[#d4d4d8] leading-relaxed">
                    {sequencing.crm.divergence}
                  </p>
                </div>
                <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] text-xs">
                  <strong className="text-[#4200db] dark:text-[#8575ff] block mb-0.5">
                    Próximo passo (90 dias):
                  </strong>
                  <span className="text-[#5e6270] dark:text-[#a1a1aa]">
                    {sequencing.crm.next_step}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#faf9fe] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <span className="font-bold text-[#4200db] dark:text-[#8575ff] whitespace-nowrap">
                Resposta à banca:
              </span>
              <span className="text-[#131920] dark:text-[#f4f4f5] font-medium">
                {sequencing.c_level_takeaway}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: CATÁLOGO DE INICIATIVAS DETALHADAS
          ========================================================================= */}
      {activeTab === 'initiatives' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] shadow-sm">
            <div>
              <h3 className="text-base font-bold text-[#131920] dark:text-[#f4f4f5]">
                Catálogo de iniciativas ({initiatives.length})
              </h3>
              <p className="text-xs text-[#5e6270] dark:text-[#a1a1aa]">
                Filtre por prazo de execução para ver o impacto financeiro e as métricas de acompanhamento.
              </p>
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2 p-1 rounded-xl bg-[#faf9fe] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] overflow-x-auto no-scrollbar">
              {['Todos', 'Quick Wins', '30 Dias', '60 Dias', '90 Dias'].map(horizon => {
                const active = selectedHorizon === horizon;
                return (
                  <button
                    key={horizon}
                    onClick={() => setSelectedHorizon(horizon)}
                    className={`text-xs px-3 py-1.5 rounded-lg border whitespace-nowrap transition-all ${active
                      ? 'bg-[#f4f2ff] dark:bg-[#8575ff]/15 border-[#4200db]/40 dark:border-[#8575ff]/50 text-[#4200db] dark:text-[#8575ff] font-semibold shadow-sm'
                      : 'bg-transparent border-transparent text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5]'
                      }`}
                  >
                    {horizon}
                  </button>
                );
              })}
            </div>
          </div>

          {filteredInitiatives.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] text-xs text-[#5e6270] dark:text-[#a1a1aa]">
              Nenhuma iniciativa encontrada para o filtro selecionado.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredInitiatives.map(init => (
                <div
                  key={init.id}
                  className="p-5 rounded-xl bg-[#ffffff] dark:bg-[#131126] border border-[#e6e5f0] dark:border-[#262046] hover:border-[#4200db]/40 dark:hover:border-[#8575ff]/50 transition-all flex flex-col justify-between space-y-4 shadow-sm"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-md bg-[#f8f7fc] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-[#4200db] dark:text-[#8575ff]">
                        {init.horizon}
                      </span>
                      <span
                        className={`text-xs font-mono px-2.5 py-0.5 rounded-md font-semibold ${init.type.includes('Quick Win')
                          ? 'bg-[#f4f2ff] dark:bg-[#8575ff]/15 text-[#4200db] dark:text-[#8575ff] border border-[#4200db]/30 dark:border-[#8575ff]/40'
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

                    {init.metrics_to_watch && init.metrics_to_watch.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {init.metrics_to_watch.map((m, mIdx) => (
                          <span
                            key={mIdx}
                            className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#f4f3fa] dark:bg-[#1a1636] text-[#5e6270] dark:text-[#a1a1aa] border border-[#e6e5f0] dark:border-[#262046]"
                          >
                            {m}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-[#e6e5f0] dark:border-[#262046] flex items-center justify-between text-xs">
                    <div>
                      <span className="text-[10px] sm:text-[11px] text-[#5e6270] dark:text-[#71717a] block font-semibold">
                        Impacto estimado:
                      </span>
                      <span className="font-mono font-bold text-[#4200db] dark:text-[#8575ff] text-xs sm:text-sm">
                        {init.financial_impact_label}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] sm:text-[11px] text-[#5e6270] dark:text-[#71717a] block font-semibold">
                        Prazo estimado:
                      </span>
                      <span className="font-mono text-[#131920] dark:text-[#f4f4f5] text-xs sm:text-sm font-bold">
                        {init.effort_days} dias
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
