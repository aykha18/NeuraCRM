import React, { useState } from 'react';
import { X, Check, AlertTriangle } from 'lucide-react';

interface Stage {
  id: number;
  name: string;
  order: number;
}

interface Deal {
  id: string;
  title: string;
  value: string;
  stage_id: number;
}

interface BulkStageUpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDeals: Deal[];
  stages: Stage[];
  onUpdateStages: (dealIds: string[], newStageId: number) => Promise<void>;
}

export default function BulkStageUpdateModal({
  isOpen,
  onClose,
  selectedDeals,
  stages,
  onUpdateStages
}: BulkStageUpdateModalProps) {
  const [selectedStageId, setSelectedStageId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpdate = async () => {
    if (!selectedStageId) {
      setError('Please select a stage');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const dealIds = selectedDeals.map(deal => deal.id);
      await onUpdateStages(dealIds, selectedStageId);
      onClose();
      setSelectedStageId(null);
    } catch (err) {
      setError('Failed to update stages');
    } finally {
      setLoading(false);
    }
  };

  const totalValue = selectedDeals.reduce((sum, deal) => {
    const value = parseFloat(deal.value.replace(/[$,]/g, '')) || 0;
    return sum + value;
  }, 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Bulk Update Stages
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Selected Deals Summary */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Check className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-900 dark:text-blue-100">
                {selectedDeals.length} deals selected
              </span>
            </div>
            <div className="text-sm text-blue-700 dark:text-blue-300">
              Total Value: ${totalValue.toLocaleString()}
            </div>
          </div>

          {/* Stage Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Move to Stage:
            </label>
            <select
              value={selectedStageId || ''}
              onChange={(e) => setSelectedStageId(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a stage...</option>
              {stages.map((stage) => (
                <option key={stage.id} value={stage.id}>
                  {stage.name}
                </option>
              ))}
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}

          {/* Selected Deals List */}
          <div className="max-h-40 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-lg">
            {selectedDeals.map((deal) => (
              <div key={deal.id} className="flex justify-between items-center p-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
                <div>
                  <div className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                    {deal.title}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {deal.value}
                  </div>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {stages.find(s => s.id === deal.stage_id)?.name}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpdate}
            disabled={!selectedStageId || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Updating...' : 'Update Stages'}
          </button>
        </div>
      </div>
    </div>
  );
}
