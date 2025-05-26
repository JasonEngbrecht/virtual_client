"""
Tests for Message Model
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.message import MessageDB, MessageCreate, Message
from backend.models.session import SessionDB
from pydantic import ValidationError


class TestMessageModel:
    """Test Message model functionality"""
    
    def test_create_message_db_instance(self, db_session: Session):
        """Test creating a MessageDB instance"""
        # First create a session for the foreign key
        session = SessionDB(
            student_id="student-123",
            client_profile_id="client-456"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message
        message = MessageDB(
            session_id=session.id,
            role="user",
            content="Hello, how are you?",
            token_count=5,
            sequence_number=1
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        # Verify fields
        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.token_count == 5
        assert message.sequence_number == 1
        assert isinstance(message.timestamp, datetime)
    
    def test_message_foreign_key_constraint(self, db_session: Session):
        """Test that message requires valid session_id"""
        # Skip this test for SQLite as it doesn't enforce foreign keys by default
        # In production (PostgreSQL), this constraint would be enforced
        if db_session.bind.dialect.name == 'sqlite':
            pytest.skip("SQLite doesn't enforce foreign keys by default")
        
        # Try to create message with non-existent session_id
        message = MessageDB(
            session_id="non-existent-session",
            role="user",
            content="Test message",
            sequence_number=1
        )
        
        db_session.add(message)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_message_relationship(self, db_session: Session):
        """Test the relationship between Message and Session"""
        # Create session
        session = SessionDB(
            student_id="student-123",
            client_profile_id="client-456"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create messages
        message1 = MessageDB(
            session_id=session.id,
            role="user",
            content="First message",
            sequence_number=1
        )
        message2 = MessageDB(
            session_id=session.id,
            role="assistant",
            content="Second message",
            sequence_number=2
        )
        
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Test relationship access
        assert message1.session.id == session.id
        assert len(session.messages) == 2
        assert session.messages[0].content == "First message"
        assert session.messages[1].content == "Second message"
    
    def test_message_pydantic_schemas(self):
        """Test Pydantic schemas for Message"""
        # Test MessageCreate
        create_data = MessageCreate(
            role="user",
            content="Test message",
            token_count=10
        )
        assert create_data.role == "user"
        assert create_data.content == "Test message"
        assert create_data.token_count == 10
        
        # Test Message (full schema)
        message_data = {
            "id": "msg-123",
            "session_id": "session-456",
            "role": "assistant",
            "content": "Response message",
            "timestamp": datetime.utcnow(),
            "token_count": 15,
            "sequence_number": 2
        }
        message = Message(**message_data)
        assert message.id == "msg-123"
        assert message.session_id == "session-456"
        assert message.role == "assistant"
        assert message.sequence_number == 2
    
    def test_message_content_validation(self):
        """Test that message content cannot be empty"""
        # Test empty string - Pydantic raises ValidationError for min_length constraint
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(role="user", content="")
        assert "at least 1 character" in str(exc_info.value)
        
        # Test whitespace only - our custom validator catches this
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            MessageCreate(role="user", content="   ")
        
        # Test valid content with whitespace (should be stripped)
        msg = MessageCreate(role="user", content="  Hello  ")
        assert msg.content == "Hello"
    
    def test_message_role_validation(self):
        """Test that role is limited to user/assistant"""
        # Valid roles
        msg1 = MessageCreate(role="user", content="Test")
        assert msg1.role == "user"
        
        msg2 = MessageCreate(role="assistant", content="Test")
        assert msg2.role == "assistant"
        
        # Invalid role should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(role="system", content="Test")
        assert "Input should be 'user' or 'assistant'" in str(exc_info.value)
    
    def test_message_defaults(self, db_session: Session):
        """Test default values for MessageDB"""
        # Create session first
        session = SessionDB(
            student_id="student-123",
            client_profile_id="client-456"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create message with minimal fields
        message = MessageDB(
            session_id=session.id,
            role="user",
            content="Test",
            sequence_number=1
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        # Check defaults
        assert message.token_count == 0  # Default value
        assert message.timestamp is not None  # Server default
        assert len(message.id) == 36  # UUID format
    
    def test_message_ordering(self, db_session: Session):
        """Test that messages can be ordered by sequence_number"""
        # Create session
        session = SessionDB(
            student_id="student-123",
            client_profile_id="client-456"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create messages out of order
        msg3 = MessageDB(
            session_id=session.id,
            role="user",
            content="Third",
            sequence_number=3
        )
        msg1 = MessageDB(
            session_id=session.id,
            role="user",
            content="First",
            sequence_number=1
        )
        msg2 = MessageDB(
            session_id=session.id,
            role="assistant",
            content="Second",
            sequence_number=2
        )
        
        db_session.add_all([msg3, msg1, msg2])
        db_session.commit()
        
        # Query messages ordered by sequence
        messages = db_session.query(MessageDB).filter(
            MessageDB.session_id == session.id
        ).order_by(MessageDB.sequence_number).all()
        
        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"
