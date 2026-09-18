export type ViewTab =
  | 'executive'
  | 'marketing'
  | 'customers'
  | 'support'
  | 'inventory'
  | 'audit'
  | 'outliers'
  | 'roadmap'
  | 'copilot';

export type PeriodKey = 'full_history' | 'calendar_2023' | 'last_90d_observed';

export interface PeriodMeta {
  period_key: PeriodKey;
  sales_start: string;
  sales_end: string;
  days: number;
  label: string;
  stock_as_of: null;
  sales_role: 'historical_trend';
}

export interface FilterOptions {
  categories: string[];
  sales_channels: string[];
  marketing_channels: string[];
  support_channels: string[];
  rfm_segments: string[];
  years: string[];
}

export interface ExecutiveOverviewData {
  kpis: {
    bruta?: number;
    liquida?: number;
    margem?: number;
    total_pedidos?: number;
    ticket_medio?: number;
    taxa_devolucao?: number;
  };
  monthly_trend: Array<{
    ano_mes: string;
    receita_liquida: number;
    margem_contribuicao: number;
    total_pedidos: number;
  }>;
  channels: Array<{
    canal: string;
    receita_liquida: number;
    margem_contribuicao: number;
    pedidos: number;
    ticket_medio: number;
  }>;
  categories: Array<{
    categoria: string;
    receita: number;
    margem: number;
    margem_pct: number;
  }>;
}

export interface SalesAnalyticsData {
  decomposition: {
    bruta: number;
    descontos: number;
    liquida: number;
    custo_prod: number;
    custo_frete: number;
    margem: number;
  };
  categories_margin: Array<{
    categoria: string;
    receita: number;
    margem: number;
    margem_pct: number;
  }>;
  returns_impact: Array<{
    motivo_devolucao: string;
    total_devolvido: number;
    valor_devolvido: number;
  }>;
  top_skus: Array<{
    sku_id: string;
    nome_produto: string;
    categoria: string;
    unidades_vendidas: number;
    receita_liquida: number;
    margem_contribuicao: number;
    margem_pct: number;
  }>;
}

export interface MarketingAnalyticsData {
  kpis: {
    invest_total: number;
    rec_total: number;
    roas_global: number;
    cac_medio: number;
    conv_total: number;
    cliques_total: number;
    impressoes_total: number;
  };
  channels: Array<{
    canal: string;
    investimento: number;
    receita_gerada: number;
    conversoes: number;
    cliques: number;
    impressoes: number;
    roas: number;
    cac: number;
    ctr_pct: number;
    taxa_conversao_pct: number;
  }>;
}

export interface InventoryAnalyticsData {
  methodology_banner?: string;
  kpis: {
    total_skus: number;
    skus_ruptura: number;
    skus_criticos: number;
    skus_precisa_reposicao: number;
    taxa_ruptura: number;
    capital_parado: number;
    capital_cadastral_descontinuado?: number;
    lead_time_medio: number;
    descontinuados_valorados?: number;
  };
  categories_rupture: Array<{
    categoria: string;
    total_skus: number;
    skus_ruptura: number;
    skus_estoque_critico: number;
    skus_precisa_reposicao: number;
    taxa_ruptura_pct: number;
    taxa_critico_pct: number;
    lead_time_medio: number;
  }>;
  critical_skus: Array<{
    sku_id: string;
    nome_produto: string;
    categoria: string;
    estoque_disponivel: number;
    ponto_pedido: number;
    deficit_unidades: number;
    lead_time_dias: number;
    custo_unitario: number;
    preco_venda_sugerido: number;
    estoque_fisico?: number;
    estoque_reservado?: number;
    deficit_potencial_unidades?: number;
    lead_time_cadastral_dias?: number;
    margem_potencialmente_exposta?: number;
  }>;
  overstock_skus?: Array<{
    sku_id: string;
    nome_produto: string;
    categoria: string;
    fornecedor_id?: string;
    estoque_disponivel: number;
    demanda_diaria_historica: number;
    cobertura_dias_historica: number;
    unidades_excedentes: number;
    capital_excedente: number;
    custo_unitario_historico: number;
  }>;
  status_breakdown: Array<{
    status_disponibilidade: string;
    total_skus: number;
    capital_total_estoque: number;
    capital_travado_descontinuado: number;
    capital_em_risco_ruptura: number;
  }>;
}

export interface CustomerAnalyticsData {
  kpis: {
    total_clientes: number;
    ltv_medio: number;
    frequencia_media: number;
    renda_media: number;
    idade_media: number;
  };
  segments: Array<{
    segmento: string;
    total_clientes: number;
    ltv_medio: number;
    ticket_medio: number;
    frequencia_media: number;
    recencia_media: number;
  }>;
  top_states: Array<{
    estado: string;
    total_clientes: number;
  }>;
  loyalty: Array<{
    nivel_fidelidade: string;
    total_clientes: number;
  }>;
  pareto_distribution: Array<{
    segmento_rfm: string;
    total_clientes: number;
    pct_base_clientes: number;
    ltv_total: number;
    pct_ltv_total: number;
    ticket_medio_segmento: number;
    pedidos_medios: number;
  }>;
  acquisition_channels: Array<{
    canal_aquisicao: string;
    total_clientes: number;
    ltv_medio: number;
    ticket_medio: number;
    taxa_newsletter_pct: number;
  }>;
}

export interface SupportAnalyticsData {
  kpis: {
    total_tickets: number;
    csat_medio: number;
    primeira_resposta_minutos: number;
    tempo_resposta_min?: number;
    tempo_resposta_mediana_min?: number;
    tempo_resolucao_horas: number;
    custo_operacional_total: number;
  };
  channels: Array<{
    canal_entrada: string;
    total_tickets: number;
    csat_medio: number;
    tempo_resposta_medio: number;
    custo_total: number;
  }>;
  reasons: Array<{
    categoria_problema: string;
    total_tickets: number;
    csat_medio: number;
    tempo_resolucao_medio: number;
  }>;
  csat_distribution: Array<{
    nota_csat: number;
    total_avaliacoes: number;
    pct_avaliacoes: number;
  }>;
  root_causes_ai: Array<{
    categoria_problema: string;
    is_automatizavel: boolean;
    total_tickets: number;
    pct_total: number;
    pct_volume?: number;
    csat_medio: number;
    tickets_detratores?: number;
    tempo_resposta_medio_min?: number;
    tempo_resolucao_medio_h?: number;
    custo_operacional_total: number;
    custo_total_categoria?: number;
    custo_evitavel_automacao: number;
  }>;
}

export interface RelationalAuditData {
  mkt_vs_sales: Array<{
    ano_mes: string;
    investimento_mkt: number;
    receita_declarada_mkt: number;
    receita_liquida_real: number;
    margem_contribuicao_real: number;
    roas_declarado: number;
    roas_real: number;
  }>;
  inventory_vs_sales: Array<{
    categoria: string;
    skus_catalogo: number;
    skus_com_venda: number;
    taxa_cobertura_vendas_pct: number;
    unidades_em_estoque: number;
    unidades_vendidas: number;
  }>;
  sales_vs_support: Array<{
    status_entrega: string;
    total_pedidos: number;
    tickets_suporte: number;
    taxa_atrito_pct: number;
    csat_medio: number;
  }>;
  customers_vs_support: Array<{
    segmento_rfm: string;
    total_clientes: number;
    clientes_com_suporte: number;
    taxa_atrito_vip_pct: number;
    media_tickets_por_cliente: number;
  }>;
  audit_findings: Array<{
    dimension: string;
    erp_coverage: string;
    external_coverage: string;
    impact: string;
    severity: string;
  }>;
}

export interface OutliersData {
  table: string;
  available_tables: string[];
  selected_metric: string;
  available_metrics: string[];
  group_by_dimension: string;
  overall_stats: {
    q1: number;
    median: number;
    q3: number;
    iqr: number;
    lower_bound: number;
    upper_bound: number;
    min: number;
    max: number;
    mean: number;
    total_records: number;
    outliers_count: number;
    outliers_pct: number;
  };
  by_dimension: Array<{
    dimension_value: string;
    q1: number;
    median: number;
    q3: number;
    iqr: number;
    lower_bound: number;
    upper_bound: number;
    min: number;
    max: number;
    mean: number;
    total_records: number;
    outliers_count: number;
    outliers_pct: number;
  }>;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatThread {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
  message_count?: number;
  messages?: ChatMessage[];
}

export interface RoadmapInitiative {
  id: string;
  title: string;
  hypothesis: string;
  type: string;
  horizon: string;
  financial_impact_label: string;
  financial_impact_value: number;
  effort_days: number;
  category: string;
  description: string;
  metrics_to_watch: string[];
}

export interface RoadmapDeliverable {
  agent: string;
  scope: string;
  badge: string;
}

export interface RoadmapTimelinePhase {
  phase: string;
  title: string;
  focus: string;
  squad: string;
  dependencies: string;
  tracking_criteria: string;
  deliverables: RoadmapDeliverable[];
}

export interface RoadmapRiskItem {
  front: string;
  kpi_target: string;
  mitigation_action: string;
}

export interface RoadmapSequencingRationale {
  title: string;
  subtitle: string;
  marketing: {
    title: string;
    highlight_number: string;
    highlight_label: string;
    divergence: string;
    next_step: string;
  };
  crm: {
    title: string;
    highlight_number: string;
    highlight_label: string;
    divergence: string;
    next_step: string;
  };
  c_level_takeaway: string;
}

export interface RoadmapBusinessCase {
  investimento_total_ano_1: number;
  investimento_total_label: string;
  payback_meses: number;
  roi_liquido_ano_1: number;
  beneficio_anual_recorrente: number;
  beneficio_anual_recorrente_label: string;
  resultado_economico_liquido_ano_1: number;
  resultado_economico_liquido_ano_1_label: string;
  receita_liquidacao_central: number;
  receita_liquidacao_central_label: string;
  margem_recuperada_descontos: number;
  margem_recuperada_descontos_label: string;
  economia_operacional_cx: number;
  economia_operacional_cx_label: string;
  breakdown_investimento: Array<{
    item: string;
    valor: number;
    percentual: number;
  }>;
}

export interface RoadmapData {
  initiatives: RoadmapInitiative[];
  timeline: RoadmapTimelinePhase[];
  business_case: RoadmapBusinessCase;
  risk_matrix: RoadmapRiskItem[];
  sequencing_rationale: RoadmapSequencingRationale;
  summary: {
    total_initiatives: number;
    quick_wins_count: number;
    total_potential_value: number;
    inventory_scenario_value: number;
  };
}

