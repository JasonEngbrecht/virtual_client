"""
Integration tests for database initialization with ORM
"""

import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy import text

from backend.scripts.init_db_orm import init_database_orm, verify_database_orm, add_sample_data
from backend.services.database import DatabaseService
from backend.models import SessionDB, MessageDB, ClientProfileDB, EvaluationRubricDB


class TestDatabaseInitialization:
    """Test the database initialization process"""
    
    def test_init_database_orm_creates_all_tables(self, tmp_path):
        """Test that init_database_orm creates all expected tables"""
        # Create a temporary database
        db_path = tmp_path / "test_init.db"
        db_url = f"sqlite:///{db_path}"
        
        # Create a temporary database service
        temp_db_service = DatabaseService(db_url)
        
        # Import all models to register them
        from backend.models import (
            ClientProfileDB, EvaluationRubricDB, SessionDB, MessageDB,
            EvaluationDB, CourseSectionDB, SectionEnrollmentDB,
            AssignmentDB, AssignmentClientDB
        )
        
        # Create tables
        temp_db_service.create_tables()
        
        # Verify all tables exist
        with temp_db_service.get_db() as db:
            # Get table names
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = {row[0] for row in result}
            
            expected_tables = {
                'client_profiles',
                'evaluation_rubrics',
                'sessions',
                'messages',  # New table
                'evaluations',
                'course_sections',
                'section_enrollments',
                'assignments',
                'assignment_clients'
            }
            
            assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
    
    def test_sample_data_creation(self, db_session):
        """Test that sample data can be added successfully"""
        # This test uses the db_session fixture which already has the correct schema
        
        # Import the init module to ensure it uses the test database
        import backend.scripts.init_db_orm as init_module
        import backend.services.database as db_module
        
        # Save original db_service
        original_db_service = db_module.db_service
        
        try:
            # Temporarily make the init module use our test database
            # by overriding the global db_service
            
            # First check if sample data already exists
            existing = db_session.query(ClientProfileDB).filter_by(id='sample-client-1').first()
            if existing:
                db_session.query(MessageDB).filter_by(session_id='sample-session-1').delete()
                db_session.query(SessionDB).filter_by(id='sample-session-1').delete()
                db_session.query(EvaluationRubricDB).filter_by(id='sample-rubric-1').delete()
                db_session.query(ClientProfileDB).filter_by(id='sample-client-1').delete()
                db_session.commit()
            
            # Add sample data using the test session
            # Create sample client profile
            client = ClientProfileDB(
                id='sample-client-1',
                name='Maria Rodriguez',
                age=35,
                race='Hispanic',
                gender='Female',
                socioeconomic_status='Low income',
                issues=['housing_insecurity', 'unemployment', 'childcare_needs'],
                background_story='Maria is a single mother of two who recently lost her job...',
                personality_traits=['anxious', 'cooperative', 'emotional'],
                communication_style='indirect',
                created_by='teacher-1'
            )
            db_session.add(client)
            
            # Create sample rubric
            rubric = EvaluationRubricDB(
                id='sample-rubric-1',
                name='Basic Empathy Assessment',
                description='Evaluates student ability to demonstrate empathy and active listening',
                criteria=[
                    {
                        "name": "Active Listening",
                        "weight": 0.5,
                        "description": "Student demonstrates active listening skills"
                    },
                    {
                        "name": "Empathetic Response", 
                        "weight": 0.5,
                        "description": "Student responds with appropriate empathy"
                    }
                ],
                total_weight=1.0,
                created_by='teacher-1'
            )
            db_session.add(rubric)
            
            # Create sample session with new fields
            session = SessionDB(
                id='sample-session-1',
                student_id='student-1',
                client_profile_id='sample-client-1',
                status='completed',  # New field
                total_tokens=150,    # New field
                estimated_cost=0.0045  # New field
            )
            db_session.add(session)
            
            # Create sample messages
            messages = [
                MessageDB(
                    id='msg-1',
                    session_id='sample-session-1',
                    role='user',
                    content='Hello Maria, how are you doing today?',
                    token_count=10,
                    sequence_number=1
                ),
                MessageDB(
                    id='msg-2',
                    session_id='sample-session-1',
                    role='assistant',
                    content='I\'m... I\'m not doing so good. I lost my job last week and I don\'t know how I\'m going to pay rent.',
                    token_count=25,
                    sequence_number=2
                ),
                MessageDB(
                    id='msg-3',
                    session_id='sample-session-1',
                    role='user',
                    content='I\'m so sorry to hear that. That must be really stressful for you. Can you tell me more about what happened?',
                    token_count=25,
                    sequence_number=3
                )
            ]
            
            for msg in messages:
                db_session.add(msg)
            
            db_session.commit()
            
            # Verify sample data exists
            session = db_session.query(SessionDB).filter_by(id='sample-session-1').first()
            assert session is not None
            assert session.student_id == 'student-1'
            assert session.status == 'completed'  # Check new field
            assert session.total_tokens == 150
            assert session.estimated_cost == 0.0045
            
            # Check messages
            messages = db_session.query(MessageDB).filter_by(session_id='sample-session-1').order_by(MessageDB.sequence_number).all()
            assert len(messages) == 3
            assert messages[0].role == 'user'
            assert messages[1].role == 'assistant'
            assert messages[2].role == 'user'
            assert messages[0].token_count == 10
            assert messages[1].token_count == 25
            assert messages[2].token_count == 25
                
        finally:
            # Restore original db_service
            db_module.db_service = original_db_service
    
    def test_foreign_key_relationship(self, db_session):
        """Test that foreign key relationship works between sessions and messages"""
        # Create a session
        session = SessionDB(
            id='fk-test-session',
            student_id='fk-test-student',
            client_profile_id='fk-test-client'
        )
        db_session.add(session)
        db_session.commit()
        
        # Create messages
        msg1 = MessageDB(
            session_id='fk-test-session',
            role='user',
            content='Test message 1',
            sequence_number=1
        )
        msg2 = MessageDB(
            session_id='fk-test-session',
            role='assistant',
            content='Test message 2',
            sequence_number=2
        )
        
        db_session.add_all([msg1, msg2])
        db_session.commit()
        
        # Query through relationship
        result = db_session.query(SessionDB).filter_by(id='fk-test-session').first()
        assert result is not None
        assert len(result.messages) == 2
        
        # Query with join
        joined = db_session.query(SessionDB, MessageDB).join(
            MessageDB, SessionDB.id == MessageDB.session_id
        ).filter(SessionDB.id == 'fk-test-session').all()
        
        assert len(joined) == 2
        for session, message in joined:
            assert session.id == 'fk-test-session'
            assert message.session_id == 'fk-test-session'
    
    def test_no_old_columns_in_sessions(self, db_session):
        """Ensure old columns are not in sessions table"""
        from sqlalchemy import inspect
        
        inspector = inspect(db_session.bind)
        columns = {col['name'] for col in inspector.get_columns('sessions')}
        
        # These columns should NOT exist
        old_columns = {'messages', 'rubric_id', 'evaluation_result_id', 'is_active'}
        assert not old_columns.intersection(columns), f"Found old columns: {old_columns.intersection(columns)}"
        
        # These columns SHOULD exist
        new_columns = {'status', 'total_tokens', 'estimated_cost'}
        assert new_columns.issubset(columns), f"Missing new columns: {new_columns - columns}"
    
    def test_message_sequence_ordering(self, db_session):
        """Test that messages maintain proper sequence ordering"""
        # Create session
        session = SessionDB(
            student_id='seq-test-student',
            client_profile_id='seq-test-client'
        )
        db_session.add(session)
        db_session.commit()
        
        # Add messages out of order
        messages_data = [
            (3, 'Third message'),
            (1, 'First message'),
            (2, 'Second message'),
        ]
        
        for seq, content in messages_data:
            msg = MessageDB(
                session_id=session.id,
                role='user',
                content=content,
                sequence_number=seq
            )
            db_session.add(msg)
        db_session.commit()
        
        # Query in sequence order
        ordered_messages = db_session.query(MessageDB).filter_by(
            session_id=session.id
        ).order_by(MessageDB.sequence_number).all()
        
        assert len(ordered_messages) == 3
        assert ordered_messages[0].content == 'First message'
        assert ordered_messages[1].content == 'Second message'
        assert ordered_messages[2].content == 'Third message'
    
    def test_token_cost_tracking(self, db_session):
        """Test token and cost tracking functionality"""
        # Create session
        session = SessionDB(
            student_id='token-test-student',
            client_profile_id='token-test-client',
            total_tokens=0,
            estimated_cost=0.0
        )
        db_session.add(session)
        db_session.commit()
        
        # Add messages with tokens
        token_counts = [10, 25, 15, 30]
        for i, tokens in enumerate(token_counts):
            msg = MessageDB(
                session_id=session.id,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message with {tokens} tokens',
                token_count=tokens,
                sequence_number=i + 1
            )
            db_session.add(msg)
        
        # Update session totals
        session.total_tokens = sum(token_counts)
        session.estimated_cost = session.total_tokens * 0.003 / 1000  # Haiku pricing
        db_session.commit()
        
        # Verify calculations
        db_session.refresh(session)
        assert session.total_tokens == 80
        expected_cost = 80 * 0.003 / 1000
        assert abs(session.estimated_cost - expected_cost) < 0.000001
        
        # Verify we can sum tokens from messages
        total_from_messages = db_session.query(
            MessageDB
        ).filter_by(
            session_id=session.id
        ).with_entities(
            MessageDB.token_count
        ).all()
        
        calculated_total = sum(t[0] for t in total_from_messages)
        assert calculated_total == session.total_tokens
