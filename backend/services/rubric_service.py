"""
Rubric Service
Handles business logic for evaluation rubric operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.rubric import EvaluationRubricDB, EvaluationRubricCreate
from .database import BaseCRUD


class RubricService(BaseCRUD[EvaluationRubricDB]):
    """
    Service class for evaluation rubric operations
    Inherits generic CRUD operations from BaseCRUD
    """
    
    def __init__(self):
        """Initialize rubric service with EvaluationRubricDB model"""
        super().__init__(EvaluationRubricDB)


# Create global instance
rubric_service = RubricService()
