"""
Section Service
Handles business logic for course section operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.course_section import CourseSectionDB, CourseSectionCreate
from .database import BaseCRUD


class SectionService(BaseCRUD[CourseSectionDB]):
    """
    Service class for course section operations
    Inherits generic CRUD operations from BaseCRUD
    """
    
    def __init__(self):
        """Initialize section service with CourseSectionDB model"""
        super().__init__(CourseSectionDB)
    
    def get_teacher_sections(
        self,
        db: Session,
        teacher_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseSectionDB]:
        """
        Get all sections for a specific teacher
        
        Args:
            db: Database session
            teacher_id: ID of the teacher
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of course sections created by the teacher
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            teacher_id=teacher_id
        )
    
    def create_section_for_teacher(
        self,
        db: Session,
        section_data: CourseSectionCreate,
        teacher_id: str
    ) -> CourseSectionDB:
        """
        Create a new course section for a specific teacher
        
        Args:
            db: Database session
            section_data: Course section data
            teacher_id: ID of the teacher creating the section
            
        Returns:
            Created course section
        """
        # Convert Pydantic model to dict and add teacher_id
        section_dict = section_data.model_dump()
        section_dict['teacher_id'] = teacher_id
        
        return self.create(db, **section_dict)
    
    def can_update(
        self,
        db: Session,
        section_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can update a specific section
        
        Args:
            db: Database session
            section_id: ID of the section
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can update the section, False otherwise
        """
        section = self.get(db, section_id)
        if not section:
            return False
        return section.teacher_id == teacher_id
    
    def can_delete(
        self,
        db: Session,
        section_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can delete a specific section
        
        Args:
            db: Database session
            section_id: ID of the section
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can delete the section, False otherwise
        """
        # For now, using same logic as can_update
        # Could be different in the future (e.g., admin override)
        return self.can_update(db, section_id, teacher_id)


# Create global instance
section_service = SectionService()
