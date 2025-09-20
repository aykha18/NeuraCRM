import { useEffect, useCallback } from 'react';

interface Stage {
  id: number;
  name: string;
  order: number;
}

interface UseStageShortcutsProps {
  stages: Stage[];
  selectedDealId: string | null;
  onStageChange: (dealId: string, newStageId: number) => void;
  onNextStage: () => void;
  onPrevStage: () => void;
  enabled?: boolean;
}

export function useStageShortcuts({
  stages,
  selectedDealId,
  onStageChange,
  onNextStage,
  onPrevStage,
  enabled = true
}: UseStageShortcutsProps) {
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled || !selectedDealId) return;

    // Only handle shortcuts when no input/textarea is focused
    const activeElement = document.activeElement;
    if (activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.contentEditable === 'true'
    )) {
      return;
    }

    const currentDeal = stages.find(stage => stage.id === parseInt(selectedDealId));
    if (!currentDeal) return;

    const currentIndex = stages.findIndex(s => s.id === currentDeal.id);
    
    switch (event.key) {
      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault();
        if (currentIndex > 0) {
          const prevStage = stages[currentIndex - 1];
          onStageChange(selectedDealId, prevStage.id);
        }
        break;
        
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault();
        if (currentIndex < stages.length - 1) {
          const nextStage = stages[currentIndex + 1];
          onStageChange(selectedDealId, nextStage.id);
        }
        break;
        
      case 'w':
      case 'W':
        event.preventDefault();
        const wonStage = stages.find(s => s.name.toLowerCase().includes('won'));
        if (wonStage) {
          onStageChange(selectedDealId, wonStage.id);
        }
        break;
        
      case 'l':
      case 'L':
        event.preventDefault();
        const lostStage = stages.find(s => s.name.toLowerCase().includes('lost'));
        if (lostStage) {
          onStageChange(selectedDealId, lostStage.id);
        }
        break;
        
      case 'q':
      case 'Q':
        event.preventDefault();
        const qualStage = stages.find(s => s.name.toLowerCase().includes('qualification'));
        if (qualStage) {
          onStageChange(selectedDealId, qualStage.id);
        }
        break;
        
      case 'p':
      case 'P':
        event.preventDefault();
        const propStage = stages.find(s => s.name.toLowerCase().includes('proposal'));
        if (propStage) {
          onStageChange(selectedDealId, propStage.id);
        }
        break;
        
      case 'n':
      case 'N':
        event.preventDefault();
        const negStage = stages.find(s => s.name.toLowerCase().includes('negotiation'));
        if (negStage) {
          onStageChange(selectedDealId, negStage.id);
        }
        break;
        
      case 'Tab':
        event.preventDefault();
        onNextStage();
        break;
        
      case 'Shift':
        if (event.shiftKey) {
          event.preventDefault();
          onPrevStage();
        }
        break;
    }
  }, [stages, selectedDealId, onStageChange, onNextStage, onPrevStage, enabled]);

  useEffect(() => {
    if (enabled) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown, enabled]);

  return {
    shortcuts: {
      '←/↑': 'Previous stage',
      '→/↓': 'Next stage',
      'W': 'Mark as Won',
      'L': 'Mark as Lost',
      'Q': 'Move to Qualification',
      'P': 'Move to Proposal',
      'N': 'Move to Negotiation',
      'Tab': 'Next deal',
      'Shift+Tab': 'Previous deal'
    }
  };
}
