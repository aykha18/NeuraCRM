import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, MoreHorizontal, Filter } from 'lucide-react';

interface Stage {
  id: number;
  name: string;
  order: number;
  deal_count?: number;
}

interface StageNavigationProps {
  stages: Stage[];
  currentStageId?: number;
  onStageSelect: (stageId: number) => void;
  onFilterChange: (filters: { stage_id?: number; owner_id?: number; search?: string }) => void;
}

export default function StageNavigation({
  stages,
  currentStageId,
  onStageSelect,
  onFilterChange
}: StageNavigationProps) {
  const [showAllStages, setShowAllStages] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({ stage_id: undefined, owner_id: undefined, search: '' });

  const sortedStages = [...stages].sort((a, b) => a.order - b.order);
  
  // Show only 5 stages by default on mobile, all on desktop
  const visibleStages = showAllStages ? sortedStages : sortedStages.slice(0, 5);
  const hasMoreStages = sortedStages.length > 5;

  const handleStageClick = (stageId: number) => {
    onStageSelect(stageId);
    setFilters(prev => ({ ...prev, stage_id: stageId }));
    onFilterChange({ ...filters, stage_id: stageId });
  };

  const handleClearFilters = () => {
    setFilters({ stage_id: undefined, owner_id: undefined, search: '' });
    onFilterChange({});
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Main Stage Navigation */}
      <div className="flex items-center justify-between p-4">
        {/* Stage Pills */}
        <div className="flex items-center gap-2 flex-1 overflow-x-auto scrollbar-hide">
          {visibleStages.map((stage) => (
            <button
              key={stage.id}
              onClick={() => handleStageClick(stage.id)}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                currentStageId === stage.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <span className="whitespace-nowrap">{stage.name}</span>
              {stage.deal_count !== undefined && (
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                  currentStageId === stage.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                }`}>
                  {stage.deal_count}
                </span>
              )}
            </button>
          ))}
          
          {/* Show More Button */}
          {hasMoreStages && !showAllStages && (
            <button
              onClick={() => setShowAllStages(true)}
              className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <MoreHorizontal className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2 ml-4">
          {/* Filters Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg transition-colors ${
              showFilters || Object.values(filters).some(f => f)
                ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
            }`}
          >
            <Filter className="w-5 h-5" />
          </button>

          {/* Clear Filters */}
          {Object.values(filters).some(f => f) && (
            <button
              onClick={handleClearFilters}
              className="px-3 py-1 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Expanded Stages (Mobile) */}
      {hasMoreStages && showAllStages && (
        <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-2 mt-4">
            {sortedStages.slice(5).map((stage) => (
              <button
                key={stage.id}
                onClick={() => handleStageClick(stage.id)}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentStageId === stage.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <span>{stage.name}</span>
                {stage.deal_count !== undefined && (
                  <span className={`px-2 py-0.5 rounded-full text-xs ${
                    currentStageId === stage.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                  }`}>
                    {stage.deal_count}
                  </span>
                )}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowAllStages(false)}
            className="w-full mt-3 text-center text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            Show Less
          </button>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search deals..."
                value={filters.search}
                onChange={(e) => {
                  const newFilters = { ...filters, search: e.target.value };
                  setFilters(newFilters);
                  onFilterChange(newFilters);
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Owner Filter */}
            <div className="sm:w-48">
              <select
                value={filters.owner_id || ''}
                onChange={(e) => {
                  const newFilters = { ...filters, owner_id: e.target.value ? parseInt(e.target.value) : undefined };
                  setFilters(newFilters);
                  onFilterChange(newFilters);
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Owners</option>
                <option value="1">John Doe</option>
                <option value="2">Jane Smith</option>
                <option value="3">Mike Johnson</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
