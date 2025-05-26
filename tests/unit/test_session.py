"""
Unit tests for Session models
Tests model instantiation, database operations, and schema validation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.models.session import (
    SessionDB, SessionBase, SessionCreate, SessionUpdate,
    Session, SessionSummary, SendMessageRequest, EndSessionRequest
)
from backend.models.client_profile import ClientProfileDB


class TestSessionModels:
    """Test session database models"""
    
    def test_session_db_instantiation(self):
        """Test creating a SessionDB instance"""
        session = SessionDB(
            id=str(uuid4()),
            student_id="student-123",
            client_profile_id=str(uuid4()),
            status="active",
            total_tokens=0,
            estimated_cost=0.0,
            session_notes="Initial session with client"
        )
        
        assert session.student_id == "student-123"
        assert session.status == "active"
        assert session.total_tokens == 0
        assert session.estimated_cost == 0.0
        assert session.session_notes == "Initial session with client"
    
    def test_session_db_defaults(self, db_session):
        """Test SessionDB default values when saved to database"""
        # Create a client first
        client = ClientProfileDB(
            name="Test Client",
            age=25,
            created_by="teacher-123"
        )
        db_session.add(client)
        db_session.commit()
        
        # Create session with minimal data
        session = SessionDB(
            student_id="student-456",
            client_profile_id=client.id
        )
        
        # Add to database and commit to apply defaults
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        # Now check the defaults were applied
        assert session.status == "active"  # default
        assert session.total_tokens == 0  # default
        assert session.estimated_cost == 0.0  # default
        assert session.session_notes is None  # nullable
        assert session.ended_at is None  # nullable
    
    def test_session_db_in_database(self, db_session):
        """Test saving and retrieving a session from database"""
        # First create a client
        client = ClientProfileDB(
            name="Test Client",
            age=30,
            created_by="teacher-123"
        )
        db_session.add(client)
        db_session.commit()
        
        # Create session
        session_id = str(uuid4())
        session = SessionDB(
            id=session_id,
            student_id="student-789",
            client_profile_id=client.id,
            status="active",
            total_tokens=150,
            estimated_cost=0.0045,  # 150 tokens * $0.003/100 tokens (Haiku rate)
            session_notes="Practice session"
        )
        
        db_session.add(session)
        db_session.commit()
        
        # Retrieve from database
        retrieved = db_session.query(SessionDB).filter_by(id=session_id).first()
        assert retrieved is not None
        assert retrieved.student_id == "student-789"
        assert retrieved.client_profile_id == client.id
        assert retrieved.status == "active"
        assert retrieved.total_tokens == 150
        assert retrieved.estimated_cost == 0.0045
        assert retrieved.session_notes == "Practice session"
        assert retrieved.started_at is not None
        assert retrieved.created_at is not None
    
    def test_session_status_values(self, db_session):
        """Test different status values"""
        client = ClientProfileDB(
            name="Test Client",
            age=25,
            created_by="teacher-123"
        )
        db_session.add(client)
        db_session.commit()
        
        # Test active status
        session1 = SessionDB(
            student_id="student-001",
            client_profile_id=client.id,
            status="active"
        )
        db_session.add(session1)
        
        # Test completed status
        session2 = SessionDB(
            student_id="student-002",
            client_profile_id=client.id,
            status="completed",
            ended_at=datetime.utcnow()
        )
        db_session.add(session2)
        
        db_session.commit()
        
        # Verify both statuses work
        active_sessions = db_session.query(SessionDB).filter_by(status="active").all()
        completed_sessions = db_session.query(SessionDB).filter_by(status="completed").all()
        
        assert len(active_sessions) == 1
        assert len(completed_sessions) == 1
        assert active_sessions[0].status == "active"
        assert completed_sessions[0].status == "completed"
    
    def test_session_token_tracking(self, db_session):
        """Test token tracking fields"""
        client = ClientProfileDB(
            name="Test Client",
            age=35,
            created_by="teacher-123"
        )
        db_session.add(client)
        db_session.commit()
        
        session = SessionDB(
            student_id="student-100",
            client_profile_id=client.id,
            total_tokens=0,
            estimated_cost=0.0
        )
        db_session.add(session)
        db_session.commit()
        
        # Simulate adding tokens from messages
        session.total_tokens += 50  # First message
        session.total_tokens += 75  # Response
        session.total_tokens += 45  # Second message
        session.total_tokens += 80  # Response
        
        # Calculate cost (using Haiku rate: $0.003 per 100 tokens)
        session.estimated_cost = (session.total_tokens / 100) * 0.003
        
        db_session.commit()
        db_session.refresh(session)
        
        assert session.total_tokens == 250
        assert session.estimated_cost == 0.0075


class TestSessionSchemas:
    """Test Pydantic schemas for sessions"""
    
    def test_session_base_schema(self):
        """Test SessionBase schema"""
        data = {
            "student_id": "student-123",
            "client_profile_id": str(uuid4()),
            "session_notes": "Initial assessment practice"
        }
        
        schema = SessionBase(**data)
        assert schema.student_id == "student-123"
        assert schema.session_notes == "Initial assessment practice"
    
    def test_session_base_minimal(self):
        """Test SessionBase with minimal data"""
        data = {
            "student_id": "student-456",
            "client_profile_id": str(uuid4())
        }
        
        schema = SessionBase(**data)
        assert schema.student_id == "student-456"
        assert schema.session_notes is None  # optional
    
    def test_session_create_schema(self):
        """Test SessionCreate schema"""
        data = {
            "student_id": "student-789",
            "client_profile_id": str(uuid4()),
            "session_notes": "Practice with elderly client"
        }
        
        schema = SessionCreate(**data)
        assert schema.student_id == "student-789"
        assert schema.session_notes == "Practice with elderly client"
    
    def test_session_update_schema(self):
        """Test SessionUpdate schema for partial updates"""
        # Update only notes
        data1 = {"session_notes": "Updated notes after session"}
        schema1 = SessionUpdate(**data1)
        assert schema1.session_notes == "Updated notes after session"
        assert schema1.status is None
        
        # Update only status
        data2 = {"status": "completed"}
        schema2 = SessionUpdate(**data2)
        assert schema2.status == "completed"
        assert schema2.session_notes is None
        
        # Update both
        data3 = {
            "session_notes": "Final notes",
            "status": "completed"
        }
        schema3 = SessionUpdate(**data3)
        assert schema3.session_notes == "Final notes"
        assert schema3.status == "completed"
    
    def test_session_update_status_validation(self):
        """Test status field validation in SessionUpdate"""
        # Valid status values
        for status in ["active", "completed"]:
            schema = SessionUpdate(status=status)
            assert schema.status == status
        
        # Invalid status should fail
        with pytest.raises(ValueError):
            SessionUpdate(status="invalid_status")
    
    def test_session_response_schema(self):
        """Test Session response schema"""
        data = {
            "id": str(uuid4()),
            "student_id": "student-001",
            "client_profile_id": str(uuid4()),
            "started_at": datetime.utcnow(),
            "ended_at": None,
            "status": "active",
            "total_tokens": 150,
            "estimated_cost": 0.0045,
            "session_notes": "Good practice session"
        }
        
        schema = Session(**data)
        assert schema.student_id == "student-001"
        assert schema.status == "active"
        assert schema.total_tokens == 150
        assert schema.estimated_cost == 0.0045
        assert schema.ended_at is None
    
    def test_session_response_completed(self):
        """Test Session response for completed session"""
        now = datetime.utcnow()
        data = {
            "id": str(uuid4()),
            "student_id": "student-002",
            "client_profile_id": str(uuid4()),
            "started_at": now - timedelta(minutes=30),
            "ended_at": now,
            "status": "completed",
            "total_tokens": 500,
            "estimated_cost": 0.015,  # 500 tokens * $0.003/100
            "session_notes": "Completed full assessment"
        }
        
        schema = Session(**data)
        assert schema.status == "completed"
        assert schema.ended_at is not None
        assert schema.total_tokens == 500
        assert schema.estimated_cost == 0.015
    
    def test_session_summary_schema(self):
        """Test SessionSummary schema"""
        data = {
            "id": str(uuid4()),
            "student_id": "student-003",
            "client_profile_id": str(uuid4()),
            "client_name": "Maria Rodriguez",
            "started_at": datetime.utcnow(),
            "ended_at": None,
            "status": "active",
            "message_count": 6,
            "total_tokens": 250,
            "estimated_cost": 0.0075
        }
        
        schema = SessionSummary(**data)
        assert schema.client_name == "Maria Rodriguez"
        assert schema.status == "active"
        assert schema.message_count == 6
        assert schema.total_tokens == 250
        assert schema.estimated_cost == 0.0075
    
    def test_send_message_request_schema(self):
        """Test SendMessageRequest schema"""
        # Valid message
        data = {"content": "Hello, can you tell me about your situation?"}
        schema = SendMessageRequest(**data)
        assert schema.content == "Hello, can you tell me about your situation?"
        
        # Empty content should fail
        with pytest.raises(ValueError):
            SendMessageRequest(content="")
        
        # Whitespace-only content should fail
        with pytest.raises(ValueError):
            SendMessageRequest(content="   ")
    
    def test_end_session_request_schema(self):
        """Test EndSessionRequest schema"""
        # With notes
        data1 = {"session_notes": "Client was cooperative, good progress made"}
        schema1 = EndSessionRequest(**data1)
        assert schema1.session_notes == "Client was cooperative, good progress made"
        
        # Without notes
        data2 = {}
        schema2 = EndSessionRequest(**data2)
        assert schema2.session_notes is None


class TestSchemaValidation:
    """Test additional schema validation rules"""
    
    def test_session_status_validation(self):
        """Test status field validation in Session schema"""
        data = {
            "id": str(uuid4()),
            "student_id": "student-001",
            "client_profile_id": str(uuid4()),
            "started_at": datetime.utcnow()
        }
        
        # Valid status values
        for status in ["active", "completed"]:
            schema = Session(**{**data, "status": status})
            assert schema.status == status
        
        # Invalid status should fail
        with pytest.raises(ValueError):
            Session(**{**data, "status": "pending"})
    
    def test_cost_calculation_examples(self):
        """Test cost calculation scenarios"""
        # Haiku pricing: $0.003 per 100 tokens
        test_cases = [
            (100, 0.003),    # 100 tokens
            (250, 0.0075),   # 250 tokens
            (1000, 0.03),    # 1000 tokens
            (333, 0.00999),  # 333 tokens
        ]
        
        for tokens, expected_cost in test_cases:
            data = {
                "id": str(uuid4()),
                "student_id": "student-001",
                "client_profile_id": str(uuid4()),
                "started_at": datetime.utcnow(),
                "total_tokens": tokens,
                "estimated_cost": expected_cost
            }
            schema = Session(**data)
            assert schema.total_tokens == tokens
            assert abs(schema.estimated_cost - expected_cost) < 0.00001  # Float comparison
    
    def test_session_summary_defaults(self):
        """Test SessionSummary default values"""
        data = {
            "id": str(uuid4()),
            "student_id": "student-001",
            "client_profile_id": str(uuid4()),
            "started_at": datetime.utcnow(),
            "status": "active"
        }
        
        schema = SessionSummary(**data)
        assert schema.client_name is None  # optional
        assert schema.ended_at is None  # optional
        assert schema.message_count == 0  # default
        assert schema.total_tokens == 0  # default
        assert schema.estimated_cost == 0.0  # default
