"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import tempfile
import os

# Add backend to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.database import Base, DatabaseService
from backend.models import ClientProfileDB, EvaluationRubricDB, SessionDB, EvaluationDB


# Test database URL - use in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_service():
    """Create a test database service"""
    # For file-based testing if needed
    # with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
    #     test_db_path = tmp.name
    # db_service = DatabaseService(f"sqlite:///{test_db_path}")
    
    # In-memory database for faster tests
    db_service = DatabaseService(TEST_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=db_service.engine)
    
    yield db_service
    
    # Cleanup
    Base.metadata.drop_all(bind=db_service.engine)
    
    # If using file-based database
    # if os.path.exists(test_db_path):
    #     os.unlink(test_db_path)


@pytest.fixture(scope="function")
def db_session(test_db_service) -> Generator[Session, None, None]:
    """Create a test database session"""
    with test_db_service.get_db() as session:
        yield session


@pytest.fixture
def sample_teacher_id():
    """Sample teacher ID for testing"""
    return "test-teacher-123"


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
