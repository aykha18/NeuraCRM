# Import all schemas to make them available when importing from schemas
from .kanban import (
    StageBase, StageCreate, StageUpdate, StageOut,
    DealBase, DealCreate, DealUpdate, DealOut,
    KanbanBoard
)

__all__ = [
    'StageBase', 'StageCreate', 'StageUpdate', 'StageOut',
    'DealBase', 'DealCreate', 'DealUpdate', 'DealOut',
    'KanbanBoard'
]
