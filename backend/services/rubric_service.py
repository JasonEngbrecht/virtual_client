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
    
    def get_teacher_rubrics(
        self,
        db: Session,
        teacher_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EvaluationRubricDB]:
        """
        Get all rubrics for a specific teacher
        
        Args:
            db: Database session
            teacher_id: ID of the teacher
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of evaluation rubrics created by the teacher
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            created_by=teacher_id
        )
    
    def create_rubric_for_teacher(
        self,
        db: Session,
        rubric_data: EvaluationRubricCreate,
        teacher_id: str
    ) -> EvaluationRubricDB:
        """
        Create a new evaluation rubric for a specific teacher
        
        Args:
            db: Database session
            rubric_data: Evaluation rubric data
            teacher_id: ID of the teacher creating the rubric
            
        Returns:
            Created evaluation rubric
        """
        # Convert Pydantic model to dict and add teacher_id
        rubric_dict = rubric_data.model_dump()
        rubric_dict['created_by'] = teacher_id
        
        return self.create(db, **rubric_dict)
    
    def can_update(
        self,
        db: Session,
        rubric_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can update a specific rubric
        
        Args:
            db: Database session
            rubric_id: ID of the rubric
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can update the rubric, False otherwise
        """
        rubric = self.get(db, rubric_id)
        if not rubric:
            return False
        return rubric.created_by == teacher_id
    
    def can_delete(
        self,
        db: Session,
        rubric_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can delete a specific rubric
        
        Args:
            db: Database session
            rubric_id: ID of the rubric
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can delete the rubric, False otherwise
        """
        # For now, using same logic as can_update
        # Could be different in the future (e.g., admin override)
        return self.can_update(db, rubric_id, teacher_id)


# Create global instance
rubric_service = RubricService()
