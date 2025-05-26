"""
Services module
Provides business logic and data access layers
"""

# Only import database-related items to avoid circular imports
# Service instances should be imported directly where needed
from .database import DatabaseService, BaseCRUD, db_service, get_db, Base

__all__ = [
    'DatabaseService',
    'BaseCRUD', 
    'db_service',
    'get_db',
    'Base'
]
