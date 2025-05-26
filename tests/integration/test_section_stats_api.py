"""
Integration tests for section statistics API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import app
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.services.section_service import section_service
from backend.services.enrollment_service import enrollment_service
from backend.services import get_db
from backend.services.database import Base, db_service


# Create test client
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    """Create a test database for the module."""
    # Create all tables using SQLAlchemy
    Base.metadata.create_all(bind=db_service.engine)
    yield
    # Cleanup handled by in-memory database


@pytest.fixture(autouse=True)
def clean_sections(test_db):
    """Clean up sections before each test."""
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        # Delete all sections (this will cascade to enrollments)
        db.query(CourseSectionDB).delete()
        db.commit()
    finally:
        db.close()


# Test section data
TEST_SECTION_DATA = {
    "name": "Test Section for Stats",
    "description": "A test section for statistics testing",
    "course_code": "TEST101",
    "term": "Test Term"
}


def test_get_section_stats_with_enrollments():
    """Test getting stats for a section with enrollments."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=TEST_SECTION_DATA)
    assert create_response.status_code == 201
    section = create_response.json()
    section_id = section["id"]
    
    # Get database session
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        # Enroll some students
        enrollment_service.enroll_student(db, section_id, "student-001")
        enrollment_service.enroll_student(db, section_id, "student-002")
        enrollment_service.enroll_student(db, section_id, "student-003")
        
        # Unenroll one student (creates inactive enrollment)
        enrollment_service.unenroll_student(db, section_id, "student-003")
        db.commit()
    finally:
        db.close()
    
    # Get stats for the section
    response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["section_id"] == section_id
    assert stats["name"] == TEST_SECTION_DATA["name"]
    assert stats["active_enrollments"] == 2
    assert stats["inactive_enrollments"] == 1
    assert stats["total_enrollments"] == 3


def test_get_section_stats_no_enrollments():
    """Test getting stats for a section with no enrollments."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=TEST_SECTION_DATA)
    assert create_response.status_code == 201
    section = create_response.json()
    section_id = section["id"]
    
    # Get stats for the section (no enrollments)
    response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["section_id"] == section_id
    assert stats["name"] == TEST_SECTION_DATA["name"]
    assert stats["active_enrollments"] == 0
    assert stats["inactive_enrollments"] == 0
    assert stats["total_enrollments"] == 0


def test_get_all_sections_stats():
    """Test getting stats for all teacher's sections."""
    # Create multiple sections
    section1_data = {
        "name": "SW 101 - Fall 2025",
        "description": "Introduction to Social Work",
        "course_code": "SW101",
        "term": "Fall 2025"
    }
    create_response1 = client.post("/api/teacher/sections", json=section1_data)
    assert create_response1.status_code == 201
    section1 = create_response1.json()
    
    section2_data = {
        "name": "SW 201 - Fall 2025",
        "description": "Advanced Social Work",
        "course_code": "SW201",
        "term": "Fall 2025"
    }
    create_response2 = client.post("/api/teacher/sections", json=section2_data)
    assert create_response2.status_code == 201
    section2 = create_response2.json()
    
    # Get database session
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        # Add enrollments to first section
        enrollment_service.enroll_student(db, section1["id"], "student-001")
        enrollment_service.enroll_student(db, section1["id"], "student-002")
        enrollment_service.unenroll_student(db, section1["id"], "student-002")
        
        # Add enrollments to second section
        enrollment_service.enroll_student(db, section2["id"], "student-003")
        enrollment_service.enroll_student(db, section2["id"], "student-004")
        enrollment_service.enroll_student(db, section2["id"], "student-005")
        db.commit()
    finally:
        db.close()
    
    # Get stats for all sections
    response = client.get("/api/teacher/sections/stats")
        
    assert response.status_code == 200
    stats_list = response.json()
    
    # Should have at least the two sections we created
    assert len(stats_list) >= 2
    
    # Find our sections in the results
    section1_stats = next(s for s in stats_list if s["section_id"] == section1["id"])
    section2_stats = next(s for s in stats_list if s["section_id"] == section2["id"])
    
    # Verify section 1 stats
    assert section1_stats["name"] == "SW 101 - Fall 2025"
    assert section1_stats["active_enrollments"] == 1
    assert section1_stats["inactive_enrollments"] == 1
    assert section1_stats["total_enrollments"] == 2
    
    # Verify section 2 stats
    assert section2_stats["name"] == "SW 201 - Fall 2025"
    assert section2_stats["active_enrollments"] == 3
    assert section2_stats["inactive_enrollments"] == 0
    assert section2_stats["total_enrollments"] == 3


def test_get_section_stats_not_found():
    """Test getting stats for non-existent section returns 404."""
    response = client.get("/api/teacher/sections/nonexistent-id/stats")
        
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_section_stats_forbidden():
    """Test getting stats for another teacher's section returns 403."""
    # Create a section
    create_response = client.post("/api/teacher/sections", json=TEST_SECTION_DATA)
    assert create_response.status_code == 201
    section = create_response.json()
    section_id = section["id"]
    
    # Change the teacher_id in the database
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        db_section = db.query(CourseSectionDB).filter_by(id=section_id).first()
        db_section.teacher_id = "other-teacher-456"
        db.commit()
    finally:
        db.close()
    
    # Try to access with original teacher ID (should fail)
    response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_inactive_enrollment_counting():
    """Test that inactive enrollments are counted correctly."""
    # Create a section
    create_response = client.post("/api/teacher/sections", json=TEST_SECTION_DATA)
    assert create_response.status_code == 201
    section = create_response.json()
    section_id = section["id"]
    
    # Get database session
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        # Enroll and unenroll multiple students
        students = ["student-001", "student-002", "student-003", "student-004", "student-005"]
        
        # Enroll all students
        for student_id in students:
            enrollment_service.enroll_student(db, section_id, student_id)
        
        # Unenroll some students
        enrollment_service.unenroll_student(db, section_id, "student-002")
        enrollment_service.unenroll_student(db, section_id, "student-004")
        db.commit()
    finally:
        db.close()
    
    # Get stats
    response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["active_enrollments"] == 3
    assert stats["inactive_enrollments"] == 2
    assert stats["total_enrollments"] == 5


def test_get_all_sections_stats_empty():
    """Test getting stats when teacher has no sections."""
    # Clean all sections first  
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        db.query(CourseSectionDB).delete()
        db.commit()
    finally:
        db.close()
    
    # Get stats (should be empty)
    response = client.get("/api/teacher/sections/stats")
        
    assert response.status_code == 200
    stats_list = response.json()
    assert stats_list == []


def test_get_all_sections_stats_with_mixed_enrollments():
    """Test bulk stats with sections having different enrollment patterns."""
    # Create sections with different enrollment patterns
    sections = []
    
    # Section with no enrollments
    create_response1 = client.post("/api/teacher/sections", json={
        "name": "Empty Section",
        "course_code": "EMPTY"
    })
    assert create_response1.status_code == 201
    section1 = create_response1.json()
    sections.append(section1)
    
    # Section with only active enrollments
    create_response2 = client.post("/api/teacher/sections", json={
        "name": "Active Only",
        "course_code": "ACTIVE"
    })
    assert create_response2.status_code == 201
    section2 = create_response2.json()
    sections.append(section2)
    
    # Section with only inactive enrollments
    create_response3 = client.post("/api/teacher/sections", json={
        "name": "Inactive Only",
        "course_code": "INACTIVE"
    })
    assert create_response3.status_code == 201
    section3 = create_response3.json()
    sections.append(section3)
    
    # Get database session and add enrollments
    from backend.services.database import db_service
    db = db_service.SessionLocal()
    try:
        # Add active enrollments to section 2
        enrollment_service.enroll_student(db, section2["id"], "student-001")
        enrollment_service.enroll_student(db, section2["id"], "student-002")
        
        # Add inactive enrollments to section 3
        enrollment_service.enroll_student(db, section3["id"], "student-003")
        enrollment_service.enroll_student(db, section3["id"], "student-004")
        enrollment_service.unenroll_student(db, section3["id"], "student-003")
        enrollment_service.unenroll_student(db, section3["id"], "student-004")
        db.commit()
    finally:
        db.close()
    
    # Get stats for all sections
    response = client.get("/api/teacher/sections/stats")
        
    assert response.status_code == 200
    stats_list = response.json()
    
    # Find our sections
    empty_stats = next(s for s in stats_list if s["section_id"] == section1["id"])
    active_stats = next(s for s in stats_list if s["section_id"] == section2["id"])
    inactive_stats = next(s for s in stats_list if s["section_id"] == section3["id"])
    
    # Verify empty section
    assert empty_stats["active_enrollments"] == 0
    assert empty_stats["inactive_enrollments"] == 0
    assert empty_stats["total_enrollments"] == 0
    
    # Verify active-only section
    assert active_stats["active_enrollments"] == 2
    assert active_stats["inactive_enrollments"] == 0
    assert active_stats["total_enrollments"] == 2
    
    # Verify inactive-only section
    assert inactive_stats["active_enrollments"] == 0
    assert inactive_stats["inactive_enrollments"] == 2
    assert inactive_stats["total_enrollments"] == 2
