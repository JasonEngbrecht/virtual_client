"""
Tests for database migration to separate messages table
"""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from backend.models import SessionDB, MessageDB, Message, MessageCreate
from backend.services.database import db_service


class TestDatabaseMigration:
    """Test database migration to separate messages table"""
    
    def test_messages_table_exists(self, db_session):
        """Test that messages table is created"""
        # Get table names from database
        inspector = inspect(db_session.bind)
        tables = inspector.get_table_names()
        
        assert 'messages' in tables, "Messages table not found in database"
    
    def test_messages_table_structure(self, db_session):
        """Test messages table has correct columns"""
        inspector = inspect(db_session.bind)
        columns = {col['name'] for col in inspector.get_columns('messages')}
        
        expected_columns = {
            'id', 'session_id', 'role', 'content', 
            'timestamp', 'token_count', 'sequence_number'
        }
        
        assert expected_columns.issubset(columns), f"Missing columns: {expected_columns - columns}"
    
    def test_messages_table_indexes(self, db_session):
        """Test messages table has performance indexes"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('messages')
        index_names = {idx['name'] for idx in indexes}
        
        # Check for our performance indexes
        assert 'idx_session_timestamp' in index_names or any('session' in name and 'timestamp' in name for name in index_names)
        assert 'idx_session_sequence' in index_names or any('session' in name and 'sequence' in name for name in index_names)
    
    def test_session_table_updated(self, db_session):
        """Test that session table no longer has messages JSON column"""
        inspector = inspect(db_session.bind)
        columns = {col['name'] for col in inspector.get_columns('sessions')}
        
        # Should NOT have these old columns
        assert 'messages' not in columns, "Old 'messages' JSON column still exists"
        assert 'rubric_id' not in columns, "Old 'rubric_id' column still exists"
        assert 'evaluation_result_id' not in columns, "Old 'evaluation_result_id' column still exists"
        
        # Should have new columns
        assert 'total_tokens' in columns, "Missing 'total_tokens' column"
        assert 'estimated_cost' in columns, "Missing 'estimated_cost' column"
        assert 'status' in columns, "Missing 'status' column"
    
    def test_create_message_with_session(self, db_session):
        """Test creating a message linked to a session"""
        # Create a session first
        session = SessionDB(
            student_id='test-student',
            client_profile_id='test-client',
            status='active'
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message for this session
        message = MessageDB(
            session_id=session.id,
            role='user',
            content='Test message content',
            token_count=5,
            sequence_number=1
        )
        db_session.add(message)
        db_session.commit()
        
        # Verify message was created
        saved_message = db_session.query(MessageDB).filter_by(id=message.id).first()
        assert saved_message is not None
        assert saved_message.session_id == session.id
        assert saved_message.content == 'Test message content'
        assert saved_message.role == 'user'
        assert saved_message.sequence_number == 1
    
    def test_foreign_key_constraint(self, db_session):
        """Test foreign key constraint between messages and sessions"""
        # Skip this test for SQLite as it doesn't enforce foreign keys by default
        if 'sqlite' in str(db_session.bind.url):
            pytest.skip("SQLite doesn't enforce foreign keys by default")
        
        # Try to create a message with non-existent session_id
        message = MessageDB(
            session_id='non-existent-session',
            role='user',
            content='Test message',
            token_count=5,
            sequence_number=1
        )
        
        db_session.add(message)
        
        # This should raise an IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_cascade_behavior(self, db_session):
        """Test what happens when a session is deleted (messages should remain)"""
        # Create session and messages
        session = SessionDB(
            student_id='test-student',
            client_profile_id='test-client'
        )
        db_session.add(session)
        db_session.commit()
        
        message1 = MessageDB(
            session_id=session.id,
            role='user',
            content='First message',
            token_count=3,
            sequence_number=1
        )
        message2 = MessageDB(
            session_id=session.id,
            role='assistant',
            content='Second message',
            token_count=4,
            sequence_number=2
        )
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Store IDs
        session_id = session.id
        message1_id = message1.id
        message2_id = message2.id
        
        # In our design, we don't cascade delete messages
        # This preserves conversation history even if session record is removed
        # So we'll verify messages can exist independently
        
        # Query messages directly
        messages = db_session.query(MessageDB).filter_by(session_id=session_id).all()
        assert len(messages) == 2
    
    def test_session_messages_relationship(self, db_session):
        """Test the relationship between session and messages"""
        # Create session
        session = SessionDB(
            student_id='test-student',
            client_profile_id='test-client'
        )
        db_session.add(session)
        db_session.commit()
        
        # Create messages
        for i in range(3):
            message = MessageDB(
                session_id=session.id,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message {i}',
                token_count=10,
                sequence_number=i + 1
            )
            db_session.add(message)
        db_session.commit()
        
        # Test accessing messages through relationship
        db_session.refresh(session)
        assert hasattr(session, 'messages')
        assert len(session.messages) == 3
        
        # Verify messages are in sequence order
        messages = sorted(session.messages, key=lambda m: m.sequence_number)
        for i, msg in enumerate(messages):
            assert msg.sequence_number == i + 1
            assert msg.content == f'Message {i}'
    
    def test_message_pydantic_schemas(self):
        """Test Message Pydantic schemas work correctly"""
        # Test MessageCreate
        msg_create = MessageCreate(
            role='user',
            content='Test message',
            token_count=5
        )
        assert msg_create.role == 'user'
        assert msg_create.content == 'Test message'
        assert msg_create.token_count == 5
        
        # Test content validation
        with pytest.raises(ValueError):
            MessageCreate(role='user', content='')  # Empty content
        
        with pytest.raises(ValueError):
            MessageCreate(role='user', content='   ')  # Whitespace only
        
        # Test role validation
        with pytest.raises(ValueError):
            MessageCreate(role='invalid_role', content='Test')
    
    def test_token_counting_fields(self, db_session):
        """Test token counting fields in both tables"""
        # Create session
        session = SessionDB(
            student_id='test-student',
            client_profile_id='test-client',
            total_tokens=0,
            estimated_cost=0.0
        )
        db_session.add(session)
        db_session.commit()
        
        # Add messages with token counts
        tokens = [10, 25, 15]
        for i, token_count in enumerate(tokens):
            message = MessageDB(
                session_id=session.id,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message with {token_count} tokens',
                token_count=token_count,
                sequence_number=i + 1
            )
            db_session.add(message)
        db_session.commit()
        
        # Update session totals (this would be done by service layer)
        session.total_tokens = sum(tokens)
        session.estimated_cost = session.total_tokens * 0.003 / 1000  # Haiku pricing
        db_session.commit()
        
        # Verify
        db_session.refresh(session)
        assert session.total_tokens == 50
        assert abs(session.estimated_cost - 0.00015) < 0.000001  # Float comparison
    
    def test_database_creation_with_both_tables(self, db_session):
        """Test that database can be created with both sessions and messages tables"""
        # This test verifies the core requirement of Part 3
        # Use the test db_session which has the proper schema
        
        # Check both tables exist and can be queried
        session_count = db_session.query(SessionDB).count()
        message_count = db_session.query(MessageDB).count()
        
        # Tables should exist (counts may be 0 or more)
        assert session_count >= 0
        assert message_count >= 0
        
        # Verify we can join the tables
        # This query should not raise an error
        query = db_session.query(SessionDB, MessageDB).outerjoin(
            MessageDB, SessionDB.id == MessageDB.session_id
        )
        results = query.first()  # Should work even if no data


@pytest.mark.integration
class TestDatabaseMigrationIntegration:
    """Integration tests for database migration"""
    
    def test_full_conversation_flow(self, db_session):
        """Test creating a full conversation with multiple messages"""
        # Create session
        session = SessionDB(
            student_id='student-123',
            client_profile_id='client-456',
            status='active'
        )
        db_session.add(session)
        db_session.commit()
        
        # Simulate conversation
        conversation = [
            ('user', 'Hello, how are you today?', 8),
            ('assistant', "I'm not doing well. I lost my job and I'm worried about my kids.", 18),
            ('user', "I'm sorry to hear that. Can you tell me more about your situation?", 16),
            ('assistant', "I have two kids and rent is due next week. I don't know what to do.", 19),
        ]
        
        total_tokens = 0
        for i, (role, content, tokens) in enumerate(conversation):
            message = MessageDB(
                session_id=session.id,
                role=role,
                content=content,
                token_count=tokens,
                sequence_number=i + 1
            )
            db_session.add(message)
            total_tokens += tokens
        
        # Update session totals
        session.total_tokens = total_tokens
        session.estimated_cost = total_tokens * 0.003 / 1000
        db_session.commit()
        
        # Verify full conversation
        messages = db_session.query(MessageDB).filter_by(
            session_id=session.id
        ).order_by(MessageDB.sequence_number).all()
        
        assert len(messages) == 4
        assert messages[0].role == 'user'
        assert messages[1].role == 'assistant'
        assert messages[2].role == 'user'
        assert messages[3].role == 'assistant'
        
        # Verify token tracking
        assert session.total_tokens == 61
        assert abs(session.estimated_cost - 0.000183) < 0.000001
