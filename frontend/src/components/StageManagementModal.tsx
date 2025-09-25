import { useState, useEffect } from 'react';
import { X, Plus, Edit2, Trash2, GripVertical } from 'lucide-react';
import { stageService, type Stage, type StageCreate, type StageUpdate } from '../services/kanban';
import ConfirmationModal from './ConfirmationModal';

interface StageManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStagesUpdated: () => void;
}

export default function StageManagementModal({ isOpen, onClose, onStagesUpdated }: StageManagementModalProps) {
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingStage, setEditingStage] = useState<Stage | null>(null);
  const [newStage, setNewStage] = useState<StageCreate>({
    name: '',
    order: 0,
    wip_limit: undefined
  });
  
  // Confirmation modal state
  const [confirmationModal, setConfirmationModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
    type?: 'danger' | 'warning' | 'info';
  }>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });

  // Load stages when modal opens
  useEffect(() => {
    if (isOpen) {
      loadStages();
    }
  }, [isOpen]);

  const loadStages = async () => {
    setLoading(true);
    setError(null);
    try {
      const stagesData = await stageService.getStages();
      setStages(stagesData);
    } catch (err) {
      setError('Failed to load stages');
      console.error('Error loading stages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStage = async () => {
    if (!newStage.name.trim()) return;
    
    setLoading(true);
    try {
      const nextOrder = Math.max(...stages.map(s => s.order), 0) + 1;
      await stageService.createStage({
        ...newStage,
        order: nextOrder
      });
      setNewStage({ name: '', order: 0, wip_limit: undefined });
      setShowCreateForm(false);
      await loadStages();
      onStagesUpdated();
    } catch (err) {
      setError('Failed to create stage');
      console.error('Error creating stage:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStage = async (stage: Stage) => {
    setLoading(true);
    try {
      await stageService.updateStage(stage.id, {
        name: stage.name,
        order: stage.order,
        wip_limit: stage.wip_limit
      });
      setEditingStage(null);
      await loadStages();
      onStagesUpdated();
    } catch (err) {
      setError('Failed to update stage');
      console.error('Error updating stage:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteStage = async (stageId: number) => {
    // Use modern confirmation - could be enhanced with a modal in the future
    if (!window.confirm('Are you sure you want to delete this stage? Deals in this stage will be moved to the first stage.')) {
      return;
    }
    
    setLoading(true);
    try {
      await stageService.deleteStage(stageId);
      await loadStages();
      onStagesUpdated();
    } catch (err) {
      setError('Failed to delete stage');
      console.error('Error deleting stage:', err);
    } finally {
      setLoading(false);
    }
  };

  const moveStage = (index: number, direction: 'up' | 'down') => {
    const newStages = [...stages];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (targetIndex < 0 || targetIndex >= newStages.length) return;
    
    // Swap stages
    [newStages[index], newStages[targetIndex]] = [newStages[targetIndex], newStages[index]];
    
    // Update order values
    newStages.forEach((stage, idx) => {
      stage.order = idx + 1;
    });
    
    setStages(newStages);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Manage Stages</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
              {error}
            </div>
          )}

          {/* Create New Stage */}
          <div className="mb-6">
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add New Stage
            </button>

            {showCreateForm && (
              <div className="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Stage Name
                    </label>
                    <input
                      type="text"
                      value={newStage.name}
                      onChange={(e) => setNewStage({ ...newStage, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="Enter stage name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      WIP Limit (optional)
                    </label>
                    <input
                      type="number"
                      value={newStage.wip_limit || ''}
                      onChange={(e) => setNewStage({ ...newStage, wip_limit: e.target.value ? parseInt(e.target.value) : undefined })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="Maximum deals in this stage"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCreateStage}
                      disabled={loading || !newStage.name.trim()}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Create Stage
                    </button>
                    <button
                      onClick={() => {
                        setShowCreateForm(false);
                        setNewStage({ name: '', order: 0, wip_limit: undefined });
                      }}
                      className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stages List */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Current Stages</h3>
            {loading && stages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">Loading stages...</div>
            ) : stages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No stages found</div>
            ) : (
              stages.map((stage, index) => (
                <div
                  key={stage.id}
                  className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <GripVertical className="w-5 h-5 text-gray-400 cursor-move" />
                  
                  <div className="flex-1">
                    {editingStage?.id === stage.id ? (
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={editingStage.name}
                          onChange={(e) => setEditingStage({ ...editingStage, name: e.target.value })}
                          className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        />
                        <input
                          type="number"
                          value={editingStage.wip_limit || ''}
                          onChange={(e) => setEditingStage({ ...editingStage, wip_limit: e.target.value ? parseInt(e.target.value) : undefined })}
                          className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                          placeholder="WIP Limit"
                        />
                      </div>
                    ) : (
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{stage.name}</div>
                        <div className="text-sm text-gray-500">
                          Order: {stage.order}
                          {stage.wip_limit && ` • WIP Limit: ${stage.wip_limit}`}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Move buttons */}
                    <button
                      onClick={() => moveStage(index, 'up')}
                      disabled={index === 0}
                      className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Move up"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => moveStage(index, 'down')}
                      disabled={index === stages.length - 1}
                      className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Move down"
                    >
                      ↓
                    </button>

                    {/* Edit/Save buttons */}
                    {editingStage?.id === stage.id ? (
                      <button
                        onClick={() => handleUpdateStage(editingStage)}
                        disabled={loading}
                        className="p-2 text-green-600 hover:text-green-700 disabled:opacity-50"
                        title="Save changes"
                      >
                        ✓
                      </button>
                    ) : (
                      <button
                        onClick={() => setEditingStage(stage)}
                        className="p-2 text-blue-600 hover:text-blue-700"
                        title="Edit stage"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    )}

                    {/* Delete button */}
                    <button
                      onClick={() => handleDeleteStage(stage.id)}
                      disabled={loading}
                      className="p-2 text-red-600 hover:text-red-700 disabled:opacity-50"
                      title="Delete stage"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
