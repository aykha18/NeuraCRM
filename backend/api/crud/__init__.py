# Import all CRUD modules to make them available when importing from crud
from .kanban import (
    get_kanban_board,
    get_stage, get_stages, create_stage, update_stage, delete_stage,
    get_deal, create_deal, update_deal, delete_deal, move_deal
)

# Create a namespace for kanban CRUD operations
kanban = (
    get_kanban_board,
    get_stage, get_stages, create_stage, update_stage, delete_stage,
    get_deal, create_deal, update_deal, delete_deal, move_deal
)

__all__ = [
    'kanban',
    'get_kanban_board',
    'get_stage', 'get_stages', 'create_stage', 'update_stage', 'delete_stage',
    'get_deal', 'create_deal', 'update_deal', 'delete_deal', 'move_deal'
]
