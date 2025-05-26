"""
Pytest configuration for integration tests
"""

import pytest
from uuid import uuid4

# Import all models at module level to ensure they're registered with SQLAlchemy
# This must happen before any database operations
from backend.models.client_profile import ClientProfileDB
from backend.models.evaluation import EvaluationDB
from backend.models.rubric import EvaluationRubricDB
from backend.models.session import SessionDB
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.models.assignment import AssignmentDB, AssignmentClientDB


@pytest.fixture
def client(db_session):
    """Create a test client for the FastAPI app"""
    # Import here to avoid import order issues
    from fastapi.testclient import TestClient
    from backend.app import app
    from backend.services import get_db
    
    # Override the database dependency
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
    # Import here to avoid import order issues
    from backend.app import app
    from backend.api.teacher_routes import get_current_teacher
    
    # Override the authentication dependency
    def override_get_current_teacher():
        return "teacher-123"
    
    app.dependency_overrides[get_current_teacher] = override_get_current_teacher
    yield
    # Cleanup is handled by client fixture clearing all overrides


@pytest.fixture
def test_section(db_session):
    """Create a test course section"""
    # Import here to avoid import order issues
    from backend.models.course_section import CourseSectionDB
    
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
def test_section_other_teacher(db_session):
    """Create a test course section for another teacher"""
    # Import here to avoid import order issues
    from backend.models.course_section import CourseSectionDB
    
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
def test_enrollment(db_session, test_section):
    """Create a test enrollment"""
    # Import here to avoid import order issues
    from backend.models.course_section import SectionEnrollmentDB
    
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
def test_section_with_teacher(db_session):
    """Create a test course section and return teacher/section info"""
    # Import here to avoid import order issues
    from backend.models.course_section import CourseSectionDB
    
    section = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-123",  # Match the mock authentication
        name="Test Section for Assignments",
        description="Test section for assignment integration tests",
        course_code="SW201",
        term="Spring 2025",
        is_active=True,
        settings={}
    )
    db_session.add(section)
    db_session.commit()
    db_session.refresh(section)
    
    return {
        "section_id": section.id,
        "teacher_id": section.teacher_id,
        "section": section
    }


@pytest.fixture
def test_assignments(db_session, test_section_with_teacher):
    """Create test assignments for testing"""
    # Import here to avoid import order issues
    from backend.models.assignment import AssignmentDB, AssignmentType
    from datetime import datetime, timedelta
    
    assignments = []
    
    # Draft assignment
    assignment1 = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section_with_teacher["section_id"],
        title="Test Assignment 1",
        description="Draft assignment for testing",
        type=AssignmentType.PRACTICE,
        settings={"time_limit": 30},
        is_published=False,
        max_attempts=3,
        created_at=datetime.utcnow()
    )
    db_session.add(assignment1)
    assignments.append(assignment1)
    
    # Published assignment
    assignment2 = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section_with_teacher["section_id"],
        title="Test Assignment 2",
        description="Published assignment for testing",
        type=AssignmentType.GRADED,
        settings={"allow_notes": True},
        is_published=True,
        available_from=datetime.utcnow() - timedelta(days=1),
        due_date=datetime.utcnow() + timedelta(days=7),
        max_attempts=1,
        created_at=datetime.utcnow() + timedelta(seconds=1)
    )
    db_session.add(assignment2)
    assignments.append(assignment2)
    
    db_session.commit()
    for assignment in assignments:
        db_session.refresh(assignment)
    
    return assignments


@pytest.fixture
def test_assignment_other_teacher(db_session, test_section_other_teacher):
    """Create a test assignment for another teacher"""
    # Import here to avoid import order issues
    from backend.models.assignment import AssignmentDB, AssignmentType
    
    assignment = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section_other_teacher.id,
        title="Other Teacher Assignment",
        description="Assignment owned by another teacher",
        type=AssignmentType.PRACTICE,
        is_published=False
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    return assignment


@pytest.fixture
def test_inactive_enrollment(db_session, test_section):
    """Create a test inactive enrollment (soft deleted)"""
    # Import here to avoid import order issues
    from backend.models.course_section import SectionEnrollmentDB
    
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
