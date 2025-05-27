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
