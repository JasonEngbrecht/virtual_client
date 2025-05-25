"""
Unit tests for RubricService
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.services.database import Base
from backend.models.session import SessionDB
from backend.services.rubric_service import RubricService, rubric_service
from backend.models.rubric import EvaluationRubricDB, EvaluationRubricCreate


def test_rubric_service_init():
    """Test that RubricService initializes correctly"""
    # Create a new instance
    service = RubricService()
    
    # Verify it's an instance of RubricService
    assert isinstance(service, RubricService)
    
    # Verify it has the correct model
    assert service.model == EvaluationRubricDB
    
    # Verify the global instance exists
    assert rubric_service is not None
    assert isinstance(rubric_service, RubricService)


def test_get_teacher_rubrics():
    """Test getting rubrics for a specific teacher"""
    # Create mock rubrics
    mock_rubrics = [
        Mock(spec=EvaluationRubricDB, id="rubric1", created_by="teacher-123"),
        Mock(spec=EvaluationRubricDB, id="rubric2", created_by="teacher-123")
    ]
    
    # Mock the get_multi method
    service = RubricService()
    with patch.object(service, 'get_multi', return_value=mock_rubrics) as mock_get_multi:
        # Call the method
        db_mock = Mock()
        result = service.get_teacher_rubrics(db_mock, "teacher-123", skip=0, limit=10)
        
        # Verify the result
        assert result == mock_rubrics
        assert len(result) == 2
        
        # Verify get_multi was called with correct parameters
        mock_get_multi.assert_called_once_with(
            db_mock,
            skip=0,
            limit=10,
            created_by="teacher-123"
        )


def test_create_rubric_for_teacher():
    """Test creating a rubric for a specific teacher"""
    # Create test rubric data
    rubric_data = EvaluationRubricCreate(
        name="Empathy Assessment",
        description="Evaluates student empathy skills",
        criteria=[
            {
                "name": "Active Listening",
                "description": "Demonstrates active listening",
                "weight": 0.5,
                "evaluation_points": ["Maintains eye contact", "Asks clarifying questions"]
            },
            {
                "name": "Emotional Response",
                "description": "Shows appropriate emotional responses",
                "weight": 0.5,
                "evaluation_points": ["Validates feelings", "Shows understanding"]
            }
        ]
    )
    
    # Create expected result
    mock_created_rubric = Mock(
        spec=EvaluationRubricDB,
        id="new-rubric-id",
        created_by="teacher-456",
        name="Empathy Assessment"
    )
    
    # Mock the create method
    service = RubricService()
    with patch.object(service, 'create', return_value=mock_created_rubric) as mock_create:
        # Call the method
        db_mock = Mock()
        result = service.create_rubric_for_teacher(db_mock, rubric_data, "teacher-456")
        
        # Verify the result
        assert result == mock_created_rubric
        assert result.created_by == "teacher-456"
        
        # Verify create was called with correct parameters
        expected_dict = rubric_data.model_dump()
        expected_dict['created_by'] = "teacher-456"
        mock_create.assert_called_once_with(db_mock, **expected_dict)


def test_can_update_rubric():
    """Test checking if a teacher can update a rubric"""
    service = RubricService()
    db_mock = Mock()
    
    # Test case 1: Teacher owns the rubric
    mock_rubric = Mock(spec=EvaluationRubricDB, created_by="teacher-123")
    with patch.object(service, 'get', return_value=mock_rubric):
        result = service.can_update(db_mock, "rubric-1", "teacher-123")
        assert result is True
    
    # Test case 2: Teacher doesn't own the rubric
    mock_rubric = Mock(spec=EvaluationRubricDB, created_by="teacher-456")
    with patch.object(service, 'get', return_value=mock_rubric):
        result = service.can_update(db_mock, "rubric-1", "teacher-123")
        assert result is False
    
    # Test case 3: Rubric doesn't exist
    with patch.object(service, 'get', return_value=None):
        result = service.can_update(db_mock, "non-existent", "teacher-123")
        assert result is False


def test_can_delete_rubric():
    """Test checking if a teacher can delete a rubric"""
    service = RubricService()
    db_mock = Mock()
    
    # Since can_delete uses can_update logic, we just need to verify it delegates correctly
    with patch.object(service, 'can_update', return_value=True) as mock_can_update:
        result = service.can_delete(db_mock, "rubric-1", "teacher-123")
        assert result is True
        mock_can_update.assert_called_once_with(db_mock, "rubric-1", "teacher-123")
    
    with patch.object(service, 'can_update', return_value=False) as mock_can_update:
        result = service.can_delete(db_mock, "rubric-1", "teacher-456")
        assert result is False
        mock_can_update.assert_called_once_with(db_mock, "rubric-1", "teacher-456")


def test_is_rubric_in_use_no_sessions():
    """Test is_rubric_in_use when rubric has no sessions"""
    service = RubricService()
    
    # Create a mock database session
    db_mock = Mock()
    
    # Mock the execute method to return 0 (no sessions using this rubric)
    mock_result = Mock()
    mock_result.scalar.return_value = 0
    db_mock.execute.return_value = mock_result
    
    # Call the method
    result = service.is_rubric_in_use(db_mock, "rubric-123")
    
    # Verify the result
    assert result is False
    
    # Verify the database was queried
    db_mock.execute.assert_called_once()


def test_is_rubric_in_use_with_sessions():
    """Test is_rubric_in_use when rubric is being used by sessions"""
    service = RubricService()
    
    # Create a mock database session
    db_mock = Mock()
    
    # Mock the execute method to return 3 (3 sessions using this rubric)
    mock_result = Mock()
    mock_result.scalar.return_value = 3
    db_mock.execute.return_value = mock_result
    
    # Call the method
    result = service.is_rubric_in_use(db_mock, "rubric-456")
    
    # Verify the result
    assert result is True
    
    # Verify the database was queried
    db_mock.execute.assert_called_once()


def test_is_rubric_in_use_integration():
    """Integration test for is_rubric_in_use with real database"""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test database session
    db = SessionLocal()
    
    try:
        service = RubricService()
        
        # Test with rubric that has no sessions
        result = service.is_rubric_in_use(db, "unused-rubric-id")
        assert result is False
        
        # Create a session that uses a rubric
        test_session = SessionDB(
            id="session-1",
            student_id="student-123",
            client_profile_id="client-123",
            rubric_id="used-rubric-id",
            messages=[]
        )
        db.add(test_session)
        db.commit()
        
        # Test with rubric that is being used
        result = service.is_rubric_in_use(db, "used-rubric-id")
        assert result is True
        
        # Test with different rubric ID
        result = service.is_rubric_in_use(db, "another-unused-rubric")
        assert result is False
        
        # Add another session with the same rubric
        test_session2 = SessionDB(
            id="session-2",
            student_id="student-456",
            client_profile_id="client-456",
            rubric_id="used-rubric-id",
            messages=[]
        )
        db.add(test_session2)
        db.commit()
        
        # Verify it still returns True (even with multiple sessions)
        result = service.is_rubric_in_use(db, "used-rubric-id")
        assert result is True
        
    finally:
        db.close()
