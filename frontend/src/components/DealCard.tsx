import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, Check, X, Clock, FileText } from 'lucide-react';

interface Deal {
  id: string;
  title: string;
  value: string;
  owner: string;
  stage: string;
  stage_id: number;
}

interface Stage {
  id: number;
  name: string;
  order: number;
}

interface DealCardProps {
  deal: Deal;
  stages: Stage[];
  onStageChange: (dealId: string, newStageId: number) => void;
  onView: (deal: Deal) => void;
  loading?: boolean;
}

export default function DealCard({ deal, stages, onStageChange, onView, loading = false }: DealCardProps) {
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [showStageDropdown, setShowStageDropdown] = useState(false);

  // Get current stage index
  const currentStageIndex = stages.findIndex(s => s.id === deal.stage_id);
  const currentStage = stages[currentStageIndex];

  // Quick actions based on current stage
  const getQuickActions = () => {
    const actions = [];
    
    // Previous stage action
    if (currentStageIndex > 0) {
      const prevStage = stages[currentStageIndex - 1];
      actions.push({
        label: `← ${prevStage.name}`,
        stageId: prevStage.id,
        icon: ChevronLeft,
        color: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
      });
    }

    // Next stage action
    if (currentStageIndex < stages.length - 1) {
      const nextStage = stages[currentStageIndex + 1];
      actions.push({
        label: `${nextStage.name} →`,
        stageId: nextStage.id,
        icon: ChevronRight,
        color: 'bg-green-100 text-green-700 hover:bg-green-200'
      });
    }

    // Special actions for specific stages
    if (currentStage?.name === 'Proposal') {
      actions.push({
        label: 'Send Proposal',
        stageId: stages.find(s => s.name === 'Proposal Sent')?.id,
        icon: FileText,
        color: 'bg-purple-100 text-purple-700 hover:bg-purple-200'
      });
    }

    if (currentStage?.name === 'Negotiation') {
      actions.push({
        label: 'Close Won',
        stageId: stages.find(s => s.name === 'Won')?.id,
        icon: Check,
        color: 'bg-green-100 text-green-700 hover:bg-green-200'
      });
      actions.push({
        label: 'Close Lost',
        stageId: stages.find(s => s.name === 'Lost')?.id,
        icon: X,
        color: 'bg-red-100 text-red-700 hover:bg-red-200'
      });
    }

    return actions;
  };

  const quickActions = getQuickActions();

  const handleStageChange = (newStageId: number) => {
    onStageChange(deal.id, newStageId);
    setShowQuickActions(false);
    setShowStageDropdown(false);
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-3 hover:shadow-md transition-shadow">
      {/* Deal Header */}
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm line-clamp-2">
          {deal.title}
        </h3>
        <div className="flex gap-1">
          {/* Quick Actions Toggle */}
          <button
            onClick={() => setShowQuickActions(!showQuickActions)}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="Quick Actions"
          >
            <Clock className="w-4 h-4" />
          </button>
          
          {/* Stage Dropdown Toggle */}
          <button
            onClick={() => setShowStageDropdown(!showStageDropdown)}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="Change Stage"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
          
          {/* View Button */}
          <button
            onClick={() => onView(deal)}
            className="p-1 text-blue-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors"
            title="View Details"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Deal Value */}
      <div className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
        {deal.value}
      </div>

      {/* Deal Owner */}
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        {deal.owner}
      </div>

      {/* Quick Actions */}
      {showQuickActions && quickActions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10 p-2">
          <div className="grid grid-cols-1 gap-1">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleStageChange(action.stageId)}
                disabled={loading}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${action.color}`}
              >
                <action.icon className="w-4 h-4" />
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Stage Dropdown */}
      {showStageDropdown && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10 p-2 max-h-60 overflow-y-auto">
          <div className="space-y-1">
            {stages.map((stage) => (
              <button
                key={stage.id}
                onClick={() => handleStageChange(stage.id)}
                disabled={loading || stage.id === deal.stage_id}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  stage.id === deal.stage_id
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {stage.name}
                {stage.id === deal.stage_id && (
                  <span className="ml-2 text-xs">(current)</span>
                )}
              </button>
            ))}
          </div>
        </div>
        )}
    </div>
  );
}
