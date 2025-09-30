"""
Initializes the routers package, making router modules available for import.
"""
from . import auth
from . import kanban
from . import conversational_ai
# Add other router imports here as they are created
# For example:
# from . import contacts
# from . import deals

# You can optionally define __all__ to specify what `from .routers import *` imports
__all__ = [
    "auth",
    "kanban",
    "conversational_ai",
]
