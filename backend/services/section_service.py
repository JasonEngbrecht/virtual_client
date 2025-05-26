"""
Section Service
Handles business logic for course section operations
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models.course_section import CourseSectionDB, CourseSectionCreate, SectionEnrollmentDB
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
    
    def get_section_stats(self, db: Session, section_id: str) -> Dict:
        """
        Get enrollment statistics for a single section.
        
        Args:
            db: Database session
            section_id: ID of the section
            
        Returns:
            Dictionary with section statistics including:
            - section_id: str
            - active_enrollments: int
            - inactive_enrollments: int  
            - total_enrollments: int
        """
        # Use SQL aggregation to count enrollments efficiently
        stats = db.query(
            func.count(case((SectionEnrollmentDB.is_active == True, 1))).label('active_enrollments'),
            func.count(case((SectionEnrollmentDB.is_active == False, 1))).label('inactive_enrollments'),
            func.count(SectionEnrollmentDB.id).label('total_enrollments')
        ).filter(
            SectionEnrollmentDB.section_id == section_id
        ).first()
        
        return {
            "section_id": section_id,
            "active_enrollments": stats.active_enrollments or 0,
            "inactive_enrollments": stats.inactive_enrollments or 0,
            "total_enrollments": stats.total_enrollments or 0
        }
    
    def get_all_sections_stats(self, db: Session, teacher_id: str) -> List[Dict]:
        """
        Get enrollment statistics for all teacher's sections.
        Uses efficient SQL to avoid N+1 queries.
        
        Args:
            db: Database session
            teacher_id: ID of the teacher
            
        Returns:
            List of dictionaries with section info and statistics
        """
        # First, get all teacher's sections
        sections = db.query(
            CourseSectionDB.id,
            CourseSectionDB.name
        ).filter(
            CourseSectionDB.teacher_id == teacher_id
        ).all()
        
        if not sections:
            return []
        
        # Get enrollment counts for all sections in one query
        section_ids = [s.id for s in sections]
        enrollment_stats = db.query(
            SectionEnrollmentDB.section_id,
            func.count(case((SectionEnrollmentDB.is_active == True, 1))).label('active_enrollments'),
            func.count(case((SectionEnrollmentDB.is_active == False, 1))).label('inactive_enrollments'),
            func.count(SectionEnrollmentDB.id).label('total_enrollments')
        ).filter(
            SectionEnrollmentDB.section_id.in_(section_ids)
        ).group_by(
            SectionEnrollmentDB.section_id
        ).all()
        
        # Convert to dict for easy lookup
        stats_dict = {
            stat.section_id: {
                "active_enrollments": stat.active_enrollments,
                "inactive_enrollments": stat.inactive_enrollments,
                "total_enrollments": stat.total_enrollments
            }
            for stat in enrollment_stats
        }
        
        # Combine section info with stats
        result = []
        for section in sections:
            stats = stats_dict.get(section.id, {
                "active_enrollments": 0,
                "inactive_enrollments": 0,
                "total_enrollments": 0
            })
            result.append({
                "section_id": section.id,
                "name": section.name,
                **stats
            })
        
        return result


# Create global instance
section_service = SectionService()
