"""
Quick test script to verify course section models are working
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.models.course_section import (
    CourseSectionDB, SectionEnrollmentDB,
    CourseSectionCreate, CourseSectionUpdate,
    CourseSection, SectionEnrollmentCreate, SectionEnrollment
)
from backend.services.database import DatabaseService, Base
from datetime import datetime
from uuid import uuid4


def test_models():
    """Test that models can be instantiated"""
    print("Testing model instantiation...")
    
    # Test database models
    section = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-123",
        name="Test Course",
        is_active=True
    )
    print(f"✓ Created CourseSectionDB: {section}")
    
    enrollment = SectionEnrollmentDB(
        id=str(uuid4()),
        section_id=section.id,
        student_id="student-456",
        is_active=True
    )
    print(f"✓ Created SectionEnrollmentDB: {enrollment}")
    
    # Test Pydantic schemas
    create_data = CourseSectionCreate(
        name="Social Work 101",
        description="Introduction to Social Work",
        course_code="SW101",
        term="Fall 2025"
    )
    print(f"✓ Created CourseSectionCreate schema")
    
    enrollment_data = SectionEnrollmentCreate(
        student_id="student-789",
        role="student"
    )
    print(f"✓ Created SectionEnrollmentCreate schema")
    
    print("\nAll models instantiated successfully!")


def test_database_tables():
    """Test that tables can be created in database"""
    print("\nTesting database table creation...")
    
    # Create in-memory database
    db_service = DatabaseService("sqlite:///:memory:")
    
    # Import all models to ensure they're registered with Base
    from backend.models import (
        ClientProfileDB, EvaluationRubricDB, 
        SessionDB, EvaluationDB,
        CourseSectionDB, SectionEnrollmentDB
    )
    
    # Create tables
    Base.metadata.create_all(bind=db_service.engine)
    
    # Check that tables exist
    from sqlalchemy import inspect
    inspector = inspect(db_service.engine)
    tables = inspector.get_table_names()
    
    print(f"Created tables: {tables}")
    
    expected_tables = [
        'client_profiles',
        'evaluation_rubrics', 
        'sessions',
        'evaluations',
        'course_sections',
        'section_enrollments'
    ]
    
    for table in expected_tables:
        if table in tables:
            print(f"✓ Table '{table}' created successfully")
        else:
            print(f"✗ Table '{table}' NOT found!")
    
    # Test inserting data
    with db_service.get_db() as db:
        section = CourseSectionDB(
            teacher_id="teacher-123",
            name="Test Course in DB",
            is_active=True
        )
        db.add(section)
        db.commit()
        
        # Query it back
        result = db.query(CourseSectionDB).first()
        if result:
            print(f"\n✓ Successfully saved and retrieved course section: {result.name}")
        else:
            print("\n✗ Failed to retrieve course section")


if __name__ == "__main__":
    print("=== Course Section Models Test ===\n")
    test_models()
    test_database_tables()
    print("\n=== All tests completed! ===")
