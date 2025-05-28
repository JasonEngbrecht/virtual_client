"""
Integration test for Part 9: Polish & Integration Testing

Tests the complete workflow across all three interfaces:
1. Teacher creates a client
2. Student starts and has a conversation
3. Admin sees the metrics

This test validates that all interfaces work together properly.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.services.client_service import client_service
from backend.services.session_service import session_service
from backend.services.conversation_service import conversation_service
from backend.models.client_profile import ClientProfileCreate
from backend.models.auth import TeacherAuth, StudentAuth
from mvp.utils import get_mock_teacher, get_mock_student


class TestCompleteWorkflowIntegration:
    """Test the complete workflow across all interfaces"""
    
    def test_full_teacher_student_admin_workflow(self, db_session):
        """
        Test complete workflow:
        1. Teacher creates a client
        2. Student has a conversation with the client  
        3. Admin can see the metrics
        """
        # Step 1: Teacher creates a client (Teacher Interface)
        teacher = get_mock_teacher()
        
        # Create a test client
        client_data = ClientProfileCreate(
            name="Integration Test Client",
            age=28,
            gender="Female",
            race="Hispanic/Latino",
            socioeconomic_status="Working class",
            issues=["anxiety", "housing_instability"],
            personality_traits=["cooperative", "anxious", "resilient"],
            background_story="Test client for integration testing workflow",
            communication_style="direct"
        )
        
        # Teacher creates the client
        created_client = client_service.create_client_for_teacher(
            db=db_session,
            client_data=client_data,
            teacher_id=teacher.teacher_id
        )
        
        assert created_client is not None
        assert created_client.name == "Integration Test Client"
        assert created_client.age == 28
        assert "anxiety" in created_client.issues
        assert "cooperative" in created_client.personality_traits
        
        # Verify teacher can retrieve their clients
        teacher_clients = client_service.get_teacher_clients(
            db=db_session,
            teacher_id=teacher.teacher_id
        )
        assert len(teacher_clients) == 1
        assert teacher_clients[0].id == created_client.id
        
        # Step 2: Student starts conversation (Student Interface)
        student = get_mock_student()
        
        # Mock the Anthropic service for the conversation
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic_service:
            # Create mock anthropic instance
            mock_anthropic_instance = Mock()
            mock_anthropic_instance.generate_response.side_effect = [
                "Hello, I'm Maria. I'm here to talk about some challenges I'm facing.",  # Initial greeting
                "Thank you for asking. I've been struggling with finding stable housing lately."  # Response to student
            ]
            mock_anthropic_service.return_value = mock_anthropic_instance
            
            # Student starts conversation
            conversation_session = conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id=created_client.id
            )
            
            assert conversation_session is not None
            assert conversation_session.student_id == student.student_id
            assert conversation_session.client_profile_id == created_client.id
            assert conversation_session.status == "active"
            
            # Verify initial greeting message was created
            messages = session_service.get_messages(
                db=db_session,
                session_id=conversation_session.id
            )
            assert len(messages) == 1
            assert messages[0].role == "assistant"
            assert "Hello, I'm Maria" in messages[0].content
            
            # Student sends a message
            student_message = conversation_service.send_message(
                db=db_session,
                session_id=conversation_session.id,
                content="Hi Maria! How are you feeling today?",
                user=student
            )
            
            assert student_message is not None
            assert student_message.role == "assistant"
            assert "struggling with finding stable housing" in student_message.content
            
            # Verify all messages are stored
            all_messages = session_service.get_messages(
                db=db_session,
                session_id=conversation_session.id
            )
            assert len(all_messages) == 3  # Initial greeting + user message + AI response
            
            # Check message sequence
            assert all_messages[0].role == "assistant"  # Greeting
            assert all_messages[1].role == "user"       # Student question
            assert all_messages[2].role == "assistant"  # AI response
            
            # Student ends the conversation
            ended_session = conversation_service.end_conversation(
                db=db_session,
                session_id=conversation_session.id,
                user=student,
                session_notes="Integration test session completed"
            )
            
            assert ended_session.status == "completed"
            assert ended_session.ended_at is not None
            assert ended_session.session_notes == "Integration test session completed"
        
        # Step 3: Admin views metrics (Admin Interface)
        # Test the admin metrics functionality from admin_monitor.py
        
        # Count active sessions (should be 0 since we ended the conversation)
        active_sessions_count = session_service.count(
            db=db_session,
            status='active'
        )
        assert active_sessions_count == 0
        
        # Count total sessions
        total_sessions_count = session_service.count(db=db_session)
        assert total_sessions_count == 1
        
        # Check that session has token counts and costs
        final_session = session_service.get_session(
            db=db_session,
            session_id=conversation_session.id
        )
        assert final_session.total_tokens > 0  # Should have accumulated tokens
        assert final_session.estimated_cost > 0.0  # Should have some cost
        
        # Verify admin can get session overview
        all_sessions = session_service.get_multi(
            db=db_session,
            limit=10
        )
        assert len(all_sessions) == 1
        assert all_sessions[0].id == conversation_session.id
        assert all_sessions[0].status == "completed"
        
        # Test admin can access client information
        admin_client = client_service.get(db_session, created_client.id)
        assert admin_client is not None
        assert admin_client.name == "Integration Test Client"
    
    
    def test_cross_interface_data_consistency(self, db_session):
        """
        Test that data created in one interface is properly accessible in others
        """
        teacher = get_mock_teacher()
        student = get_mock_student()
        
        # Teacher creates client
        client_data = ClientProfileCreate(
            name="Cross Interface Test Client",
            age=35,
            personality_traits=["analytical", "reserved"],
            issues=["depression"]
        )
        
        client = client_service.create_client_for_teacher(
            db=db_session,
            client_data=client_data,
            teacher_id=teacher.teacher_id
        )
        
        # Mock conversation for student
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic_service:
            mock_anthropic_instance = Mock()
            mock_anthropic_instance.generate_response.return_value = "Hello, I'm here to talk."
            mock_anthropic_service.return_value = mock_anthropic_instance
            
            # Student can access the client
            session = conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id=client.id
            )
            
            # Admin can see the session
            admin_sessions = session_service.get_multi(db=db_session)
            assert len(admin_sessions) == 1
            assert admin_sessions[0].client_profile_id == client.id
            
            # Teacher can see their client in history
            teacher_clients = client_service.get_teacher_clients(
                db=db_session,
                teacher_id=teacher.teacher_id
            )
            assert len(teacher_clients) == 1
            assert teacher_clients[0].id == client.id
    
    
    def test_error_handling_across_interfaces(self, db_session):
        """
        Test error handling consistency across all interfaces
        """
        student = get_mock_student()
        
        # Test student trying to start conversation with non-existent client
        with pytest.raises(ValueError, match="Client with ID nonexistent not found"):
            conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id="nonexistent"
            )
        
        # Test accessing non-existent session
        non_existent_session = session_service.get_session(
            db=db_session,
            session_id="nonexistent"
        )
        assert non_existent_session is None
        
        # Test teacher accessing non-existent client
        non_existent_client = client_service.get(
            db_session,
            "nonexistent"
        )
        assert non_existent_client is None
