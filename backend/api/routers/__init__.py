"""
Initializes the routers package, making router modules available for import.
"""
from . import auth
from . import kanban
from . import conversational_ai
# from . import rag
from . import predictive_analytics
from . import email_automation
from . import chat
# Add other router imports here as they are created
# For example:
# from . import contacts
# from . import deals

# You can optionally define __all__ to specify what `from .routers import *` imports
__all__ = [
    "auth",
    "kanban",
    "conversational_ai",
    # "rag",
    "predictive_analytics",
    "email_automation",
    "chat",
]
