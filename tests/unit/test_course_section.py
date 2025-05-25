"""
Unit tests for Course Section models
Tests basic model instantiation and database operations
"""

import pytest
from datetime import datetime
from uuid import uuid4

from backend.models.course_section import (
    CourseSectionDB, SectionEnrollmentDB,
    CourseSectionCreate, CourseSectionUpdate, CourseSection,
    SectionEnrollmentCreate, SectionEnrollment
)


class TestCourseSectionModels:
    """Test course section database models"""
    
    def test_course_section_db_instantiation(self):
        """Test creating a CourseSectionDB instance"""
        section = CourseSectionDB(
            id=str(uuid4()),
            teacher_id="teacher-123",
            name="Social Work Practice I - Fall 2025",
            description="Introduction to social work practice",
            course_code="SW101",
            term="Fall 2025",
            is_active=True,
            settings={"allow_late_submissions": True}
        )
        
        assert section.teacher_id == "teacher-123"
        assert section.name == "Social Work Practice I - Fall 2025"
        assert section.course_code == "SW101"
        assert section.is_active is True
        assert section.settings["allow_late_submissions"] is True
    
    def test_section_enrollment_db_instantiation(self):
        """Test creating a SectionEnrollmentDB instance"""
        enrollment = SectionEnrollmentDB(
            id=str(uuid4()),
            section_id=str(uuid4()),
            student_id="student-456",
            is_active=True,
            role="student"
        )
        
        assert enrollment.student_id == "student-456"
        assert enrollment.is_active is True
        assert enrollment.role == "student"
    
    def test_course_section_db_in_database(self, db_session):
        """Test saving and retrieving a course section from database"""
        section_id = str(uuid4())
        section = CourseSectionDB(
            id=section_id,
            teacher_id="teacher-123",
            name="Test Course Section",
            description="Test description",
            course_code="TEST101",
            term="Test Term",
            is_active=True,
            settings={}
        )
        
        db_session.add(section)
        db_session.commit()
        
        # Retrieve from database
        retrieved = db_session.query(CourseSectionDB).filter_by(id=section_id).first()
        assert retrieved is not None
        assert retrieved.name == "Test Course Section"
        assert retrieved.teacher_id == "teacher-123"
        assert retrieved.course_code == "TEST101"
    
    def test_section_enrollment_db_in_database(self, db_session):
        """Test saving and retrieving an enrollment from database"""
        # First create a section
        section = CourseSectionDB(
            id=str(uuid4()),
            teacher_id="teacher-123",
            name="Test Section",
            is_active=True
        )
        db_session.add(section)
        db_session.commit()
        
        # Create enrollment
        enrollment_id = str(uuid4())
        enrollment = SectionEnrollmentDB(
            id=enrollment_id,
            section_id=section.id,
            student_id="student-456",
            is_active=True,
            role="student"
        )
        
        db_session.add(enrollment)
        db_session.commit()
        
        # Retrieve from database
        retrieved = db_session.query(SectionEnrollmentDB).filter_by(id=enrollment_id).first()
        assert retrieved is not None
        assert retrieved.student_id == "student-456"
        assert retrieved.section_id == section.id
        assert retrieved.role == "student"
    
    def test_section_enrollment_relationship(self, db_session):
        """Test the relationship between sections and enrollments"""
        # Create section
        section = CourseSectionDB(
            teacher_id="teacher-123",
            name="Test Section with Enrollments",
            is_active=True
        )
        db_session.add(section)
        db_session.commit()
        
        # Add multiple enrollments
        for i in range(3):
            enrollment = SectionEnrollmentDB(
                section_id=section.id,
                student_id=f"student-{i}",
                is_active=True,
                role="student"
            )
            db_session.add(enrollment)
        
        db_session.commit()
        db_session.refresh(section)
        
        # Check relationship
        assert len(section.enrollments) == 3
        assert all(e.section_id == section.id for e in section.enrollments)
        assert section.enrollments[0].section == section


class TestCourseSectionSchemas:
    """Test Pydantic schemas for course sections"""
    
    def test_course_section_create_schema(self):
        """Test CourseSectionCreate schema validation"""
        data = {
            "name": "Social Work Practice I",
            "description": "Introduction to practice",
            "course_code": "SW101",
            "term": "Fall 2025",
            "is_active": True,
            "settings": {"max_students": 30}
        }
        
        schema = CourseSectionCreate(**data)
        assert schema.name == "Social Work Practice I"
        assert schema.course_code == "SW101"
        assert schema.settings["max_students"] == 30
    
    def test_course_section_create_minimal(self):
        """Test CourseSectionCreate with minimal data"""
        data = {"name": "Basic Course"}
        schema = CourseSectionCreate(**data)
        
        assert schema.name == "Basic Course"
        assert schema.description is None
        assert schema.course_code is None
        assert schema.is_active is True  # default value
        assert schema.settings == {}  # default empty dict
    
    def test_course_section_update_schema(self):
        """Test CourseSectionUpdate schema for partial updates"""
        data = {
            "description": "Updated description",
            "is_active": False
        }
        
        schema = CourseSectionUpdate(**data)
        assert schema.description == "Updated description"
        assert schema.is_active is False
        assert schema.name is None  # not provided
        assert schema.course_code is None  # not provided
    
    def test_course_section_response_schema(self):
        """Test CourseSection response schema"""
        data = {
            "id": str(uuid4()),
            "teacher_id": "teacher-123",
            "name": "Test Course",
            "description": "Test description",
            "course_code": "TEST101",
            "term": "Fall 2025",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "settings": {},
            "enrollment_count": 25
        }
        
        schema = CourseSection(**data)
        assert schema.teacher_id == "teacher-123"
        assert schema.enrollment_count == 25
    
    def test_section_enrollment_create_schema(self):
        """Test SectionEnrollmentCreate schema"""
        data = {
            "student_id": "student-789",
            "role": "student"
        }
        
        schema = SectionEnrollmentCreate(**data)
        assert schema.student_id == "student-789"
        assert schema.role == "student"
    
    def test_section_enrollment_create_default_role(self):
        """Test SectionEnrollmentCreate with default role"""
        data = {"student_id": "student-999"}
        schema = SectionEnrollmentCreate(**data)
        
        assert schema.student_id == "student-999"
        assert schema.role == "student"  # default value
    
    def test_section_enrollment_response_schema(self):
        """Test SectionEnrollment response schema"""
        data = {
            "id": str(uuid4()),
            "section_id": str(uuid4()),
            "student_id": "student-123",
            "enrolled_at": datetime.utcnow(),
            "is_active": True,
            "role": "student",
            "student_name": "John Doe"  # optional field
        }
        
        schema = SectionEnrollment(**data)
        assert schema.student_id == "student-123"
        assert schema.student_name == "John Doe"
        assert schema.is_active is True


class TestSchemaValidation:
    """Test schema validation rules"""
    
    def test_course_section_name_validation(self):
        """Test name field validation"""
        # Empty name should fail
        with pytest.raises(ValueError):
            CourseSectionCreate(name="")
        
        # Very long name should fail (>200 chars)
        with pytest.raises(ValueError):
            CourseSectionCreate(name="x" * 201)
    
    def test_enrollment_role_validation(self):
        """Test role field validation"""
        # Invalid role should fail
        with pytest.raises(ValueError):
            SectionEnrollmentCreate(student_id="student-123", role="invalid_role")
        
        # Valid roles should pass
        valid_roles = ["student", "ta"]
        for role in valid_roles:
            schema = SectionEnrollmentCreate(student_id="student-123", role=role)
            assert schema.role == role
    
    def test_course_code_length_validation(self):
        """Test course code length limit"""
        # Should accept up to 20 characters
        data = {"name": "Test", "course_code": "A" * 20}
        schema = CourseSectionCreate(**data)
        assert len(schema.course_code) == 20
        
        # Should reject more than 20 characters
        with pytest.raises(ValueError):
            CourseSectionCreate(name="Test", course_code="A" * 21)
