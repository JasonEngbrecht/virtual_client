"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
import tempfile
import os

# Add backend to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Base before any models
from backend.services.database import Base, db_service

# Import all models to ensure they're registered with Base.metadata
# This MUST happen before create_all is called
from backend.models.client_profile import ClientProfileDB
from backend.models.evaluation import EvaluationDB
from backend.models.rubric import EvaluationRubricDB
from backend.models.session import SessionDB
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.models.assignment import AssignmentDB, AssignmentClientDB


# Test database URL - use in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a test database session with fresh tables"""
    # Create in-memory test engine with StaticPool for proper cleanup
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Use StaticPool for in-memory databases
        echo=False  # Set to True for SQL debugging
    )
    
    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables - models must be imported before this!
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestSessionLocal()
    
    # Override the global db_service to use our test database
    # This ensures all services use the test database
    original_engine = db_service.engine
    original_session_local = db_service.SessionLocal
    db_service.engine = engine
    db_service.SessionLocal = TestSessionLocal
    
    try:
        yield session
        session.commit()  # Commit any pending transactions
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # Restore original database service
        db_service.engine = original_engine
        db_service.SessionLocal = original_session_local
        # Drop all tables and dispose of engine
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def sample_teacher_id():
    """Sample teacher ID for testing"""
    return "teacher-123"  # Must match the mock authentication


@pytest.fixture
def sample_student_id():
    """Sample student ID for testing"""
    return "test-student-456"


@pytest.fixture
def sample_client_profile(db_session, sample_teacher_id) -> ClientProfileDB:
    """Create a sample client profile for testing"""
    client = ClientProfileDB(
        id="test-client-1",
        name="Test Client",
        age=35,
        race="Caucasian",
        gender="Female",
        socioeconomic_status="Middle class",
        issues=["anxiety", "work_stress"],
        background_story="Test background story",
        personality_traits=["anxious", "cooperative"],
        communication_style="direct",
        created_by=sample_teacher_id
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def sample_rubric(db_session, sample_teacher_id) -> EvaluationRubricDB:
    """Create a sample evaluation rubric for testing"""
    rubric = EvaluationRubricDB(
        id="test-rubric-1",
        name="Test Rubric",
        description="Test rubric description",
        criteria=[
            {
                "name": "Empathy",
                "description": "Shows empathy",
                "weight": 0.5,
                "evaluation_points": ["Active listening", "Validation"],
                "scoring_levels": {
                    "excellent": 4,
                    "good": 3,
                    "satisfactory": 2,
                    "needs_improvement": 1
                }
            },
            {
                "name": "Communication",
                "description": "Communicates effectively",
                "weight": 0.5,
                "evaluation_points": ["Clear language", "Appropriate tone"],
                "scoring_levels": {
                    "excellent": 4,
                    "good": 3,
                    "satisfactory": 2,
                    "needs_improvement": 1
                }
            }
        ],
        total_weight=1.0,
        created_by=sample_teacher_id
    )
    db_session.add(rubric)
    db_session.commit()
    db_session.refresh(rubric)
    return rubric


@pytest.fixture
def sample_session(
    db_session,
    sample_student_id,
    sample_client_profile,
    sample_rubric
) -> SessionDB:
    """Create a sample session for testing"""
    session = SessionDB(
        id="test-session-1",
        student_id=sample_student_id,
        client_profile_id=sample_client_profile.id,
        rubric_id=sample_rubric.id,
        messages=[
            {
                "role": "student",
                "content": "Hello, how are you today?",
                "timestamp": "2025-05-23T10:00:00"
            },
            {
                "role": "client",
                "content": "I'm feeling quite anxious about work.",
                "timestamp": "2025-05-23T10:00:30"
            }
        ],
        is_active=True
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "content": "I understand you're feeling anxious. Can you tell me more about what's happening at work?",
        "metadata": {
            "emotion_state": "anxious",
            "topics": ["work", "anxiety"]
        }
    }


# Marker for slow tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
