"""
Rubric Service
Handles business logic for evaluation rubric operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..models.rubric import EvaluationRubricDB, EvaluationRubricCreate
from ..models.assignment import AssignmentClientDB
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
            
        Raises:
            ValueError: If rubric data contains duplicate criterion names
        """
        # Additional validation: Check for duplicate criterion names
        criterion_names = [c.name.lower() for c in rubric_data.criteria]
        if len(criterion_names) != len(set(criterion_names)):
            # Find duplicates
            duplicates = [name for name in criterion_names if criterion_names.count(name) > 1]
            unique_duplicates = list(set(duplicates))
            raise ValueError(
                f"Each criterion must have a unique name. Found duplicate criterion names: {', '.join(unique_duplicates)}. "
                f"Please use distinct names for each evaluation criterion."
            )
        
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
    
    def is_rubric_in_use(
        self,
        db: Session,
        rubric_id: str
    ) -> bool:
        """
        Check if a rubric is being used by any assignment-client relationships
        
        Args:
            db: Database session
            rubric_id: ID of the rubric to check
            
        Returns:
            True if rubric is referenced by any assignment-client relationships, False otherwise
        """
        # Query to check if any assignment-client relationships reference this rubric
        stmt = select(func.count(AssignmentClientDB.id)).where(AssignmentClientDB.rubric_id == rubric_id)
        count = db.execute(stmt).scalar()
        return count > 0
    
    def update(
        self,
        db: Session,
        id: str,
        **kwargs
    ) -> Optional[EvaluationRubricDB]:
        """
        Update a rubric with additional validation
        
        Args:
            db: Database session
            id: Rubric ID
            **kwargs: Fields to update
            
        Returns:
            Updated rubric instance or None if not found
            
        Raises:
            ValueError: If update contains duplicate criterion names
        """
        # If criteria are being updated, validate for duplicates
        if 'criteria' in kwargs and kwargs['criteria'] is not None:
            criteria = kwargs['criteria']
            # Handle both dict and object representations
            if isinstance(criteria, list) and len(criteria) > 0:
                # Extract names based on whether items are dicts or objects
                if isinstance(criteria[0], dict):
                    criterion_names = [c['name'].lower() for c in criteria]
                else:
                    criterion_names = [c.name.lower() for c in criteria]
                
                if len(criterion_names) != len(set(criterion_names)):
                    # Find duplicates
                    duplicates = [name for name in criterion_names if criterion_names.count(name) > 1]
                    unique_duplicates = list(set(duplicates))
                    raise ValueError(
                        f"Each criterion must have a unique name. Found duplicate criterion names: {', '.join(unique_duplicates)}. "
                        f"Please use distinct names for each evaluation criterion."
                    )
        
        # Call parent update method
        return super().update(db, id, **kwargs)


# Create global instance
rubric_service = RubricService()
