/**
 * Enhanced Kanban Board with Multiple Stage Update Methods
 * - Quick action buttons on deal cards
 * - Bulk stage updates
 * - Keyboard shortcuts
 * - Responsive stage navigation
 * - No horizontal scrolling required
 */
import React, { useState, useMemo, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getKanbanBoard, moveDeal, updateDeal, type KanbanBoard as ApiKanbanBoard, type Deal as ApiDeal } from '../services/kanban';
import DealCard from '../components/DealCard';
import BulkStageUpdateModal from '../components/BulkStageUpdateModal';
import StageNavigation from '../components/StageNavigation';
import { useStageShortcuts } from '../hooks/useStageShortcuts';
import { Plus, Settings, Keyboard, Info } from 'lucide-react';

interface Deal {
  id: string;
  title: string;
  value: string;
  owner: string;
  stage: string;
  stage_id: number;
  watchers: string[];
}

interface Stage {
  id: number;
  name: string;
  order: number;
  deal_count?: number;
}

interface DealsByStage {
  [stageId: number]: Deal[];
}

export default function KanbanEnhanced() {
  const queryClient = useQueryClient();
  
  // State
  const [selectedDeals, setSelectedDeals] = useState<string[]>([]);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [selectedDealId, setSelectedDealId] = useState<string | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [filters, setFilters] = useState<{ stage_id?: number; owner_id?: number; search?: string }>({});
  const [viewingDeal, setViewingDeal] = useState<Deal | null>(null);

  // Fetch kanban data
  const { data: kanbanData, isLoading, error } = useQuery<ApiKanbanBoard>({
    queryKey: ['kanban', filters],
    queryFn: () => getKanbanBoard(filters),
  });

  // Group deals by stage
  const dealsByStage = useMemo<DealsByStage>(() => {
    if (!kanbanData?.deals || !kanbanData?.stages) return {};
    
    const stageMap = new Map<number, string>();
    kanbanData.stages.forEach(stage => stageMap.set(stage.id, stage.name));
    
    return kanbanData.deals.reduce((acc, deal) => {
      const stageId = deal.stage_id;
      if (!acc[stageId]) {
        acc[stageId] = [];
      }
      
      const frontendDeal: Deal = {
        ...deal,
        id: String(deal.id),
        value: `$${deal.value?.toLocaleString() || '0'}`,
        owner: deal.owner_name || 'Unassigned',
        stage: stageMap.get(stageId) || 'Unknown',
        watchers: deal.watchers || [],
      };
      
      acc[stageId].push(frontendDeal);
      return acc;
    }, {} as DealsByStage);
  }, [kanbanData]);

  // Get sorted stages
  const stages = useMemo(() => {
    if (!kanbanData?.stages) return [];
    return [...kanbanData.stages].sort((a, b) => a.order - b.order);
  }, [kanbanData?.stages]);

  // Filtered deals by stage
  const filteredDealsByStage = useMemo(() => {
    if (!filters.search) return dealsByStage;
    
    const filtered: DealsByStage = {};
    Object.entries(dealsByStage).forEach(([stageId, deals]) => {
      const filteredDeals = deals.filter(deal => 
        deal.title.toLowerCase().includes(filters.search!.toLowerCase()) ||
        deal.owner.toLowerCase().includes(filters.search!.toLowerCase())
      );
      if (filteredDeals.length > 0) {
        filtered[parseInt(stageId)] = filteredDeals;
      }
    });
    return filtered;
  }, [dealsByStage, filters.search]);

  // Stage change handler
  const handleStageChange = useCallback(async (dealId: string, newStageId: number) => {
    try {
      await moveDeal(parseInt(dealId), newStageId, 0);
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
    } catch (error) {
      console.error('Failed to move deal:', error);
    }
  }, [queryClient]);

  // Bulk stage update
  const handleBulkStageUpdate = useCallback(async (dealIds: string[], newStageId: number) => {
    try {
      await Promise.all(dealIds.map(dealId => moveDeal(parseInt(dealId), newStageId, 0)));
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
      setSelectedDeals([]);
    } catch (error) {
      console.error('Failed to bulk update stages:', error);
      throw error;
    }
  }, [queryClient]);

  // Deal selection
  const toggleDealSelection = useCallback((dealId: string) => {
    setSelectedDeals(prev => 
      prev.includes(dealId) 
        ? prev.filter(id => id !== dealId)
        : [...prev, dealId]
    );
  }, []);

  // Select all deals in current view
  const selectAllDeals = useCallback(() => {
    const allDeals = Object.values(filteredDealsByStage).flat();
    setSelectedDeals(allDeals.map(deal => deal.id));
  }, [filteredDealsByStage]);

  // Clear selection
  const clearSelection = useCallback(() => {
    setSelectedDeals([]);
  }, []);

  // Keyboard shortcuts
  const { shortcuts } = useStageShortcuts({
    stages,
    selectedDealId,
    onStageChange: handleStageChange,
    onNextStage: () => {
      // Navigate to next deal logic
      const allDeals = Object.values(filteredDealsByStage).flat();
      const currentIndex = allDeals.findIndex(deal => deal.id === selectedDealId);
      if (currentIndex < allDeals.length - 1) {
        setSelectedDealId(allDeals[currentIndex + 1].id);
      }
    },
    onPrevStage: () => {
      // Navigate to previous deal logic
      const allDeals = Object.values(filteredDealsByStage).flat();
      const currentIndex = allDeals.findIndex(deal => deal.id === selectedDealId);
      if (currentIndex > 0) {
        setSelectedDealId(allDeals[currentIndex - 1].id);
      }
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading deals...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Failed to load deals</div>
      </div>
    );
  }

  const selectedDealsData = selectedDeals.map(dealId => 
    Object.values(filteredDealsByStage).flat().find(deal => deal.id === dealId)
  ).filter(Boolean) as Deal[];

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Deals Pipeline
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {Object.values(filteredDealsByStage).flat().length} deals across {stages.length} stages
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Selection Actions */}
            {selectedDeals.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {selectedDeals.length} selected
                </span>
                <button
                  onClick={() => setShowBulkModal(true)}
                  className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                >
                  Bulk Update
                </button>
                <button
                  onClick={clearSelection}
                  className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
                >
                  Clear
                </button>
              </div>
            )}
            
            {/* Select All */}
            {selectedDeals.length === 0 && (
              <button
                onClick={selectAllDeals}
                className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
              >
                Select All
              </button>
            )}
            
            {/* Shortcuts Help */}
            <button
              onClick={() => setShowShortcuts(!showShortcuts)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              title="Keyboard Shortcuts"
            >
              <Keyboard className="w-5 h-5" />
            </button>
            
            {/* Settings */}
            <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Stage Navigation */}
      <StageNavigation
        stages={stages}
        currentStageId={filters.stage_id}
        onStageSelect={(stageId) => setFilters(prev => ({ ...prev, stage_id: stageId }))}
        onFilterChange={setFilters}
      />

      {/* Keyboard Shortcuts Help */}
      {showShortcuts && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800 p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                Keyboard Shortcuts
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                {Object.entries(shortcuts).map(([key, description]) => (
                  <div key={key} className="flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs font-mono">
                      {key}
                    </kbd>
                    <span className="text-blue-700 dark:text-blue-300">{description}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {filters.stage_id ? (
          // Single Stage View
          <div className="h-full p-4">
            <div className="h-full overflow-y-auto">
              <div className="grid gap-3">
                {filteredDealsByStage[filters.stage_id]?.map((deal) => (
                  <div key={deal.id} className="relative">
                    <input
                      type="checkbox"
                      checked={selectedDeals.includes(deal.id)}
                      onChange={() => toggleDealSelection(deal.id)}
                      className="absolute top-4 left-4 z-10"
                    />
                    <div className={`${selectedDeals.includes(deal.id) ? 'ml-8' : ''}`}>
                      <DealCard
                        deal={deal}
                        stages={stages}
                        onStageChange={handleStageChange}
                        onView={setViewingDeal}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          // All Stages View (Vertical Layout)
          <div className="h-full overflow-y-auto p-4">
            <div className="space-y-6">
              {stages.map((stage) => (
                <div key={stage.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {stage.name}
                      </h2>
                      <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full text-sm">
                        {filteredDealsByStage[stage.id]?.length || 0} deals
                      </span>
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="grid gap-3">
                      {filteredDealsByStage[stage.id]?.map((deal) => (
                        <div key={deal.id} className="relative">
                          <input
                            type="checkbox"
                            checked={selectedDeals.includes(deal.id)}
                            onChange={() => toggleDealSelection(deal.id)}
                            className="absolute top-4 left-4 z-10"
                          />
                          <div className={`${selectedDeals.includes(deal.id) ? 'ml-8' : ''}`}>
                            <DealCard
                              deal={deal}
                              stages={stages}
                              onStageChange={handleStageChange}
                              onView={setViewingDeal}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bulk Update Modal */}
      <BulkStageUpdateModal
        isOpen={showBulkModal}
        onClose={() => setShowBulkModal(false)}
        selectedDeals={selectedDealsData}
        stages={stages}
        onUpdateStages={handleBulkStageUpdate}
      />

      {/* Deal Detail Modal */}
      {viewingDeal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {viewingDeal.title}
            </h2>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Value:</span>
                <span className="ml-2 text-gray-900 dark:text-gray-100">{viewingDeal.value}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Owner:</span>
                <span className="ml-2 text-gray-900 dark:text-gray-100">{viewingDeal.owner}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Stage:</span>
                <span className="ml-2 text-gray-900 dark:text-gray-100">{viewingDeal.stage}</span>
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setViewingDeal(null)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
