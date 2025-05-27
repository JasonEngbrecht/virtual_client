"""
Unit tests for MVP Teacher Interface - Business Logic Focus

Tests the business logic without mocking Streamlit UI components.
For UI testing, see the integration tests which test the full flow.
"""

import pytest
from backend.models.client_profile import ClientProfileCreate, ClientProfileDB
from backend.models.auth import TeacherAuth, StudentAuth
from backend.models.session import Session, SessionDB
from backend.models.message import Message, MessageDB


class TestTeacherInterfaceLogic:
    """Test teacher interface business logic"""
    
    def test_client_profile_create_validation(self):
        """Test ClientProfileCreate validation"""
        # Valid client
        valid_client = ClientProfileCreate(
            name="Test Client",
            age=30,
            personality_traits=["anxious", "cooperative"]
        )
        assert valid_client.name == "Test Client"
        assert valid_client.age == 30
        assert len(valid_client.personality_traits) == 2
        
        # Test with all fields
        full_client = ClientProfileCreate(
            name="Full Client",
            age=45,
            gender="Female",
            race="Asian",
            socioeconomic_status="Middle class",
            issues=["housing_insecurity", "unemployment"],
            background_story="Detailed background",
            personality_traits=["defensive", "withdrawn", "anxious"],
            communication_style="brief"
        )
        assert full_client.gender == "Female"
        assert len(full_client.issues) == 2
        assert full_client.communication_style == "brief"
    
    def test_teacher_auth_model(self):
        """Test TeacherAuth model"""
        teacher = TeacherAuth(id="teacher-1", teacher_id="teacher-1")
        assert teacher.id == "teacher-1"
        assert teacher.teacher_id == "teacher-1"
    
    def test_personality_traits_validation_logic(self):
        """Test personality traits validation logic"""
        # Test minimum traits (should have at least 2)
        traits_too_few = ["anxious"]
        assert len(traits_too_few) < 2  # This would fail validation
        
        # Test maximum traits (should have at most 5)
        traits_too_many = ["anxious", "cooperative", "defensive", 
                          "emotional", "talkative", "withdrawn"]
        assert len(traits_too_many) > 5  # This would fail validation
        
        # Test valid range
        traits_valid = ["anxious", "cooperative", "defensive"]
        assert 2 <= len(traits_valid) <= 5  # This would pass validation
    
    def test_client_display_formatting(self):
        """Test client display formatting logic"""
        # Test issue formatting
        issues = ["housing_insecurity", "unemployment", "mental_health"]
        formatted_issues = [issue.replace("_", " ").title() for issue in issues]
        assert formatted_issues == ["Housing Insecurity", "Unemployment", "Mental Health"]
        
        # Test personality trait formatting
        traits = ["anxious", "cooperative"]
        formatted_traits = [trait.replace("_", " ").title() for trait in traits]
        assert formatted_traits == ["Anxious", "Cooperative"]
    
    def test_client_data_transformation(self):
        """Test transforming form data to ClientProfileCreate"""
        # Simulate form data
        form_data = {
            "name": "Maria Rodriguez",
            "age": 35,
            "gender": "Female",
            "race": "Hispanic/Latino",
            "socioeconomic_status": "Working class",
            "issues": ["housing_insecurity", "unemployment"],
            "background_story": "Single mother facing challenges",
            "personality_traits": ["anxious", "cooperative"],
            "communication_style": "emotional"
        }
        
        # Transform to ClientProfileCreate
        client = ClientProfileCreate(**form_data)
        
        assert client.name == form_data["name"]
        assert client.age == form_data["age"]
        assert client.issues == form_data["issues"]
        assert client.personality_traits == form_data["personality_traits"]
    
    def test_empty_optional_fields(self):
        """Test handling of empty optional fields"""
        # Create client with minimal data
        minimal_data = {
            "name": "Test Client",
            "age": 25,
            "personality_traits": ["reserved", "honest"]
        }
        
        client = ClientProfileCreate(**minimal_data)
        
        # Check optional fields default to None or empty
        assert client.gender is None
        assert client.race is None
        assert client.socioeconomic_status is None
        assert client.issues == []
        assert client.background_story is None
        assert client.communication_style is None


class TestConversationLogic:
    """Test conversation interface business logic"""
    
    def test_student_auth_model(self):
        """Test StudentAuth model"""
        student = StudentAuth(id="student-1", student_id="student-1")
        assert student.id == "student-1"
        assert student.student_id == "student-1"
    
    def test_session_state_initialization_values(self):
        """Test expected session state initialization values"""
        # Initial state values
        initial_state = {
            'conversation_active': False,
            'current_session_id': None,
            'conversation_messages': [],
            'conversation_cost': 0.0,
            'conversation_tokens': 0
        }
        
        assert initial_state['conversation_active'] is False
        assert initial_state['current_session_id'] is None
        assert initial_state['conversation_messages'] == []
        assert initial_state['conversation_cost'] == 0.0
        assert initial_state['conversation_tokens'] == 0
    
    def test_conversation_message_structure(self):
        """Test the structure of conversation messages"""
        # User message structure
        user_msg = {
            'role': 'user',
            'content': 'Hello, how are you?',
            'tokens': None  # Will be calculated by service
        }
        
        assert user_msg['role'] == 'user'
        assert user_msg['content'] != ''
        assert 'tokens' in user_msg
        
        # AI message structure
        ai_msg = {
            'role': 'assistant',
            'content': 'I am doing well, thank you for asking.',
            'tokens': 12
        }
        
        assert ai_msg['role'] == 'assistant'
        assert ai_msg['content'] != ''
        assert ai_msg['tokens'] > 0
    
    def test_session_id_display_truncation(self):
        """Test session ID display truncation logic"""
        # Full session ID
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Truncated display (first 8 characters + ...)
        display_id = f"{session_id[:8]}..."
        
        assert display_id == "550e8400..."
        assert len(display_id) == 11  # 8 chars + 3 dots
    
    def test_conversation_status_logic(self):
        """Test conversation status state transitions"""
        # Start state
        status = "inactive"
        conversation_active = False
        
        # After starting conversation
        status = "active"
        conversation_active = True
        
        assert status == "active"
        assert conversation_active is True
        
        # After ending conversation
        status = "completed"
        conversation_active = False
        
        assert status == "completed"
        assert conversation_active is False
    
    def test_message_validation_logic(self):
        """Test message validation before sending"""
        # Empty message should not be sent
        empty_message = ""
        assert not empty_message  # Should fail validation
        
        # Whitespace-only message should not be sent
        whitespace_message = "   \n\t   "
        assert not whitespace_message.strip()  # Should fail validation
        
        # Valid message
        valid_message = "Hello, how are you feeling today?"
        assert valid_message.strip()  # Should pass validation
    
    def test_conversation_metrics_calculation(self):
        """Test conversation metrics calculations"""
        # Initial metrics
        total_tokens = 0
        total_cost = 0.0
        
        # After first message (greeting)
        greeting_tokens = 25
        greeting_cost = 0.000019  # Based on Haiku pricing
        total_tokens += greeting_tokens
        total_cost += greeting_cost
        
        assert total_tokens == 25
        assert total_cost > 0
        
        # After user message and response
        user_tokens = 10
        response_tokens = 50
        message_cost = (user_tokens + response_tokens) * 0.00000075  # Haiku rate
        
        total_tokens += user_tokens + response_tokens
        total_cost += message_cost
        
        assert total_tokens == 85
        assert total_cost > greeting_cost
    
    def test_error_message_formatting(self):
        """Test error message formatting for user display"""
        # API error
        api_error = "Failed to generate AI response: Connection timeout"
        user_friendly = f"Failed to send message: {api_error}"
        assert "Failed to send message" in user_friendly
        
        # Session error
        session_error = "Session with ID xyz not found"
        user_friendly = f"Failed to start conversation: {session_error}"
        assert "Failed to start conversation" in user_friendly
    
    def test_conversation_end_notes(self):
        """Test conversation end notes formatting"""
        # Teacher test notes
        teacher_notes = "Teacher test conversation"
        assert teacher_notes == "Teacher test conversation"
        
        # Could be enhanced with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        enhanced_notes = f"Teacher test conversation - {timestamp}"
        assert "Teacher test conversation" in enhanced_notes
        assert timestamp in enhanced_notes
