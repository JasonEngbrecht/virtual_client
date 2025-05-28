"""
Integration tests for student practice interface
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from mvp.student_practice import display_client_card
from backend.models.client_profile import ClientProfile, ClientProfileCreate
from backend.models.session import Session as SessionModel
from backend.services.client_service import client_service
from backend.services.session_service import session_service
from backend.services.conversation_service import conversation_service


class TestStudentInterfaceIntegration:
    """Integration tests for student practice interface"""
    
    def test_student_can_see_and_start_conversation(self, db_session: Session):
        """Test that a student can see available clients and start a conversation"""
        # Arrange - Create a test client using only valid fields
        client_data = ClientProfileCreate(
            name="Test Student Client",
            age=25,
            gender="Non-binary",
            race="Mixed",
            socioeconomic_status="Middle class",
            issues=["housing_insecurity", "financial_crisis"],
            background_story="A 25-year-old retail worker struggling with housing insecurity and financial stress. They are seeking help to find stable housing and manage their finances better.",
            personality_traits=["anxious", "cooperative"],
            communication_style="indirect"
        )
        
        # Create client for teacher-1 (our mock teacher)
        client = client_service.create_client_for_teacher(
            db_session, 
            client_data, 
            "teacher-1"
        )
        db_session.commit()
        
        # Verify client was created
        assert client.id is not None
        assert client.name == "Test Student Client"
        
        # Test getting clients as done in the interface
        teacher_clients = client_service.get_teacher_clients(db_session, "teacher-1")
        assert len(teacher_clients) > 0
        assert any(c.id == client.id for c in teacher_clients)
        
        # Test starting a conversation
        from backend.models.auth import StudentAuth
        student = StudentAuth(id="student-1", student_id="student-1")
        
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=client.id
        )
        
        assert session is not None
        assert session.student_id == "student-1"
        assert session.client_profile_id == client.id
        assert session.status == "active"
        
        # Test that active session is found
        active_sessions = session_service.get_student_sessions(
            db_session,
            "student-1",
            status="active"
        )
        
        assert len(active_sessions) > 0
        assert any(s.id == session.id for s in active_sessions)
        
        # Test getting active session for specific client
        active_session = session_service.get_active_session(
            db_session,
            "student-1",
            client.id
        )
        
        assert active_session is not None
        assert active_session.id == session.id
    
    def test_student_conversation_flow(self, db_session: Session):
        """Test the complete conversation flow in the student interface"""
        # Arrange - Create a test client
        client_data = ClientProfileCreate(
            name="Conversation Test Client",
            age=30,
            gender="Female",
            race="Hispanic/Latino",
            socioeconomic_status="Working class",
            issues=["relationship_conflict", "work_stress"],
            background_story="A 30-year-old teacher experiencing relationship conflicts and work-related stress.",
            personality_traits=["emotional", "talkative", "defensive"],
            communication_style="direct"
        )
        
        client = client_service.create_client_for_teacher(
            db_session, 
            client_data, 
            "teacher-1"
        )
        db_session.commit()
        
        # Start a conversation
        from backend.models.auth import StudentAuth
        student = StudentAuth(id="student-1", student_id="student-1")
        
        # Mock the anthropic service for the entire test
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic_service:
            # Create a mock instance
            mock_instance = MagicMock()
            mock_anthropic_service.return_value = mock_instance
            
            # Setup responses for different calls
            mock_responses = [
                # Initial greeting
                "Hi there. I'm Maria, and I... I guess I'm here because things have been really hard lately. I'm not sure where to start.",
                # Response to student's first message
                "I've been having a really tough time at work lately. My principal has been putting so much pressure on me, and I feel like nothing I do is good enough."
            ]
            mock_instance.generate_response.side_effect = mock_responses
            
            # Start conversation
            session = conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id=client.id
            )
            
            assert session is not None
            assert session.status == "active"
            
            # Get initial messages (should have AI greeting)
            messages = session_service.get_messages(db_session, session.id)
            assert len(messages) >= 1
            assert messages[0].role == "assistant"
            assert "Maria" in messages[0].content
            
            # Send a message from the student
            user_message = "Hello, I'm here to help. Can you tell me what's been bothering you?"
            
            ai_message = conversation_service.send_message(
                db=db_session,
                session_id=session.id,
                content=user_message,
                user=student
            )
            
            assert ai_message is not None
            assert ai_message.role == "assistant"
            assert "work" in ai_message.content.lower() or "principal" in ai_message.content.lower()
            
            # Verify messages are saved
            all_messages = session_service.get_messages(db_session, session.id)
            assert len(all_messages) >= 3  # Initial greeting + user message + AI response
            
            # Verify token counting and cost calculation
            updated_session = session_service.get_session(db_session, session.id)
            assert updated_session.total_tokens > 0
            assert updated_session.estimated_cost > 0
            
            # End the conversation
            ended_session = conversation_service.end_conversation(
                db=db_session,
                session_id=session.id,
                user=student,
                session_notes="Test conversation completed"
            )
            
            assert ended_session.status == "completed"
            assert ended_session.ended_at is not None
            assert ended_session.session_notes == "Test conversation completed"
            
            # Verify no active sessions remain for this client
            active_session = session_service.get_active_session(
                db_session,
                "student-1",
                client.id
            )
            assert active_session is None
