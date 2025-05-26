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
def test_assignment_with_clients(db_session, test_section_with_teacher, sample_client_profile, sample_rubric):
    """Create a test assignment with clients already assigned"""
    # Import here to avoid import order issues
    from backend.models.assignment import AssignmentDB, AssignmentClientDB, AssignmentType
    from backend.models.client_profile import ClientProfileDB
    from backend.models.rubric import EvaluationRubricDB
    
    # Create assignment
    assignment = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section_with_teacher["section_id"],
        title="Assignment with Clients",
        description="Test assignment with pre-assigned clients",
        type=AssignmentType.PRACTICE,
        is_published=False
    )
    db_session.add(assignment)
    
    # Create additional client for testing
    client2 = ClientProfileDB(
        id=str(uuid4()),
        name="Second Test Client",
        age=45,
        race="Asian",
        gender="Male",
        socioeconomic_status="Working class",
        issues=["depression"],
        background_story="Second client background",
        personality_traits=["reserved"],
        communication_style="indirect",
        created_by="teacher-123"
    )
    db_session.add(client2)
    
    # Create additional rubric
    rubric2 = EvaluationRubricDB(
        id=str(uuid4()),
        name="Second Test Rubric",
        description="Another test rubric",
        criteria=[
            {
                "name": "Assessment",
                "description": "Assessment skills",
                "weight": 1.0,
                "evaluation_points": ["Complete assessment"],
                "scoring_levels": {"excellent": 4, "good": 3, "satisfactory": 2, "needs_improvement": 1}
            }
        ],
        total_weight=1.0,
        created_by="teacher-123"
    )
    db_session.add(rubric2)
    
    # Create assignment-client relationships
    assignment_client1 = AssignmentClientDB(
        id=str(uuid4()),
        assignment_id=assignment.id,
        client_id=sample_client_profile.id,
        rubric_id=sample_rubric.id,
        is_active=True,
        display_order=1
    )
    db_session.add(assignment_client1)
    
    assignment_client2 = AssignmentClientDB(
        id=str(uuid4()),
        assignment_id=assignment.id,
        client_id=client2.id,
        rubric_id=rubric2.id,
        is_active=True,
        display_order=2
    )
    db_session.add(assignment_client2)
    
    db_session.commit()
    db_session.refresh(assignment)
    db_session.refresh(sample_client_profile)
    db_session.refresh(client2)
    
    return assignment.id, [sample_client_profile, client2]


@pytest.fixture
def test_assignment_with_inactive_client(db_session, test_section_with_teacher, sample_client_profile, sample_rubric):
    """Create a test assignment with a soft-deleted client"""
    # Import here to avoid import order issues
    from backend.models.assignment import AssignmentDB, AssignmentClientDB, AssignmentType
    
    # Create assignment
    assignment = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section_with_teacher["section_id"],
        title="Assignment with Inactive Client",
        description="Test assignment with soft-deleted client",
        type=AssignmentType.PRACTICE,
        is_published=False
    )
    db_session.add(assignment)
    
    # Create inactive assignment-client relationship
    assignment_client = AssignmentClientDB(
        id=str(uuid4()),
        assignment_id=assignment.id,
        client_id=sample_client_profile.id,
        rubric_id=sample_rubric.id,
        is_active=False,  # Soft deleted
        display_order=1
    )
    db_session.add(assignment_client)
    
    db_session.commit()
    db_session.refresh(assignment)
    db_session.refresh(sample_client_profile)
    
    return assignment.id, sample_client_profile


@pytest.fixture
def test_client_other_teacher(db_session):
    """Create a client owned by another teacher"""
    # Import here to avoid import order issues
    from backend.models.client_profile import ClientProfileDB
    
    client = ClientProfileDB(
        id=str(uuid4()),
        name="Other Teacher's Client",
        age=30,
        race="Hispanic",
        gender="Non-binary",
        socioeconomic_status="Upper class",
        issues=["substance_abuse"],
        background_story="Client of another teacher",
        personality_traits=["defensive"],
        communication_style="assertive",
        created_by="other-teacher-456"  # Different teacher
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def test_rubric_other_teacher(db_session):
    """Create a rubric owned by another teacher"""
    # Import here to avoid import order issues
    from backend.models.rubric import EvaluationRubricDB
    
    rubric = EvaluationRubricDB(
        id=str(uuid4()),
        name="Other Teacher's Rubric",
        description="Rubric owned by another teacher",
        criteria=[
            {
                "name": "Ethics",
                "description": "Ethical considerations",
                "weight": 1.0,
                "evaluation_points": ["Maintains boundaries"],
                "scoring_levels": {"excellent": 4, "good": 3, "satisfactory": 2, "needs_improvement": 1}
            }
        ],
        total_weight=1.0,
        created_by="other-teacher-456"  # Different teacher
    )
    db_session.add(rubric)
    db_session.commit()
    db_session.refresh(rubric)
    return rubric


@pytest.fixture
def test_multiple_clients(db_session):
    """Create multiple clients for bulk operations"""
    # Import here to avoid import order issues
    from backend.models.client_profile import ClientProfileDB
    
    clients = []
    for i in range(5):
        client = ClientProfileDB(
            id=str(uuid4()),
            name=f"Bulk Test Client {i+1}",
            age=25 + i * 5,
            race="Diverse",
            gender="Various",
            socioeconomic_status="Various",
            issues=["general_counseling"],
            background_story=f"Bulk test client {i+1} background",
            personality_traits=["cooperative"],
            communication_style="varied",
            created_by="teacher-123"  # Owned by test teacher
        )
        db_session.add(client)
        clients.append(client)
    
    db_session.commit()
    for client in clients:
        db_session.refresh(client)
    
    return clients


@pytest.fixture
def test_multiple_rubrics(db_session):
    """Create multiple rubrics for bulk operations"""
    # Import here to avoid import order issues
    from backend.models.rubric import EvaluationRubricDB
    
    rubrics = []
    for i in range(5):
        rubric = EvaluationRubricDB(
            id=str(uuid4()),
            name=f"Bulk Test Rubric {i+1}",
            description=f"Bulk test rubric {i+1} description",
            criteria=[
                {
                    "name": f"Criterion {i+1}",
                    "description": f"Test criterion {i+1}",
                    "weight": 1.0,
                    "evaluation_points": [f"Point {i+1}"],
                    "scoring_levels": {"excellent": 4, "good": 3, "satisfactory": 2, "needs_improvement": 1}
                }
            ],
            total_weight=1.0,
            created_by="teacher-123"  # Owned by test teacher
        )
        db_session.add(rubric)
        rubrics.append(rubric)
    
    db_session.commit()
    for rubric in rubrics:
        db_session.refresh(rubric)
    
    return rubrics


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
