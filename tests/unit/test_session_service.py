"""
Unit tests for Session Service
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from pytest import approx

from backend.services.session_service import SessionService, session_service
from backend.services.database import BaseCRUD
from backend.models.session import SessionDB, SessionCreate, SessionUpdate


class TestSessionServiceBasic:
    """Test basic session service functionality"""
    
    def test_session_service_instantiation(self):
        """Test that session service can be instantiated"""
        service = SessionService()
        assert service is not None
        assert isinstance(service, SessionService)
        assert isinstance(service, BaseCRUD)
    
    def test_session_service_model(self):
        """Test that session service uses correct model"""
        service = SessionService()
        assert service.model == SessionDB
    
    def test_global_session_service_instance(self):
        """Test that global instance is available"""
        assert session_service is not None
        assert isinstance(session_service, SessionService)
        assert session_service.model == SessionDB
    
    def test_inherits_base_crud_methods(self):
        """Test that session service inherits BaseCRUD methods"""
        service = SessionService()
        
        # Check that all BaseCRUD methods are available
        assert hasattr(service, 'create')
        assert hasattr(service, 'get')
        assert hasattr(service, 'get_multi')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')
        assert hasattr(service, 'count')
        assert hasattr(service, 'exists')
        assert hasattr(service, 'get_db')
        
        # Check they are callable
        assert callable(service.create)
        assert callable(service.get)
        assert callable(service.get_multi)
        assert callable(service.update)
        assert callable(service.delete)
        assert callable(service.count)
        assert callable(service.exists)


class TestSessionServiceCRUD:
    """Test session service CRUD operations"""
    
    def test_create_session_basic(self, db_session, sample_student_id, sample_client_profile):
        """Test basic session creation"""
        service = SessionService()
        
        # Create session data
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        
        # Create session
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Verify session created correctly
        assert session is not None
        assert session.student_id == sample_student_id
        assert session.client_profile_id == sample_client_profile.id
        assert session.status == 'active'
        assert session.total_tokens == 0
        assert session.estimated_cost == 0.0
        assert session.started_at is not None
        assert session.ended_at is None
    
    def test_create_session_overrides_student_id(self, db_session, sample_student_id, sample_client_profile):
        """Test that create_session enforces the authenticated student ID"""
        service = SessionService()
        
        # Try to create session with different student_id in data
        session_data = SessionCreate(
            student_id="different-student",
            client_profile_id=sample_client_profile.id
        )
        
        # Create session with authenticated student_id
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Verify it uses the authenticated student_id, not the one in data
        assert session.student_id == sample_student_id
        assert session.student_id != "different-student"
    
    def test_get_session_basic(self, db_session, sample_student_id, sample_client_profile):
        """Test basic session retrieval"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        created_session = service.create_session(db_session, session_data, sample_student_id)
        
        # Get session without student validation
        retrieved_session = service.get_session(db_session, created_session.id)
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.student_id == sample_student_id
    
    def test_get_session_with_student_validation(self, db_session, sample_student_id, sample_client_profile):
        """Test session retrieval with student validation"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        created_session = service.create_session(db_session, session_data, sample_student_id)
        
        # Get session with correct student_id
        retrieved_session = service.get_session(db_session, created_session.id, sample_student_id)
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        
        # Try to get session with wrong student_id
        wrong_session = service.get_session(db_session, created_session.id, "wrong-student")
        assert wrong_session is None
    
    def test_get_session_not_found(self, db_session):
        """Test getting non-existent session"""
        service = SessionService()
        
        session = service.get_session(db_session, "non-existent-id")
        assert session is None
        
        # With student validation
        session = service.get_session(db_session, "non-existent-id", "student-123")
        assert session is None


class TestSessionServiceBusinessLogic:
    """Test session service business logic"""
    
    def test_end_session_success(self, db_session, sample_student_id, sample_client_profile):
        """Test successfully ending a session"""
        service = SessionService()
        
        # Create an active session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # End the session
        ended_session = service.end_session(
            db_session,
            session.id,
            sample_student_id,
            "Session completed successfully"
        )
        
        # Verify session ended correctly
        assert ended_session is not None
        assert ended_session.status == 'completed'
        assert ended_session.ended_at is not None
        assert ended_session.session_notes == "Session completed successfully"
    
    def test_end_session_without_notes(self, db_session, sample_student_id, sample_client_profile):
        """Test ending a session without notes"""
        service = SessionService()
        
        # Create and end session without notes
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        ended_session = service.end_session(db_session, session.id, sample_student_id)
        
        assert ended_session is not None
        assert ended_session.status == 'completed'
        assert ended_session.ended_at is not None
        assert ended_session.session_notes is None
    
    def test_end_session_already_completed(self, db_session, sample_student_id, sample_client_profile):
        """Test that already completed sessions cannot be ended again"""
        service = SessionService()
        
        # Create and end a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        service.end_session(db_session, session.id, sample_student_id)
        
        # Try to end it again
        result = service.end_session(db_session, session.id, sample_student_id)
        assert result is None
    
    def test_end_session_wrong_student(self, db_session, sample_student_id, sample_client_profile):
        """Test that students cannot end other students' sessions"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Try to end with wrong student_id
        result = service.end_session(db_session, session.id, "wrong-student")
        assert result is None
        
        # Verify session is still active
        active_session = service.get_session(db_session, session.id)
        assert active_session.status == 'active'
    
    def test_get_student_sessions(self, db_session, sample_student_id, sample_client_profile):
        """Test getting all sessions for a student"""
        service = SessionService()
        other_student_id = "other-student-789"
        
        # Create sessions for different students
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        
        # Create 3 sessions for our student
        session1 = service.create_session(db_session, session_data, sample_student_id)
        session2 = service.create_session(db_session, session_data, sample_student_id)
        session3 = service.create_session(db_session, session_data, sample_student_id)
        
        # End one session
        service.end_session(db_session, session2.id, sample_student_id)
        
        # Create a session for another student
        other_session_data = SessionCreate(
            student_id=other_student_id,
            client_profile_id=sample_client_profile.id
        )
        service.create_session(db_session, other_session_data, other_student_id)
        
        # Get all sessions for our student
        student_sessions = service.get_student_sessions(db_session, sample_student_id)
        assert len(student_sessions) == 3
        
        # Get only active sessions
        active_sessions = service.get_student_sessions(
            db_session, 
            sample_student_id,
            status='active'
        )
        assert len(active_sessions) == 2
        
        # Get only completed sessions
        completed_sessions = service.get_student_sessions(
            db_session,
            sample_student_id,
            status='completed'
        )
        assert len(completed_sessions) == 1
        assert completed_sessions[0].id == session2.id
    
    def test_get_student_sessions_pagination(self, db_session, sample_student_id, sample_client_profile):
        """Test pagination for student sessions"""
        service = SessionService()
        
        # Create 5 sessions
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        for _ in range(5):
            service.create_session(db_session, session_data, sample_student_id)
        
        # Test pagination
        page1 = service.get_student_sessions(db_session, sample_student_id, skip=0, limit=2)
        assert len(page1) == 2
        
        page2 = service.get_student_sessions(db_session, sample_student_id, skip=2, limit=2)
        assert len(page2) == 2
        
        page3 = service.get_student_sessions(db_session, sample_student_id, skip=4, limit=2)
        assert len(page3) == 1
    
    def test_get_active_session(self, db_session, sample_student_id, sample_client_profile):
        """Test getting active session for student-client pair"""
        service = SessionService()
        
        # Initially no active session
        active = service.get_active_session(
            db_session,
            sample_student_id,
            sample_client_profile.id
        )
        assert active is None
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Now should find active session
        active = service.get_active_session(
            db_session,
            sample_student_id,
            sample_client_profile.id
        )
        assert active is not None
        assert active.id == session.id
        
        # End the session
        service.end_session(db_session, session.id, sample_student_id)
        
        # Should not find active session anymore
        active = service.get_active_session(
            db_session,
            sample_student_id,
            sample_client_profile.id
        )
        assert active is None
    
    def test_update_token_count(self, db_session, sample_student_id, sample_client_profile):
        """Test updating token count and cost"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Initial values
        assert session.total_tokens == 0
        assert session.estimated_cost == 0.0
        
        # Update tokens and cost
        updated = service.update_token_count(
            db_session,
            session.id,
            tokens_used=100,
            cost_incurred=0.003
        )
        
        assert updated is not None
        assert updated.total_tokens == 100
        assert updated.estimated_cost == approx(0.003)
        
        # Add more tokens
        updated = service.update_token_count(
            db_session,
            session.id,
            tokens_used=50,
            cost_incurred=0.0015
        )
        
        assert updated.total_tokens == 150
        assert updated.estimated_cost == approx(0.0045)
    
    def test_update_token_count_nonexistent_session(self, db_session):
        """Test updating tokens for non-existent session"""
        service = SessionService()
        
        result = service.update_token_count(
            db_session,
            "non-existent-id",
            tokens_used=100,
            cost_incurred=0.003
        )
        
        assert result is None


class TestSessionServiceEdgeCases:
    """Test edge cases and error handling"""
    
    def test_multiple_active_sessions_same_client(self, db_session, sample_student_id, sample_client_profile):
        """Test that multiple active sessions can exist for same student-client pair"""
        service = SessionService()
        
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        
        # Create multiple active sessions
        session1 = service.create_session(db_session, session_data, sample_student_id)
        session2 = service.create_session(db_session, session_data, sample_student_id)
        
        # Both should be active
        assert session1.status == 'active'
        assert session2.status == 'active'
        
        # get_active_session should return one of them (the first found)
        active = service.get_active_session(
            db_session,
            sample_student_id,
            sample_client_profile.id
        )
        assert active is not None
        assert active.id in [session1.id, session2.id]
    
    def test_session_lifecycle(self, db_session, sample_student_id, sample_client_profile):
        """Test complete session lifecycle"""
        service = SessionService()
        
        # Create session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id,
            session_notes="Initial notes"
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Verify initial state
        assert session.status == 'active'
        assert session.total_tokens == 0
        assert session.session_notes == "Initial notes"
        
        # Simulate conversation with token updates
        service.update_token_count(db_session, session.id, 50, 0.0015)
        service.update_token_count(db_session, session.id, 75, 0.00225)
        service.update_token_count(db_session, session.id, 25, 0.00075)
        
        # Get updated session
        session = service.get_session(db_session, session.id)
        assert session.total_tokens == 150
        assert session.estimated_cost == approx(0.0045)
        
        # End session
        ended = service.end_session(
            db_session,
            session.id,
            sample_student_id,
            "Final notes about the conversation"
        )
        
        assert ended.status == 'completed'
        assert ended.ended_at is not None
        assert ended.session_notes == "Final notes about the conversation"
        assert ended.total_tokens == 150
        assert ended.estimated_cost == approx(0.0045)
