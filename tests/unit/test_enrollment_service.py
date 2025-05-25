"""
Unit tests for enrollment service
Tests all enrollment management functionality
"""

import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.enrollment_service import enrollment_service
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.services.section_service import section_service
from backend.services.database import db_service


@pytest.fixture
def test_sections(db_session):
    """Create test sections for enrollment tests"""
    section1 = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-123",
        name="Test Section 1",
        description="Test section for enrollment tests",
        is_active=True
    )
    section2 = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-456",
        name="Test Section 2",
        description="Another test section",
        is_active=True
    )
    
    db_session.add(section1)
    db_session.add(section2)
    db_session.commit()
    db_session.refresh(section1)
    db_session.refresh(section2)
    
    # Return sections for use in tests
    return section1, section2


@pytest.fixture
def student_ids():
    """Test student IDs"""
    return {
        'student1': "student-001",
        'student2': "student-002",
        'student3': "student-003"
    }


class TestEnrollmentService:
    """Test suite for enrollment service"""
    
    def test_service_instantiation(self):
        """Test that enrollment service can be instantiated"""
        assert enrollment_service is not None
        assert enrollment_service.model == SectionEnrollmentDB
    
    def test_enroll_student_success(self, db_session: Session, test_sections, student_ids):
        """Test successful student enrollment"""
        section1, section2 = test_sections
        
        # Enroll student
        enrollment = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Verify enrollment
        assert enrollment is not None
        assert enrollment.section_id == section1.id
        assert enrollment.student_id == student_ids['student1']
        assert enrollment.is_active is True
        assert enrollment.role == "student"
        assert enrollment.enrolled_at is not None
    
    def test_enroll_student_with_ta_role(self, db_session: Session, test_sections, student_ids):
        """Test enrolling a student as a TA"""
        section1, section2 = test_sections
        
        enrollment = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1'],
            role="ta"
        )
        
        assert enrollment is not None
        assert enrollment.role == "ta"
    
    def test_enroll_student_duplicate_active(self, db_session: Session, test_sections, student_ids):
        """Test that duplicate active enrollments return existing enrollment"""
        section1, section2 = test_sections
        
        # First enrollment
        enrollment1 = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Attempt duplicate enrollment
        enrollment2 = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Should return the same enrollment
        assert enrollment2.id == enrollment1.id
        assert enrollment2.is_active is True
        
        # Verify only one enrollment exists
        count = db_session.query(SectionEnrollmentDB).filter(
            SectionEnrollmentDB.section_id == section1.id,
            SectionEnrollmentDB.student_id == student_ids['student1']
        ).count()
        assert count == 1
    
    def test_enroll_student_reactivate_inactive(self, db_session: Session, test_sections, student_ids):
        """Test that enrolling after unenrollment reactivates the enrollment"""
        section1, section2 = test_sections
        
        # Enroll student
        enrollment1 = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Unenroll student
        success = enrollment_service.unenroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        assert success is True
        
        # Re-enroll student
        enrollment2 = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Should reactivate the same enrollment
        assert enrollment2.id == enrollment1.id
        assert enrollment2.is_active is True
    
    def test_enroll_student_invalid_section(self, db_session: Session, student_ids):
        """Test enrolling in non-existent section returns None"""
        enrollment = enrollment_service.enroll_student(
            db_session,
            section_id="invalid-section-id",
            student_id=student_ids['student1']
        )
        
        assert enrollment is None
    
    def test_unenroll_student_success(self, db_session: Session, test_sections, student_ids):
        """Test successful student unenrollment"""
        section1, section2 = test_sections
        
        # First enroll the student
        enrollment = enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        assert enrollment is not None
        
        # Unenroll the student
        success = enrollment_service.unenroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        assert success is True
        
        # Verify enrollment is inactive
        db_session.refresh(enrollment)
        assert enrollment.is_active is False
    
    def test_unenroll_student_not_enrolled(self, db_session: Session, test_sections, student_ids):
        """Test unenrolling a student who isn't enrolled"""
        section1, section2 = test_sections
        
        success = enrollment_service.unenroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        assert success is False
    
    def test_unenroll_student_already_inactive(self, db_session: Session, test_sections, student_ids):
        """Test unenrolling a student who is already unenrolled"""
        section1, section2 = test_sections
        
        # Enroll and then unenroll
        enrollment_service.enroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        enrollment_service.unenroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        # Try to unenroll again
        success = enrollment_service.unenroll_student(
            db_session,
            section_id=section1.id,
            student_id=student_ids['student1']
        )
        
        assert success is False
    
    def test_get_section_roster_active_only(self, db_session: Session, test_sections, student_ids):
        """Test getting active enrollments for a section"""
        section1, section2 = test_sections
        
        # Enroll multiple students
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student2'])
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student3'])
        
        # Unenroll one student
        enrollment_service.unenroll_student(db_session, section1.id, student_ids['student2'])
        
        # Get roster (active only by default)
        roster = enrollment_service.get_section_roster(db_session, section1.id)
        
        assert len(roster) == 2
        student_ids_in_roster = [e.student_id for e in roster]
        assert student_ids['student1'] in student_ids_in_roster
        assert student_ids['student3'] in student_ids_in_roster
        assert student_ids['student2'] not in student_ids_in_roster
    
    def test_get_section_roster_include_inactive(self, db_session: Session, test_sections, student_ids):
        """Test getting all enrollments including inactive"""
        section1, section2 = test_sections
        
        # Enroll and unenroll
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student2'])
        enrollment_service.unenroll_student(db_session, section1.id, student_ids['student2'])
        
        # Get roster including inactive
        roster = enrollment_service.get_section_roster(
            db_session, 
            section1.id,
            include_inactive=True
        )
        
        assert len(roster) == 2
        active_count = sum(1 for e in roster if e.is_active)
        assert active_count == 1
    
    def test_get_section_roster_empty(self, db_session: Session, test_sections):
        """Test getting roster for section with no enrollments"""
        section1, section2 = test_sections
        
        roster = enrollment_service.get_section_roster(db_session, section1.id)
        assert len(roster) == 0
    
    def test_is_student_enrolled_active(self, db_session: Session, test_sections, student_ids):
        """Test checking if student is actively enrolled"""
        section1, section2 = test_sections
        
        # Not enrolled yet
        assert enrollment_service.is_student_enrolled(
            db_session, section1.id, student_ids['student1']
        ) is False
        
        # Enroll student
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        
        # Now enrolled
        assert enrollment_service.is_student_enrolled(
            db_session, section1.id, student_ids['student1']
        ) is True
    
    def test_is_student_enrolled_inactive(self, db_session: Session, test_sections, student_ids):
        """Test that inactive enrollments return False"""
        section1, section2 = test_sections
        
        # Enroll and unenroll
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        enrollment_service.unenroll_student(db_session, section1.id, student_ids['student1'])
        
        # Should return False for inactive enrollment
        assert enrollment_service.is_student_enrolled(
            db_session, section1.id, student_ids['student1']
        ) is False
    
    def test_get_student_sections_active_only(self, db_session: Session, test_sections, student_ids):
        """Test getting sections a student is actively enrolled in"""
        section1, section2 = test_sections
        
        # Enroll in multiple sections
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        enrollment_service.enroll_student(db_session, section2.id, student_ids['student1'])
        
        # Unenroll from one section
        enrollment_service.unenroll_student(db_session, section1.id, student_ids['student1'])
        
        # Get student's sections
        sections = enrollment_service.get_student_sections(db_session, student_ids['student1'])
        
        assert len(sections) == 1
        assert sections[0].id == section2.id
    
    def test_get_student_sections_include_inactive(self, db_session: Session, test_sections, student_ids):
        """Test getting all sections including those with inactive enrollments"""
        section1, section2 = test_sections
        
        # Enroll and unenroll
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        enrollment_service.enroll_student(db_session, section2.id, student_ids['student1'])
        enrollment_service.unenroll_student(db_session, section1.id, student_ids['student1'])
        
        # Get all sections including inactive
        sections = enrollment_service.get_student_sections(
            db_session, 
            student_ids['student1'],
            include_inactive=True
        )
        
        assert len(sections) == 2
        section_ids = [s.id for s in sections]
        assert section1.id in section_ids
        assert section2.id in section_ids
    
    def test_get_student_sections_no_enrollments(self, db_session: Session, student_ids):
        """Test getting sections for student with no enrollments"""
        sections = enrollment_service.get_student_sections(db_session, student_ids['student1'])
        assert len(sections) == 0
    
    def test_get_enrollment_exists(self, db_session: Session, test_sections, student_ids):
        """Test getting a specific enrollment record"""
        section1, section2 = test_sections
        
        # Create enrollment
        enrollment = enrollment_service.enroll_student(
            db_session, section1.id, student_ids['student1']
        )
        
        # Get enrollment
        retrieved = enrollment_service.get_enrollment(
            db_session, section1.id, student_ids['student1']
        )
        
        assert retrieved is not None
        assert retrieved.id == enrollment.id
    
    def test_get_enrollment_not_exists(self, db_session: Session, test_sections, student_ids):
        """Test getting non-existent enrollment returns None"""
        section1, section2 = test_sections
        
        enrollment = enrollment_service.get_enrollment(
            db_session, section1.id, student_ids['student1']
        )
        assert enrollment is None
    
    def test_enrollment_ordering(self, db_session: Session, test_sections, student_ids):
        """Test that enrollments are ordered by date"""
        import time
        section1, section2 = test_sections
        
        # Enroll students with slight delays
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student1'])
        time.sleep(0.1)  # Small delay to ensure different timestamps
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student2'])
        time.sleep(0.1)
        enrollment_service.enroll_student(db_session, section1.id, student_ids['student3'])
        
        # Get roster - should be ordered by enrollment date
        roster = enrollment_service.get_section_roster(db_session, section1.id)
        
        assert len(roster) == 3
        # First enrolled should be first in list
        assert roster[0].student_id == student_ids['student1']
        assert roster[1].student_id == student_ids['student2']
        assert roster[2].student_id == student_ids['student3']
