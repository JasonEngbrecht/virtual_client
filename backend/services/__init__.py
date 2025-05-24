"""
Services module
Provides business logic and data access layers
"""

from .database import DatabaseService, BaseCRUD, db_service, get_db, Base
from .client_service import ClientService, client_service

__all__ = [
    'DatabaseService',
    'BaseCRUD', 
    'db_service',
    'get_db',
    'Base',
    'ClientService',
    'client_service'
]
