"""
Minimal integration tests for MVP Teacher Interface

Following MVP testing strategy: Test happy path for core features only.
Skip edge cases, error scenarios, and comprehensive coverage.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import pytest
from sqlalchemy.orm import Session
from backend.models.client_profile import ClientProfileCreate
from backend.services.client_service import client_service
from backend.services.conversation_service import conversation_service
from mvp.utils import get_mock_teacher, get_mock_student

# Check if Anthropic API key is available
HAS_ANTHROPIC_API_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))


class TestTeacherInterfaceHappyPath:
    """Test the happy path for teacher interface features"""
    
    def test_create_and_retrieve_client(self, db_session):
        """Test that a teacher can create and view a client"""
        teacher = get_mock_teacher()
        
        # Create a client
        client_data = ClientProfileCreate(
            name="Happy Path Client",
            age=35,
            personality_traits=["anxious", "cooperative"]
        )
        
        created = client_service.create_client_for_teacher(
            db_session, client_data, teacher.teacher_id
        )
        
        # Verify it was created
        assert created.id is not None
        assert created.name == "Happy Path Client"
        
        # Verify teacher can retrieve it
        clients = client_service.get_teacher_clients(db_session, teacher.teacher_id)
        assert any(c.name == "Happy Path Client" for c in clients)
    
    @pytest.mark.skipif(not HAS_ANTHROPIC_API_KEY, reason="Anthropic API key not configured")
    def test_complete_conversation_flow(self, db_session):
        """Test a complete conversation from start to finish"""
        teacher = get_mock_teacher()
        student = get_mock_student()
        
        # Create a client
        client_data = ClientProfileCreate(
            name="Conversation Test Client",
            age=40,
            personality_traits=["defensive", "anxious"],
            issues=["housing_insecurity"]
        )
        
        client = client_service.create_client_for_teacher(
            db_session, client_data, teacher.teacher_id
        )
        
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=client.id
        )
        
        assert session.status == "active"
        assert session.total_tokens > 0
        
        # Send a message
        response = conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content="Hello, how are you today?",
            user=student
        )
        
        assert response.role == "assistant"
        assert response.content != ""
        
        # End conversation
        ended = conversation_service.end_conversation(
            db=db_session,
            session_id=session.id,
            user=student,
            session_notes="Test completed"
        )
        
        assert ended.status == "completed"


# TODO: Post-MVP tests to add:
# - Test teacher isolation (can't see other teachers' clients)
# - Test student access control (can't access others' sessions)
# - Test conversation history retrieval
# - Test metrics calculation with real data
# - Test export functionality
# - Test error handling for missing API key
# - Test rate limiting
# - Test concurrent conversations
# - Test session timeout
# - Test database connection failures
