import { useEffect, useState } from 'react';
import { Plus, MoreHorizontal, GripVertical } from 'lucide-react';
import { getKanbanBoard, moveDeal } from '../services/kanban';
import type { KanbanBoard as KanbanBoardType, Deal } from '../services/kanban';

export default function KanbanBoard() {
  const [board, setBoard] = useState<KanbanBoardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draggedDeal, setDraggedDeal] = useState<{ deal: Deal; sourceStageId: number } | null>(null);

  useEffect(() => {
    loadBoard();
  }, []);

  const loadBoard = async () => {
    try {
      setLoading(true);
      const data = await getKanbanBoard();
      setBoard(data);
      setError(null);
    } catch (err) {
      // failed to load kanban board
      setError('Failed to load kanban board');
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (deal: Deal, stageId: number) => {
    setDraggedDeal({ deal, sourceStageId: stageId });
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDrop = async (targetStageId: number, position: number) => {
    if (!draggedDeal) return;

    try {
      await moveDeal(draggedDeal.deal.id, targetStageId, position);
      await loadBoard(); // Refresh the board after moving
    } catch (err) {
      // failed to move deal
      setError('Failed to move deal');
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading kanban board...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-500">{error}</div>;
  }

  if (!board) {
    return <div className="p-8 text-center">No data available</div>;
  }

  return (
    <div className="flex-1 p-4 overflow-x-auto">
      <div className="flex space-x-4 min-w-max">
        {board.stages.map((stage) => (
          <div
            key={stage.id}
            className="w-72 bg-gray-50 rounded-lg shadow-sm flex flex-col"
            onDragOver={handleDragOver}
            onDrop={() => handleDrop(stage.id, 0)}
          >
            <div className="p-3 border-b flex justify-between items-center">
              <h3 className="font-medium">{stage.name}</h3>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-500">
                  {board.deals.filter((deal) => deal.stage_id === stage.id).length}
                </span>
                <button className="text-gray-400 hover:text-gray-600">
                  <MoreHorizontal size={16} />
                </button>
              </div>
            </div>
            <div className="p-2 flex-1 overflow-y-auto min-h-[100px]">
              {board.deals
                .filter((deal) => deal.stage_id === stage.id)
                .map((deal) => (
                  <div
                    key={deal.id}
                    className="bg-white p-3 mb-2 rounded border hover:shadow-md transition-shadow cursor-move"
                    draggable
                    onDragStart={() => handleDragStart(deal, stage.id)}
                  >
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium text-sm">{deal.title}</h4>
                      <button className="text-gray-400 hover:text-gray-600">
                        <GripVertical size={16} />
                      </button>
                    </div>
                    {deal.value && (
                      <div className="mt-1 text-sm font-medium">
                        ${deal.value.toLocaleString()}
                      </div>
                    )}
                    {deal.contact_name && (
                      <div className="mt-1 text-xs text-gray-500">
                        {deal.contact_name}
                      </div>
                    )}
                  </div>
                ))}
              <button className="w-full mt-2 p-2 text-sm text-gray-500 hover:bg-gray-100 rounded flex items-center justify-center">
                <Plus size={16} className="mr-1" /> Add card
              </button>
            </div>
          </div>
        ))}
        <div className="w-72">
          <button className="w-full p-3 text-sm text-gray-500 hover:bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
            <Plus size={16} className="mr-1" /> Add another list
          </button>
        </div>
      </div>
    </div>
  );
}
