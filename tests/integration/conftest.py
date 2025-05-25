"""
Pytest configuration for integration tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.app import app
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.api.teacher_routes import get_current_teacher


@pytest.fixture
def client(db_session):
    """Create a test client for the FastAPI app"""
    # Override the database dependency
    from backend.services import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_teacher_auth(client):
    """Mock teacher authentication for tests"""
    # Override the authentication dependency
    def override_get_current_teacher():
        return "teacher-123"
    
    app.dependency_overrides[get_current_teacher] = override_get_current_teacher
    yield
    # Cleanup is handled by client fixture clearing all overrides


@pytest.fixture
def test_section(db_session) -> CourseSectionDB:
    """Create a test course section"""
    section = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-123",  # Match the mock authentication
        name="Test Section - SW 101",
        description="Test section for integration tests",
        course_code="SW101",
        term="Fall 2025",
        is_active=True,
        settings={}
    )
    db_session.add(section)
    db_session.commit()
    db_session.refresh(section)
    return section


@pytest.fixture
def test_section_other_teacher(db_session) -> CourseSectionDB:
    """Create a test course section for another teacher"""
    section = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="other-teacher-456",  # Different teacher
        name="Other Teacher Section",
        description="Section owned by another teacher",
        course_code="SW102",
        term="Fall 2025",
        is_active=True,
        settings={}
    )
    db_session.add(section)
    db_session.commit()
    db_session.refresh(section)
    return section


@pytest.fixture
def test_enrollment(db_session, test_section) -> SectionEnrollmentDB:
    """Create a test enrollment"""
    enrollment = SectionEnrollmentDB(
        id=str(uuid4()),
        section_id=test_section.id,
        student_id="student-preset-001",
        is_active=True,
        role="student"
    )
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(enrollment)
    return enrollment


@pytest.fixture
def test_inactive_enrollment(db_session, test_section) -> SectionEnrollmentDB:
    """Create a test inactive enrollment (soft deleted)"""
    enrollment = SectionEnrollmentDB(
        id=str(uuid4()),
        section_id=test_section.id,
        student_id="student-inactive-001",
        is_active=False,  # Soft deleted
        role="student"
    )
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(enrollment)
    return enrollment
