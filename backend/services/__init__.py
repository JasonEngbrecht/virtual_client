"""
Services module
Provides business logic and data access layers
"""

from .database import DatabaseService, BaseCRUD, db_service, get_db, Base
from .assignment_service import assignment_service
from .section_service import section_service
from .enrollment_service import enrollment_service
from .client_service import client_service
from .rubric_service import rubric_service

__all__ = [
    'DatabaseService',
    'BaseCRUD', 
    'db_service',
    'get_db',
    'Base',
    'assignment_service',
    'section_service',
    'enrollment_service',
    'client_service',
    'rubric_service'
]
