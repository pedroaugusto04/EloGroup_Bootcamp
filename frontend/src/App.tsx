import React, { useState, useEffect } from 'react';
import { ViewTab, FilterOptions } from './types/analytics';
import { api } from './api/client';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { ExecutiveView } from './components/views/ExecutiveView';
import { InventoryView } from './components/views/InventoryView';
import { GrowthView } from './components/views/GrowthView';
import { AuditView } from './components/views/AuditView';
import { CopilotRoadmapView } from './components/views/CopilotRoadmapView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ViewTab>('executive');
  const [filterOptions, setFilterOptions] = useState<FilterOptions | undefined>(undefined);
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getFilters()
      .then(opts => setFilterOptions(opts))
      .catch(err => console.error('Erro ao buscar opções de filtro:', err));
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setRefreshKey(prev => prev + 1);
    setTimeout(() => setLoading(false), 400);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#09090b] text-[#f4f4f5]">
      {/* Navigation Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#09090b]">
        <Header
          activeTab={activeTab}
          onRefresh={handleRefresh}
          loading={loading}
        />

        {/* Dynamic View Container */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8" key={refreshKey}>
          <div className="max-w-7xl mx-auto pb-12">
            {activeTab === 'executive' && <ExecutiveView filterOptions={filterOptions} />}
            {activeTab === 'inventory' && <InventoryView filterOptions={filterOptions} />}
            {activeTab === 'growth' && <GrowthView filterOptions={filterOptions} />}
            {activeTab === 'audit' && <AuditView />}
            {activeTab === 'copilot' && <CopilotRoadmapView />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
