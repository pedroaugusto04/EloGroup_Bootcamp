import React, { useState, useEffect } from 'react';
import { ViewTab, FilterOptions } from './types/analytics';
import { api } from './api/client';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { ExecutiveView } from './components/views/ExecutiveView';
import { InventoryView } from './components/views/InventoryView';
import { MarketingView } from './components/views/MarketingView';
import { CustomersView } from './components/views/CustomersView';
import { SupportView } from './components/views/SupportView';
import { AuditRelationalView } from './components/views/AuditRelationalView';
import { OutliersView } from './components/views/OutliersView';
import { RoadmapView } from './components/views/RoadmapView';
import { CopilotView } from './components/views/CopilotView';
import { AuditEmailModal } from './components/common/AuditEmailModal';

const getInitialNavState = (): { tab: ViewTab; threadId: string | null } => {
  if (typeof window === 'undefined') return { tab: 'executive', threadId: null };

  const params = new URLSearchParams(window.location.search);
  const viewParam = (params.get('view') || params.get('tab') || '').toLowerCase();
  const threadId = params.get('thread_id') || params.get('thread') || params.get('threadId') || null;
  const source = params.get('source');

  if (
    viewParam === 'copilot' ||
    viewParam === 'agent' ||
    viewParam === 'agente_consultor' ||
    viewParam === 'chat' ||
    threadId ||
    source === 'email'
  ) {
    return { tab: 'copilot', threadId };
  }

  if (viewParam === 'marketing' || viewParam === 'mkt' || viewParam === 'midia') return { tab: 'marketing', threadId: null };
  if (viewParam === 'customers' || viewParam === 'clientes' || viewParam === 'rfm') return { tab: 'customers', threadId: null };
  if (viewParam === 'support' || viewParam === 'atendimento' || viewParam === 'suporte') return { tab: 'support', threadId: null };
  if (viewParam === 'inventory' || viewParam === 'estoque') return { tab: 'inventory', threadId: null };
  if (viewParam === 'outliers' || viewParam === 'dispersao') return { tab: 'outliers', threadId: null };
  if (viewParam === 'audit' || viewParam === 'auditoria' || viewParam === 'relacional') return { tab: 'audit', threadId: null };
  if (viewParam === 'roadmap' || viewParam === 'plano') return { tab: 'roadmap', threadId: null };

  return { tab: 'executive', threadId: null };
};

export const App: React.FC = () => {
  const initialNav = getInitialNavState();
  const [activeTab, setActiveTab] = useState<ViewTab>(initialNav.tab);
  const [initialThreadId, setInitialThreadId] = useState<string | null>(initialNav.threadId);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | undefined>(undefined);
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [auditModalOpen, setAuditModalOpen] = useState(false);

  useEffect(() => {
    api.getFilters()
      .then(opts => setFilterOptions(opts))
      .catch(err => console.error('Erro ao buscar opções de filtro:', err));
  }, []);

  const handleTabChange = (tab: ViewTab) => {
    setActiveTab(tab);
    // Sincroniza a URL sem recarregar
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('view', tab);
      if (tab !== 'copilot') {
        url.searchParams.delete('thread_id');
        url.searchParams.delete('thread');
        url.searchParams.delete('source');
      }
      window.history.replaceState({}, '', url.toString());
    } catch {
      // ignore
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    setRefreshKey(prev => prev + 1);
    setTimeout(() => setLoading(false), 400);
  };

  const handleAuditSuccess = (threadId: string) => {
    setInitialThreadId(threadId);
    handleTabChange('copilot');
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0a0914] text-[#f4f4f5]">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#0a0914] min-w-0">
        <Header
          activeTab={activeTab}
          onRefresh={handleRefresh}
          loading={loading}
          onOpenSidebar={() => setSidebarOpen(true)}
          onOpenAuditModal={() => setAuditModalOpen(true)}
        />

        {/* Dynamic View Container */}
        {activeTab === 'copilot' ? (
          <div className="flex-1 h-full min-h-0 overflow-hidden" key={refreshKey}>
            <CopilotView
              initialThreadId={initialThreadId}
              onOpenAuditModal={() => setAuditModalOpen(true)}
            />
          </div>
        ) : (
          <main className="flex-1 overflow-y-auto overflow-x-hidden p-3 sm:p-5 md:p-8" key={refreshKey}>
            <div className="max-w-7xl mx-auto pb-12 w-full">
              {activeTab === 'executive' && <ExecutiveView filterOptions={filterOptions} />}
              {activeTab === 'marketing' && <MarketingView filterOptions={filterOptions} />}
              {activeTab === 'customers' && <CustomersView filterOptions={filterOptions} />}
              {activeTab === 'support' && <SupportView filterOptions={filterOptions} />}
              {activeTab === 'inventory' && (
                <InventoryView
                  filterOptions={filterOptions}
                  onOpenAuditModal={() => setAuditModalOpen(true)}
                />
              )}
              {activeTab === 'audit' && <AuditRelationalView />}
              {activeTab === 'outliers' && <OutliersView />}
              {activeTab === 'roadmap' && <RoadmapView />}
            </div>
          </main>
        )}
      </div>

      {/* Audit & Email Dispatch Modal */}
      <AuditEmailModal
        isOpen={auditModalOpen}
        onClose={() => setAuditModalOpen(false)}
        onSuccess={handleAuditSuccess}
      />
    </div>
  );
};

export default App;
