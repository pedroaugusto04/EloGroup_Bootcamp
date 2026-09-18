// Typed API Client for FastAPI backend

import {
  ExecutiveOverviewData,
  SalesAnalyticsData,
  MarketingAnalyticsData,
  InventoryAnalyticsData,
  CustomerAnalyticsData,
  SupportAnalyticsData,
  RelationalAuditData,
  OutliersData,
  FilterOptions,
  ChatThread,
  RoadmapInitiative,
  RoadmapData,
  PeriodKey,
  PeriodMeta,
  DeliverableMeta,
  DeliverableDetail,
} from '../types/analytics';

const BASE_URL = 'api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API Error ${res.status}: ${errorBody || res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Global Filters
  getFilters: () => fetchJson<FilterOptions>(`${BASE_URL}/analytics/filters`),

  // Executive Overview
  getExecutive: (status = 'Aprovado', ano = 'Todos', categories: string[] = []) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (ano) params.append('ano', ano);
    categories.forEach(c => params.append('categoria', c));
    return fetchJson<ExecutiveOverviewData>(`${BASE_URL}/analytics/executive?${params.toString()}`);
  },

  // Sales & Margin
  getSales: (channels: string[] = [], categories: string[] = []) => {
    const params = new URLSearchParams();
    channels.forEach(c => params.append('canal', c));
    categories.forEach(c => params.append('categoria', c));
    return fetchJson<SalesAnalyticsData>(`${BASE_URL}/analytics/sales?${params.toString()}`);
  },

  // Marketing
  getMarketing: (channels: string[] = []) => {
    const params = new URLSearchParams();
    channels.forEach(c => params.append('canal', c));
    return fetchJson<MarketingAnalyticsData>(`${BASE_URL}/analytics/marketing?${params.toString()}`);
  },

  // Inventory
  getInventory: (categories: string[] = []) => {
    const params = new URLSearchParams();
    categories.forEach(c => params.append('categoria', c));
    return fetchJson<InventoryAnalyticsData>(`${BASE_URL}/analytics/inventory?${params.toString()}`);
  },

  // Customers
  getCustomers: (segments: string[] = []) => {
    const params = new URLSearchParams();
    segments.forEach(s => params.append('segmento', s));
    return fetchJson<CustomerAnalyticsData>(`${BASE_URL}/analytics/customers?${params.toString()}`);
  },

  // Support & AI
  getSupport: (channels: string[] = []) => {
    const params = new URLSearchParams();
    channels.forEach(c => params.append('canal', c));
    return fetchJson<SupportAnalyticsData>(`${BASE_URL}/analytics/support?${params.toString()}`);
  },

  // Audit
  getRelationalAudit: () => fetchJson<RelationalAuditData>(`${BASE_URL}/audit/relational`),
  
  getOutliers: (table = 'vendas', metric?: string) => {
    const params = new URLSearchParams({ table });
    if (metric) params.append('metric', metric);
    return fetchJson<OutliersData>(`${BASE_URL}/audit/outliers?${params.toString()}`);
  },

  // Roadmap
  getRoadmap: () => fetchJson<RoadmapData>(`${BASE_URL}/roadmap/initiatives`),

  // Copilot Threads
  listThreads: () => fetchJson<{ threads: ChatThread[] }>(`${BASE_URL}/copilot/threads`),
  
  getThread: (threadId: string) => fetchJson<{ thread: ChatThread }>(`${BASE_URL}/copilot/threads/${threadId}`),
  
  createThread: (title = 'Nova Conversa', initialMessage?: string) =>
    fetchJson<{ thread: ChatThread }>(`${BASE_URL}/copilot/threads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, initial_message: initialMessage }),
    }),

  deleteThread: (threadId: string) =>
    fetchJson<{ status: string; thread_id: string }>(`${BASE_URL}/copilot/threads/${threadId}`, {
      method: 'DELETE',
    }),

  sendChatMessage: (threadId: string, message: string) =>
    fetchJson<{ thread_id: string; response: string; messages: any[]; title: string }>(`${BASE_URL}/copilot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ thread_id: threadId, message }),
    }),

  getLatestAudit: () => fetchJson<{ snapshot: any }>(`${BASE_URL}/copilot/audit/latest`),

  getCopilotPeriods: () => fetchJson<{ periods: PeriodMeta[] }>(`${BASE_URL}/copilot/periods`),

  runAudit: (params?: { period_key?: PeriodKey; send_email?: boolean; to_email?: string }) =>
    fetchJson<{
      success: boolean;
      analysis_success: boolean;
      deterministic_approved: boolean;
      email_status: string;
      timestamp: string;
      audit_thread_id: string;
      email_result?: any;
      deep_link_url: string;
      diagnostic: any;
    }>(`${BASE_URL}/copilot/audit/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params || {}),
    }),

  // Documentos e Entregáveis
  getDeliverables: () => fetchJson<DeliverableMeta[]>(`${BASE_URL}/deliverables`),

  getDeliverable: (docId: string) => fetchJson<DeliverableDetail>(`${BASE_URL}/deliverables/${docId}`),

  updateDeliverable: (docId: string, content: string) =>
    fetchJson<DeliverableDetail>(`${BASE_URL}/deliverables/${docId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    }),

  getDeliverableDownloadUrl: (docId: string) => `${BASE_URL}/deliverables/${docId}/download`,
  getDeliverablesZipUrl: () => `${BASE_URL}/deliverables/export/zip`,
};
