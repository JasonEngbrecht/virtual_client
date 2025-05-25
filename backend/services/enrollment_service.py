"""
Enrollment Service
Handles business logic for student enrollment operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.course_section import SectionEnrollmentDB, CourseSectionDB, SectionEnrollmentCreate
from .database import BaseCRUD
import logging

logger = logging.getLogger(__name__)


class EnrollmentService(BaseCRUD[SectionEnrollmentDB]):
    """
    Service class for enrollment operations
    Manages student-section relationships with soft delete support
    """
    
    def __init__(self):
        """Initialize enrollment service with SectionEnrollmentDB model"""
        super().__init__(SectionEnrollmentDB)
    
    def enroll_student(
        self,
        db: Session,
        section_id: str,
        student_id: str,
        role: str = "student"
    ) -> Optional[SectionEnrollmentDB]:
        """
        Enroll a student in a section
        
        Args:
            db: Database session
            section_id: ID of the course section
            student_id: ID of the student to enroll
            role: Role in the section (default: "student")
            
        Returns:
            Created enrollment or None if duplicate/invalid
            
        Business Rules:
            - No duplicate active enrollments allowed
            - Reactivates existing inactive enrollment if found
            - Validates section exists before enrolling
        """
        # Check if section exists
        section = db.query(CourseSectionDB).filter(
            CourseSectionDB.id == section_id
        ).first()
        
        if not section:
            logger.warning(f"Cannot enroll student {student_id}: Section {section_id} not found")
            return None
        
        # Check for existing enrollment (active or inactive)
        existing = db.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section_id,
            SectionEnrollmentDB.student_id == student_id
        ).first()
        
        if existing:
            if existing.is_active:
                # Already enrolled and active
                logger.info(f"Student {student_id} already enrolled in section {section_id}")
                return existing
            else:
                # Reactivate inactive enrollment
                existing.is_active = True
                db.commit()
                db.refresh(existing)
                logger.info(f"Reactivated enrollment for student {student_id} in section {section_id}")
                return existing
        
        # Create new enrollment
        enrollment = self.create(
            db,
            section_id=section_id,
            student_id=student_id,
            role=role,
            is_active=True
        )
        logger.info(f"Enrolled student {student_id} in section {section_id}")
        return enrollment
    
    def unenroll_student(
        self,
        db: Session,
        section_id: str,
        student_id: str
    ) -> bool:
        """
        Unenroll a student from a section (soft delete)
        
        Args:
            db: Database session
            section_id: ID of the course section
            student_id: ID of the student to unenroll
            
        Returns:
            True if unenrolled, False if not found or already inactive
            
        Business Rules:
            - Uses soft delete (sets is_active=False)
            - Preserves enrollment history
            - Returns False if already inactive
        """
        enrollment = db.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section_id,
            SectionEnrollmentDB.student_id == student_id,
            SectionEnrollmentDB.is_active == True
        ).first()
        
        if not enrollment:
            logger.warning(f"No active enrollment found for student {student_id} in section {section_id}")
            return False
        
        # Soft delete - set is_active to False
        enrollment.is_active = False
        db.commit()
        logger.info(f"Unenrolled student {student_id} from section {section_id}")
        return True
    
    def get_section_roster(
        self,
        db: Session,
        section_id: str,
        include_inactive: bool = False
    ) -> List[SectionEnrollmentDB]:
        """
        Get all enrollments for a section
        
        Args:
            db: Database session
            section_id: ID of the course section
            include_inactive: Whether to include inactive enrollments
            
        Returns:
            List of enrollments for the section
            
        Business Rules:
            - By default, only returns active enrollments
            - Can optionally include inactive for historical data
            - Orders by enrollment date
        """
        query = db.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section_id
        )
        
        if not include_inactive:
            query = query.filter(SectionEnrollmentDB.is_active == True)
        
        enrollments = query.order_by(SectionEnrollmentDB.enrolled_at).all()
        logger.debug(f"Retrieved {len(enrollments)} enrollments for section {section_id}")
        return enrollments
    
    def is_student_enrolled(
        self,
        db: Session,
        section_id: str,
        student_id: str
    ) -> bool:
        """
        Check if a student is actively enrolled in a section
        
        Args:
            db: Database session
            section_id: ID of the course section
            student_id: ID of the student
            
        Returns:
            True if student is actively enrolled, False otherwise
            
        Business Rules:
            - Only checks active enrollments
            - Returns False for inactive enrollments
        """
        enrollment = db.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section_id,
            SectionEnrollmentDB.student_id == student_id,
            SectionEnrollmentDB.is_active == True
        ).first()
        
        return enrollment is not None
    
    def get_student_sections(
        self,
        db: Session,
        student_id: str,
        include_inactive: bool = False
    ) -> List[CourseSectionDB]:
        """
        Get all sections a student is enrolled in
        
        Args:
            db: Database session
            student_id: ID of the student
            include_inactive: Whether to include sections from inactive enrollments
            
        Returns:
            List of course sections the student is enrolled in
            
        Business Rules:
            - By default, only returns sections with active enrollments
            - Joins with course_sections to return full section data
            - Orders by enrollment date (most recent first)
        """
        query = db.query(CourseSectionDB).join(
            SectionEnrollmentDB,
            CourseSectionDB.id == SectionEnrollmentDB.section_id
        ).filter(
            SectionEnrollmentDB.student_id == student_id
        )
        
        if not include_inactive:
            query = query.filter(SectionEnrollmentDB.is_active == True)
        
        sections = query.order_by(SectionEnrollmentDB.enrolled_at.desc()).all()
        logger.debug(f"Retrieved {len(sections)} sections for student {student_id}")
        return sections
    
    def get_enrollment(
        self,
        db: Session,
        section_id: str,
        student_id: str
    ) -> Optional[SectionEnrollmentDB]:
        """
        Get a specific enrollment record
        
        Args:
            db: Database session
            section_id: ID of the course section
            student_id: ID of the student
            
        Returns:
            Enrollment record or None if not found
            
        Note:
            Returns both active and inactive enrollments
        """
        return db.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section_id,
            SectionEnrollmentDB.student_id == student_id
        ).first()


# Create global instance
enrollment_service = EnrollmentService()
