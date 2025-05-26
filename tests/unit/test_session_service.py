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
from backend.models.message import MessageDB, MessageCreate, Message


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


class TestSessionServiceMessageOperations:
    """Test message operations in session service"""
    
    def test_get_next_sequence_number_empty(self, db_session, sample_student_id, sample_client_profile):
        """Test getting next sequence number for session with no messages"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # First message should get sequence number 1
        next_seq = service._get_next_sequence_number(db_session, session.id)
        assert next_seq == 1
    
    def test_get_next_sequence_number_with_messages(self, db_session, sample_student_id, sample_client_profile):
        """Test getting next sequence number with existing messages"""
        service = SessionService()
        
        # Create a session and add messages
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add some messages
        for i in range(3):
            message_data = MessageCreate(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}"
            )
            service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Next should be 4
        next_seq = service._get_next_sequence_number(db_session, session.id)
        assert next_seq == 4
    
    def test_add_message_basic(self, db_session, sample_student_id, sample_client_profile):
        """Test basic message addition"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add a user message
        message_data = MessageCreate(
            role="user",
            content="Hello, I need help with a client."
        )
        message = service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Verify message created correctly
        assert message is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello, I need help with a client."
        assert message.sequence_number == 1
        assert message.token_count == 0
        assert message.timestamp is not None
    
    def test_add_message_with_student_validation(self, db_session, sample_student_id, sample_client_profile):
        """Test that only the session owner can add messages"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Try to add message as wrong student
        message_data = MessageCreate(
            role="user",
            content="This should fail"
        )
        message = service.add_message(db_session, session.id, message_data, "wrong-student")
        
        assert message is None
        
        # Verify no messages were added
        messages = service.get_messages(db_session, session.id, sample_student_id)
        assert len(messages) == 0
    
    def test_add_message_to_completed_session(self, db_session, sample_student_id, sample_client_profile):
        """Test that messages cannot be added to completed sessions"""
        service = SessionService()
        
        # Create and end a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        service.end_session(db_session, session.id, sample_student_id)
        
        # Try to add message
        message_data = MessageCreate(
            role="user",
            content="This should fail"
        )
        message = service.add_message(db_session, session.id, message_data, sample_student_id)
        
        assert message is None
    
    def test_add_message_sequence_numbers(self, db_session, sample_student_id, sample_client_profile):
        """Test that sequence numbers increment correctly"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add multiple messages
        messages = []
        for i in range(5):
            message_data = MessageCreate(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}"
            )
            message = service.add_message(db_session, session.id, message_data, sample_student_id)
            messages.append(message)
        
        # Verify sequence numbers
        for i, message in enumerate(messages):
            assert message.sequence_number == i + 1
    
    def test_add_assistant_message_updates_tokens(self, db_session, sample_student_id, sample_client_profile):
        """Test that assistant messages update session token count and cost"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add user message (no token cost)
        user_message = MessageCreate(
            role="user",
            content="Help me with a client",
            token_count=10  # User tokens don't count toward cost
        )
        service.add_message(db_session, session.id, user_message, sample_student_id)
        
        # Verify no cost yet
        session = service.get_session(db_session, session.id)
        assert session.total_tokens == 0
        assert session.estimated_cost == 0.0
        
        # Add assistant message with tokens
        assistant_message = MessageCreate(
            role="assistant",
            content="I'd be happy to help you with your client.",
            token_count=100
        )
        service.add_message(db_session, session.id, assistant_message, sample_student_id)
        
        # Verify tokens and cost updated
        session = service.get_session(db_session, session.id)
        assert session.total_tokens == 100
        # Cost calculation: 100 tokens * (0.75 / 1_000_000) = 0.000075
        assert session.estimated_cost == approx(0.000075)
        
        # Add another assistant message
        assistant_message2 = MessageCreate(
            role="assistant",
            content="What specific challenges are you facing?",
            token_count=50
        )
        service.add_message(db_session, session.id, assistant_message2, sample_student_id)
        
        # Verify cumulative update
        session = service.get_session(db_session, session.id)
        assert session.total_tokens == 150
        assert session.estimated_cost == approx(0.000075 + 0.0000375)
    
    def test_get_messages_basic(self, db_session, sample_student_id, sample_client_profile):
        """Test basic message retrieval"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add messages
        messages_data = [
            ("user", "Hello"),
            ("assistant", "Hi there!"),
            ("user", "How are you?"),
            ("assistant", "I'm doing well, thanks!")
        ]
        
        for role, content in messages_data:
            message_data = MessageCreate(role=role, content=content)
            service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Get all messages
        messages = service.get_messages(db_session, session.id, sample_student_id)
        
        assert len(messages) == 4
        for i, (role, content) in enumerate(messages_data):
            assert messages[i].role == role
            assert messages[i].content == content
            assert messages[i].sequence_number == i + 1
    
    def test_get_messages_with_student_validation(self, db_session, sample_student_id, sample_client_profile):
        """Test that only session owner can retrieve messages"""
        service = SessionService()
        
        # Create a session and add messages
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        message_data = MessageCreate(role="user", content="Test message")
        service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Try to get messages as wrong student
        messages = service.get_messages(db_session, session.id, "wrong-student")
        assert messages is None
        
        # Get messages as correct student
        messages = service.get_messages(db_session, session.id, sample_student_id)
        assert messages is not None
        assert len(messages) == 1
    
    def test_get_messages_pagination(self, db_session, sample_student_id, sample_client_profile):
        """Test message pagination"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add 10 messages
        for i in range(10):
            message_data = MessageCreate(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}"
            )
            service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Get first page
        page1 = service.get_messages(db_session, session.id, sample_student_id, skip=0, limit=3)
        assert len(page1) == 3
        assert page1[0].content == "Message 1"
        assert page1[2].content == "Message 3"
        
        # Get second page
        page2 = service.get_messages(db_session, session.id, sample_student_id, skip=3, limit=3)
        assert len(page2) == 3
        assert page2[0].content == "Message 4"
        assert page2[2].content == "Message 6"
        
        # Get last page
        page3 = service.get_messages(db_session, session.id, sample_student_id, skip=9, limit=3)
        assert len(page3) == 1
        assert page3[0].content == "Message 10"
    
    def test_get_messages_nonexistent_session(self, db_session):
        """Test getting messages for non-existent session"""
        service = SessionService()
        
        messages = service.get_messages(db_session, "non-existent-id")
        assert messages is None
        
        messages = service.get_messages(db_session, "non-existent-id", "student-123")
        assert messages is None
    
    def test_message_ordering(self, db_session, sample_student_id, sample_client_profile):
        """Test that messages are ordered by sequence number"""
        service = SessionService()
        
        # Create a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Add messages in specific order
        messages_to_add = [
            ("user", "First message"),
            ("assistant", "Second message"),
            ("user", "Third message"),
            ("assistant", "Fourth message"),
            ("user", "Fifth message")
        ]
        
        for role, content in messages_to_add:
            message_data = MessageCreate(role=role, content=content)
            service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Retrieve messages
        messages = service.get_messages(db_session, session.id, sample_student_id)
        
        # Verify order
        assert len(messages) == 5
        for i, message in enumerate(messages):
            assert message.sequence_number == i + 1
            assert message.content == messages_to_add[i][1]
    
    def test_complete_conversation_flow(self, db_session, sample_student_id, sample_client_profile):
        """Test a complete conversation flow with messages"""
        service = SessionService()
        
        # Start a session
        session_data = SessionCreate(
            student_id=sample_student_id,
            client_profile_id=sample_client_profile.id
        )
        session = service.create_session(db_session, session_data, sample_student_id)
        
        # Simulate a conversation
        conversation = [
            ("user", "Hi, I'm working with a client who seems withdrawn.", 0),
            ("assistant", "I understand you're working with a client who appears withdrawn. Can you tell me more about their behavior?", 150),
            ("user", "They barely speak during our sessions and avoid eye contact.", 0),
            ("assistant", "That must be challenging. How long have you been working with this client, and have you noticed any patterns?", 175),
            ("user", "About 3 weeks now. They seem more withdrawn on Mondays.", 0),
            ("assistant", "Interesting observation about Mondays. Have you explored what might be happening over the weekends?", 125)
        ]
        
        for role, content, tokens in conversation:
            message_data = MessageCreate(
                role=role,
                content=content,
                token_count=tokens
            )
            service.add_message(db_session, session.id, message_data, sample_student_id)
        
        # Check final session state
        session = service.get_session(db_session, session.id)
        assert session.total_tokens == 450  # Sum of assistant tokens
        assert session.estimated_cost == approx(450 * 0.75 / 1_000_000)
        
        # Get all messages
        messages = service.get_messages(db_session, session.id, sample_student_id)
        assert len(messages) == 6
        
        # End the session
        ended = service.end_session(
            db_session,
            session.id,
            sample_student_id,
            "Good practice session discussing withdrawn client behavior"
        )
        assert ended is not None
        
        # Can still retrieve messages after session ends
        messages = service.get_messages(db_session, session.id, sample_student_id)
        assert len(messages) == 6
