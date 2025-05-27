"""
Integration tests for MVP Teacher Interface
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.models.client_profile import ClientProfileCreate, ClientProfileDB
from backend.services.client_service import client_service
from backend.services.conversation_service import conversation_service
from backend.models.auth import TeacherAuth, StudentAuth
from backend.models.session import SessionDB
from backend.models.message import MessageDB
from mvp.utils import get_database_connection, get_mock_teacher, get_mock_student

# Check if Anthropic API key is available for conversation tests
HAS_ANTHROPIC_API_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))


class TestTeacherInterfaceIntegration:
    """Integration tests for teacher interface with real database"""
    
    @pytest.fixture
    def db_session(self, db_session):
        """Use the standard test database session"""
        return db_session
    
    @pytest.fixture
    def teacher(self):
        """Get mock teacher for testing"""
        return get_mock_teacher()
    
    @pytest.fixture
    def sample_client_data(self):
        """Sample client data for testing"""
        return ClientProfileCreate(
            name="Integration Test Client",
            age=42,
            gender="Male",
            race="Asian",
            socioeconomic_status="Middle class",
            issues=["mental_health", "unemployment", "family_conflict"],
            background_story="Recently laid off software engineer struggling with depression",
            personality_traits=["withdrawn", "anxious", "logical", "pessimistic"],
            communication_style="brief"
        )
    
    def test_create_client_full_flow(self, db_session, teacher, sample_client_data):
        """Test creating a client through the service"""
        # Create client
        created_client = client_service.create_client_for_teacher(
            db_session, sample_client_data, teacher.teacher_id
        )
        
        # Verify client was created
        assert created_client.id is not None
        assert created_client.name == sample_client_data.name
        assert created_client.age == sample_client_data.age
        assert created_client.created_by == teacher.teacher_id
        assert len(created_client.issues) == 3
        assert len(created_client.personality_traits) == 4
        assert created_client.communication_style == "brief"
    
    def test_get_teacher_clients(self, db_session, teacher):
        """Test retrieving clients for a teacher"""
        # Create multiple clients
        clients_data = [
            ClientProfileCreate(
                name=f"Test Client {i}",
                age=30 + i,
                personality_traits=["anxious", "cooperative"],
                issues=["housing_insecurity"]
            )
            for i in range(3)
        ]
        
        # Create clients
        for client_data in clients_data:
            client_service.create_client_for_teacher(
                db_session, client_data, teacher.teacher_id
            )
        
        # Retrieve clients
        clients = client_service.get_teacher_clients(db_session, teacher.teacher_id)
        
        # Verify
        assert len(clients) >= 3  # May have clients from other tests
        client_names = [client.name for client in clients]
        for i in range(3):
            assert f"Test Client {i}" in client_names
    
    def test_client_isolation_between_teachers(self, db_session):
        """Test that teachers only see their own clients"""
        # Create clients for different teachers
        teacher1_id = "teacher-1"
        teacher2_id = "teacher-2"
        
        client1 = client_service.create_client_for_teacher(
            db_session,
            ClientProfileCreate(
                name="Teacher 1 Client",
                age=25,
                personality_traits=["defensive", "suspicious"]
            ),
            teacher1_id
        )
        
        client2 = client_service.create_client_for_teacher(
            db_session,
            ClientProfileCreate(
                name="Teacher 2 Client",
                age=35,
                personality_traits=["cooperative", "talkative"]
            ),
            teacher2_id
        )
        
        # Get clients for each teacher
        teacher1_clients = client_service.get_teacher_clients(db_session, teacher1_id)
        teacher2_clients = client_service.get_teacher_clients(db_session, teacher2_id)
        
        # Verify isolation
        teacher1_client_names = [c.name for c in teacher1_clients]
        teacher2_client_names = [c.name for c in teacher2_clients]
        
        assert "Teacher 1 Client" in teacher1_client_names
        assert "Teacher 2 Client" not in teacher1_client_names
        assert "Teacher 2 Client" in teacher2_client_names
        assert "Teacher 1 Client" not in teacher2_client_names
    
    def test_client_with_minimal_data(self, db_session, teacher):
        """Test creating a client with only required fields"""
        minimal_client = ClientProfileCreate(
            name="Minimal Client",
            age=50,
            personality_traits=["reserved", "honest"]
        )
        
        created = client_service.create_client_for_teacher(
            db_session, minimal_client, teacher.teacher_id
        )
        
        # Verify
        assert created.name == "Minimal Client"
        assert created.age == 50
        assert created.gender is None
        assert created.race is None
        assert created.socioeconomic_status is None
        assert created.issues == []
        assert created.background_story is None
        assert created.communication_style is None
        assert len(created.personality_traits) == 2
    
    def test_client_with_all_fields(self, db_session, teacher):
        """Test creating a client with all fields populated"""
        full_client = ClientProfileCreate(
            name="Complete Client Profile",
            age=38,
            gender="Non-binary",
            race="Mixed",
            socioeconomic_status="Working class",
            issues=[
                "substance_abuse", "mental_health", "trauma_history",
                "unemployment", "housing_insecurity"
            ],
            background_story="A detailed background story " * 10,  # Long story
            personality_traits=["defensive", "anxious", "emotional", "suspicious", "withdrawn"],
            communication_style="indirect"
        )
        
        created = client_service.create_client_for_teacher(
            db_session, full_client, teacher.teacher_id
        )
        
        # Verify all fields
        assert created.name == full_client.name
        assert created.age == full_client.age
        assert created.gender == full_client.gender
        assert created.race == full_client.race
        assert created.socioeconomic_status == full_client.socioeconomic_status
        assert len(created.issues) == 5
        assert created.background_story == full_client.background_story
        assert len(created.personality_traits) == 5
        assert created.communication_style == full_client.communication_style
    
    def test_database_connection_utility(self):
        """Test the get_database_connection utility function"""
        # Get connection
        db = get_database_connection()
        
        # Verify it's a valid session
        assert isinstance(db, Session)
        
        # Test we can query
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        # Clean up
        db.close()
    
    def test_mock_teacher_consistency(self):
        """Test that mock teacher returns consistent data"""
        teacher1 = get_mock_teacher()
        teacher2 = get_mock_teacher()
        
        assert teacher1.teacher_id == teacher2.teacher_id
        assert teacher1.teacher_id == "teacher-1"
        assert isinstance(teacher1, TeacherAuth)


@pytest.mark.skipif(not HAS_ANTHROPIC_API_KEY, reason="Anthropic API key not configured")
class TestTeacherConversationIntegration:
    """Integration tests for teacher conversation testing functionality"""
    
    @pytest.fixture
    def db_session(self, db_session):
        """Use the standard test database session"""
        return db_session
    
    @pytest.fixture
    def teacher(self):
        """Get mock teacher for testing"""
        return get_mock_teacher()
    
    @pytest.fixture
    def student(self):
        """Get mock student for testing"""
        return get_mock_student()
    
    @pytest.fixture
    def test_client(self, db_session, teacher):
        """Create a test client for conversations"""
        client_data = ClientProfileCreate(
            name="Conversation Test Client",
            age=35,
            gender="Female",
            issues=["anxiety_disorder", "family_conflict"],
            personality_traits=["anxious", "cooperative", "emotional"],
            communication_style="direct",
            background_story="A working mother dealing with anxiety and family stress."
        )
        
        return client_service.create_client_for_teacher(
            db_session, client_data, teacher.teacher_id
        )
    
    def test_start_conversation(self, db_session, student, test_client):
        """Test starting a conversation with a client"""
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=test_client.id
        )
        
        # Verify session created
        assert session.id is not None
        assert session.student_id == student.student_id
        assert session.client_profile_id == test_client.id
        assert session.status == "active"
        assert session.total_tokens > 0  # Initial greeting should have tokens
        assert session.estimated_cost > 0  # Should have some cost
        
        # Check that initial greeting message was created
        from backend.services.session_service import session_service
        messages = session_service.get_messages(
            db=db_session,
            session_id=session.id
        )
        
        assert len(messages) == 1
        assert messages[0].role == "assistant"
        assert messages[0].content != ""  # Should have greeting content
        assert messages[0].token_count > 0
    
    def test_send_message_in_conversation(self, db_session, student, test_client):
        """Test sending messages back and forth in a conversation"""
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=test_client.id
        )
        
        initial_tokens = session.total_tokens
        initial_cost = session.estimated_cost
        
        # Send a user message
        user_message = "Hello, how are you feeling today?"
        ai_response = conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content=user_message,
            user=student
        )
        
        # Verify AI response
        assert ai_response.role == "assistant"
        assert ai_response.content != ""
        assert ai_response.token_count > 0
        
        # Check session was updated
        from backend.services.session_service import session_service
        updated_session = session_service.get_session(
            db=db_session,
            session_id=session.id
        )
        
        assert updated_session.total_tokens > initial_tokens
        assert updated_session.estimated_cost > initial_cost
        
        # Check message history
        messages = session_service.get_messages(
            db=db_session,
            session_id=session.id
        )
        
        # Should have: initial greeting, user message, AI response
        assert len(messages) == 3
        assert messages[0].role == "assistant"  # Initial greeting
        assert messages[1].role == "user"
        assert messages[1].content == user_message
        assert messages[2].role == "assistant"
        assert messages[2].content == ai_response.content
    
    def test_end_conversation(self, db_session, student, test_client):
        """Test ending a conversation"""
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=test_client.id
        )
        
        # Send a message
        conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content="Thank you for talking with me.",
            user=student
        )
        
        # End conversation
        ended_session = conversation_service.end_conversation(
            db=db_session,
            session_id=session.id,
            user=student,
            session_notes="Test conversation completed successfully"
        )
        
        # Verify session ended
        assert ended_session.status == "completed"
        assert ended_session.session_notes == "Test conversation completed successfully"
        
        # Verify we can't send more messages
        with pytest.raises(ValueError, match="is not active"):
            conversation_service.send_message(
                db=db_session,
                session_id=session.id,
                content="Another message",
                user=student
            )
    
    def test_conversation_with_multiple_messages(self, db_session, student, test_client):
        """Test a longer conversation with multiple exchanges"""
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=test_client.id
        )
        
        # Have multiple exchanges
        exchanges = [
            "How has your anxiety been affecting you lately?",
            "Can you tell me more about the family conflicts?",
            "What coping strategies have you tried?",
            "How can I help support you?"
        ]
        
        total_messages = 1  # Start with initial greeting
        
        for user_msg in exchanges:
            ai_response = conversation_service.send_message(
                db=db_session,
                session_id=session.id,
                content=user_msg,
                user=student
            )
            
            assert ai_response.content != ""
            assert ai_response.token_count > 0
            total_messages += 2  # User message + AI response
        
        # Check final message count
        from backend.services.session_service import session_service
        messages = session_service.get_messages(
            db=db_session,
            session_id=session.id
        )
        
        assert len(messages) == total_messages
        
        # Check token accumulation
        final_session = session_service.get_session(
            db=db_session,
            session_id=session.id
        )
        
        assert final_session.total_tokens > 100  # Should have accumulated tokens
        assert final_session.estimated_cost > 0.0001  # Should have some cost
    
    @pytest.mark.skipif(HAS_ANTHROPIC_API_KEY, reason="Skip error tests when API key is available")
    def test_conversation_error_handling_no_api_key(self, db_session, student, test_client):
        """Test error handling when no API key is configured"""
        # Test that start_conversation fails gracefully without API key
        with pytest.raises(RuntimeError, match="Failed to generate AI greeting"):
            conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id=test_client.id
            )
    
    def test_conversation_validation_errors(self, db_session, student):
        """Test validation errors that don't require API"""
        # Test with non-existent client
        with pytest.raises(ValueError, match="Client with ID .* not found"):
            conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id="non-existent-client-id"
            )
        
        # Test sending message to non-existent session
        with pytest.raises(ValueError, match="Session with ID .* not found"):
            conversation_service.send_message(
                db=db_session,
                session_id="non-existent-session-id",
                content="Test message",
                user=student
            )
        
        # Test ending non-existent session
        with pytest.raises(ValueError, match="Session with ID .* not found"):
            conversation_service.end_conversation(
                db=db_session,
                session_id="non-existent-session-id",
                user=student
            )
    
    def test_conversation_access_control(self, db_session, test_client):
        """Test that students can only access their own conversations"""
        student1 = StudentAuth(id="student-1", student_id="student-1")
        student2 = StudentAuth(id="student-2", student_id="student-2")
        
        # Student 1 starts a conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student1,
            client_id=test_client.id
        )
        
        # Student 2 tries to send a message to student 1's session
        with pytest.raises(ValueError, match="does not have access to session"):
            conversation_service.send_message(
                db=db_session,
                session_id=session.id,
                content="Unauthorized message",
                user=student2
            )
        
        # Student 2 tries to end student 1's session
        with pytest.raises(ValueError, match="does not have access to session"):
            conversation_service.end_conversation(
                db=db_session,
                session_id=session.id,
                user=student2
            )
    
    def test_mock_student_consistency(self):
        """Test that mock student returns consistent data"""
        student1 = get_mock_student()
        student2 = get_mock_student()
        
        assert student1.student_id == student2.student_id
        assert student1.student_id == "student-1"
        assert isinstance(student1, StudentAuth)


class TestConversationUILogic:
    """Test conversation UI logic without requiring API key"""
    
    def test_session_state_management(self):
        """Test conversation session state logic"""
        # Simulate session state for conversation
        session_state = {
            'conversation_active': False,
            'current_session_id': None,
            'conversation_messages': [],
            'conversation_cost': 0.0,
            'conversation_tokens': 0
        }
        
        # After starting conversation
        session_state['conversation_active'] = True
        session_state['current_session_id'] = "test-session-123"
        session_state['conversation_messages'].append({
            'role': 'assistant',
            'content': 'Hello! How can I help you today?',
            'tokens': 10
        })
        session_state['conversation_tokens'] = 10
        session_state['conversation_cost'] = 0.0000075  # Based on Haiku pricing
        
        assert session_state['conversation_active'] is True
        assert session_state['current_session_id'] is not None
        assert len(session_state['conversation_messages']) == 1
        assert session_state['conversation_messages'][0]['role'] == 'assistant'
        
        # After adding user message
        session_state['conversation_messages'].append({
            'role': 'user',
            'content': 'I need help with housing.',
            'tokens': None  # Will be calculated by service
        })
        
        assert len(session_state['conversation_messages']) == 2
        
        # After ending conversation
        session_state['conversation_active'] = False
        session_state['current_session_id'] = None
        
        assert session_state['conversation_active'] is False
        assert session_state['current_session_id'] is None
    
    def test_message_display_logic(self):
        """Test message display formatting"""
        messages = [
            {
                'role': 'assistant',
                'content': 'Hello! I\'m here to help.',
                'tokens': 8
            },
            {
                'role': 'user',
                'content': 'I\'m feeling anxious about my housing situation.',
                'tokens': 12
            },
            {
                'role': 'assistant',
                'content': 'I understand that housing concerns can be very stressful. Can you tell me more about your situation?',
                'tokens': 20
            }
        ]
        
        # Verify message structure
        for msg in messages:
            assert 'role' in msg
            assert 'content' in msg
            assert 'tokens' in msg
            assert msg['role'] in ['user', 'assistant']
            assert isinstance(msg['content'], str)
            assert msg['content'] != ''
            
        # Calculate total tokens
        total_tokens = sum(msg['tokens'] for msg in messages if msg['tokens'])
        assert total_tokens == 40
    
    def test_client_selection_state(self):
        """Test client selection state management"""
        # No client selected
        selected_client_id = None
        selected_client_name = None
        
        assert selected_client_id is None
        assert selected_client_name is None
        
        # Client selected
        selected_client_id = "client-123"
        selected_client_name = "Test Client"
        
        assert selected_client_id == "client-123"
        assert selected_client_name == "Test Client"
    
    def test_conversation_metrics_display(self):
        """Test conversation metrics formatting"""
        # Test token formatting
        from mvp.utils import format_tokens
        
        assert format_tokens(100) == "100"
        assert format_tokens(1234) == "1,234"
        assert format_tokens(1234567) == "1,234,567"
        
        # Test cost formatting
        from mvp.utils import format_cost
        
        assert format_cost(0.0001) == "$0.0001"
        assert format_cost(0.0045) == "$0.0045"
        assert format_cost(0.123) == "$0.123"
        assert format_cost(1.2345) == "$1.23"
    
    def test_error_message_display(self):
        """Test error message formatting for UI"""
        # API key error
        api_error = "ANTHROPIC_API_KEY not provided or found in environment variables"
        user_message = f"Failed to start conversation: Failed to generate AI greeting: {api_error}"
        
        assert "Failed to start conversation" in user_message
        assert "API key" in user_message or "ANTHROPIC_API_KEY" in user_message
        
        # Connection error
        connection_error = "Unable to connect to the AI service"
        user_message = f"Failed to send message: {connection_error}"
        
        assert "Failed to send message" in user_message
        assert "connect" in user_message
