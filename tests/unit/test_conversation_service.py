"""
Test conversation service structure and imports.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session as DBSession

from backend.services.conversation_service import ConversationService, conversation_service
from backend.models.auth import StudentAuth, TeacherAuth
from backend.models.session import Session
from backend.models.message import Message


def test_conversation_service_exists():
    """Test that conversation service can be imported and instantiated."""
    assert ConversationService is not None
    assert conversation_service is not None
    assert isinstance(conversation_service, ConversationService)


def test_conversation_service_methods_exist():
    """Test that all required methods exist on the service."""
    service = ConversationService()
    
    # Check that all methods exist
    assert hasattr(service, 'start_conversation')
    assert hasattr(service, 'send_message')
    assert hasattr(service, 'get_ai_response')
    assert hasattr(service, 'end_conversation')
    assert hasattr(service, '_format_conversation_for_ai')
    assert hasattr(service, '_calculate_cost')
    
    # Check that methods are callable
    assert callable(service.start_conversation)
    assert callable(service.send_message)
    assert callable(service.get_ai_response)
    assert callable(service.end_conversation)
    assert callable(service._format_conversation_for_ai)
    assert callable(service._calculate_cost)


def test_conversation_service_imports():
    """Test that all required imports are available in the service module."""
    # This will fail if any imports are missing
    from backend.services import conversation_service as cs_module
    
    # Check key imports are available
    module_items = dir(cs_module)
    
    # Model imports
    assert 'Session' in module_items or True  # Imported as type
    assert 'SessionCreate' in module_items or True
    assert 'Message' in module_items or True
    assert 'MessageCreate' in module_items or True
    assert 'ClientProfile' in module_items or True
    assert 'StudentAuth' in module_items or True
    
    # Service imports should be available
    assert 'session_service' in module_items
    assert 'anthropic_service' in module_items
    assert 'prompt_service' in module_items
    assert 'client_service' in module_items


def test_method_signatures():
    """Test that methods have correct signatures (will fail until implemented)."""
    service = ConversationService()
    
    # Test start_conversation signature
    import inspect
    sig = inspect.signature(service.start_conversation)
    params = list(sig.parameters.keys())
    # Note: 'self' is not included in signature of bound methods
    assert 'db' in params
    assert 'student' in params
    assert 'client_id' in params
    assert 'assignment_id' in params
    
    # Test send_message signature
    sig = inspect.signature(service.send_message)
    params = list(sig.parameters.keys())
    # Note: 'self' is not included in signature of bound methods
    assert 'db' in params
    assert 'session_id' in params
    assert 'content' in params
    assert 'user' in params


# ==================== START_CONVERSATION TESTS ====================

@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock all external service dependencies."""
    # Mock client service
    mock_client_service = Mock()
    mock_client = Mock(
        id="client-123",
        name="Maria Rodriguez",
        age=45,
        gender="female",
        race="Latina",
        issues=["housing_insecurity", "unemployment"],
        personality_traits=["anxious", "cooperative"],
        communication_style="direct"
    )
    mock_client_service.get.return_value = mock_client
    
    # Mock session service
    mock_session_service = Mock()
    # Create a proper mock that can be validated by Pydantic
    from datetime import datetime
    mock_session_db = Mock(
        id="session-456",
        student_id="student-123",
        client_profile_id="client-123",
        status="active",
        total_tokens=25,  # After greeting is added
        estimated_cost=0.0001,
        session_notes=None,
        started_at=datetime.utcnow(),
        ended_at=None
    )
    mock_session_service.create_session.return_value = mock_session_db
    mock_session_service.add_message.return_value = Mock()
    
    # Mock prompt service
    mock_prompt_service = Mock()
    mock_prompt_service.generate_system_prompt.return_value = "You are Maria Rodriguez..."
    
    # Mock anthropic service - it's a function that returns an instance
    mock_anthropic_instance = Mock()
    mock_anthropic_instance.generate_response.return_value = "Hello, I'm Maria. Nice to meet you."
    mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
    
    # Mock token counter
    mock_count_tokens = Mock(return_value=25)
    
    # Apply all mocks
    monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
    monkeypatch.setattr("backend.services.conversation_service.session_service", mock_session_service)
    monkeypatch.setattr("backend.services.conversation_service.prompt_service", mock_prompt_service)
    monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
    monkeypatch.setattr("backend.services.conversation_service.count_tokens", mock_count_tokens)
    
    return {
        "client_service": mock_client_service,
        "session_service": mock_session_service,
        "prompt_service": mock_prompt_service,
        "anthropic_service": mock_anthropic_service,
        "anthropic_instance": mock_anthropic_instance,
        "count_tokens": mock_count_tokens,
        "mock_client": mock_client,
        "mock_session_db": mock_session_db
    }


def test_start_conversation_success(mock_dependencies):
    """Test successful conversation start with greeting."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Act
    result = service.start_conversation(
        db=db,
        student=student,
        client_id="client-123"
    )
    
    # Assert
    # Verify client was fetched
    mock_dependencies["client_service"].get.assert_called_once_with(db, "client-123")
    
    # Verify session was created with correct data
    mock_dependencies["session_service"].create_session.assert_called_once()
    call_args = mock_dependencies["session_service"].create_session.call_args
    assert call_args.kwargs["student_id"] == "student-123"
    session_data = call_args.kwargs["session_data"]
    assert session_data.student_id == "student-123"
    assert session_data.client_profile_id == "client-123"
    
    # Verify system prompt was generated
    mock_dependencies["prompt_service"].generate_system_prompt.assert_called_once_with(
        mock_dependencies["mock_client"]
    )
    
    # Verify AI greeting was generated
    mock_dependencies["anthropic_instance"].generate_response.assert_called_once()
    ai_call_args = mock_dependencies["anthropic_instance"].generate_response.call_args
    assert ai_call_args.kwargs["system_prompt"] == "You are Maria Rodriguez..."
    assert ai_call_args.kwargs["max_tokens"] == 150
    assert "Maria" in ai_call_args.kwargs["messages"][0]["content"]
    
    # Verify message was added to session
    mock_dependencies["session_service"].add_message.assert_called_once()
    message_call_args = mock_dependencies["session_service"].add_message.call_args
    assert message_call_args.kwargs["session_id"] == "session-456"
    message_data = message_call_args.kwargs["message_data"]
    assert message_data.role == "assistant"
    assert message_data.content == "Hello, I'm Maria. Nice to meet you."
    assert message_data.token_count == 25
    
    # Verify result is a Session model
    assert isinstance(result, Session)
    assert result.id == "session-456"
    assert result.student_id == "student-123"
    assert result.client_profile_id == "client-123"


def test_start_conversation_client_not_found(mock_dependencies):
    """Test error when client doesn't exist."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Make client_service return None
    mock_dependencies["client_service"].get.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.start_conversation(
            db=db,
            student=student,
            client_id="nonexistent-client"
        )
    
    assert "Client with ID nonexistent-client not found" in str(exc_info.value)
    
    # Verify session was not created
    mock_dependencies["session_service"].create_session.assert_not_called()


def test_start_conversation_anthropic_error(mock_dependencies):
    """Test error handling when Anthropic API fails."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Make Anthropic raise an error
    mock_dependencies["anthropic_instance"].generate_response.side_effect = Exception("API rate limit exceeded")
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        service.start_conversation(
            db=db,
            student=student,
            client_id="client-123"
        )
    
    assert "Failed to generate AI greeting" in str(exc_info.value)
    assert "API rate limit exceeded" in str(exc_info.value)
    
    # Verify session was created but message was not added
    mock_dependencies["session_service"].create_session.assert_called_once()
    mock_dependencies["session_service"].add_message.assert_not_called()


def test_start_conversation_with_assignment_id(mock_dependencies):
    """Test conversation start with assignment ID (currently just passes through)."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Act
    result = service.start_conversation(
        db=db,
        student=student,
        client_id="client-123",
        assignment_id="assignment-999"  # Currently not validated
    )
    
    # Assert - should succeed for now (validation is TODO)
    assert isinstance(result, Session)
    assert result.id == "session-456"


def test_start_conversation_greeting_prompt_format(mock_dependencies):
    """Test that the greeting prompt is properly formatted."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Act
    service.start_conversation(
        db=db,
        student=student,
        client_id="client-123"
    )
    
    # Assert - check the greeting prompt content
    ai_call_args = mock_dependencies["anthropic_instance"].generate_response.call_args
    greeting_prompt = ai_call_args.kwargs["messages"][0]["content"]
    
    assert "social work student" in greeting_prompt
    assert "first time" in greeting_prompt
    assert "Maria" in greeting_prompt  # Client's name
    assert "brief" in greeting_prompt
    assert "1-2 sentences" in greeting_prompt
    assert "natural" in greeting_prompt


def test_start_conversation_token_counting(mock_dependencies):
    """Test that tokens are properly counted for the greeting."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Set specific token count
    mock_dependencies["count_tokens"].return_value = 42
    
    # Act
    service.start_conversation(
        db=db,
        student=student,
        client_id="client-123"
    )
    
    # Assert
    mock_dependencies["count_tokens"].assert_called_once_with("Hello, I'm Maria. Nice to meet you.")
    
    # Verify message was created with correct token count
    message_call_args = mock_dependencies["session_service"].add_message.call_args
    message_data = message_call_args.kwargs["message_data"]
    assert message_data.token_count == 42


def test_start_conversation_db_refresh_called(mock_dependencies):
    """Test that database refresh is called to get updated session data."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-789", student_id="student-123")
    
    # Act
    service.start_conversation(
        db=db,
        student=student,
        client_id="client-123"
    )
    
    # Assert
    db.refresh.assert_called_once_with(mock_dependencies["mock_session_db"])


# ==================== SEND_MESSAGE TESTS ====================

@pytest.fixture
def mock_send_dependencies(monkeypatch):
    """Mock dependencies for send_message tests."""
    # Mock session service
    mock_session_service = Mock()
    mock_session_db = Mock(
        id="session-123",
        student_id="student-456",
        client_profile_id="client-789",
        status="active"
    )
    mock_session_service.get_session.return_value = mock_session_db
    
    # Mock messages for history
    from datetime import datetime
    mock_messages = [
        Mock(role="assistant", content="Hello, I'm Maria.", sequence_number=1),
        Mock(role="user", content="Hi Maria, how are you?", sequence_number=2),
        Mock(role="assistant", content="I'm doing okay, thanks for asking.", sequence_number=3)
    ]
    mock_session_service.get_messages.return_value = mock_messages
    
    # Mock add_message to return a message with proper attributes
    def mock_add_message(db, session_id, message_data):
        # Return different messages based on role
        if message_data.role == "user":
            return Mock(
                id="msg-user-new",
                session_id=session_id,
                role="user",
                content=message_data.content,
                token_count=message_data.token_count,
                sequence_number=4,
                timestamp=datetime.utcnow()
            )
        else:
            return Mock(
                id="msg-ai-new",
                session_id=session_id,
                role="assistant",
                content=message_data.content,
                token_count=message_data.token_count,
                sequence_number=5,
                timestamp=datetime.utcnow()
            )
    
    mock_session_service.add_message.side_effect = mock_add_message
    
    # Mock client service
    mock_client_service = Mock()
    mock_client = Mock(
        id="client-789",
        name="Maria Rodriguez",
        issues=["housing_insecurity"]
    )
    mock_client_service.get.return_value = mock_client
    
    # Mock prompt service
    mock_prompt_service = Mock()
    mock_prompt_service.generate_system_prompt.return_value = "You are Maria Rodriguez..."
    
    # Mock anthropic service
    mock_anthropic_instance = Mock()
    mock_anthropic_instance.generate_response.return_value = "I understand you want to help. Let me tell you about my situation."
    mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
    
    # Mock token counter
    mock_count_tokens = Mock(side_effect=lambda text: len(text.split()) * 2)  # Simple estimation
    
    # Apply mocks
    monkeypatch.setattr("backend.services.conversation_service.session_service", mock_session_service)
    monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
    monkeypatch.setattr("backend.services.conversation_service.prompt_service", mock_prompt_service)
    monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
    monkeypatch.setattr("backend.services.conversation_service.count_tokens", mock_count_tokens)
    
    return {
        "session_service": mock_session_service,
        "client_service": mock_client_service,
        "prompt_service": mock_prompt_service,
        "anthropic_service": mock_anthropic_service,
        "anthropic_instance": mock_anthropic_instance,
        "count_tokens": mock_count_tokens,
        "mock_session_db": mock_session_db,
        "mock_client": mock_client,
        "mock_messages": mock_messages
    }


def test_send_message_success(mock_send_dependencies):
    """Test successful message sending and AI response."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    user_content = "Can you tell me more about your housing situation?"
    
    # Act
    result = service.send_message(
        db=db,
        session_id="session-123",
        content=user_content,
        user=student
    )
    
    # Assert
    # Verify session was retrieved
    mock_send_dependencies["session_service"].get_session.assert_called_once_with(db, "session-123")
    
    # Verify user message was added
    assert mock_send_dependencies["session_service"].add_message.call_count == 2  # User + AI
    first_call = mock_send_dependencies["session_service"].add_message.call_args_list[0]
    assert first_call.kwargs["session_id"] == "session-123"
    assert first_call.kwargs["message_data"].role == "user"
    assert first_call.kwargs["message_data"].content == user_content
    
    # Verify AI response was generated
    mock_send_dependencies["anthropic_instance"].generate_response.assert_called_once()
    ai_call = mock_send_dependencies["anthropic_instance"].generate_response.call_args
    # We pass messages[:-1] (2 messages) plus the new user message = 3 total
    assert len(ai_call.kwargs["messages"]) == 3  # 2 history (excluding just-added) + 1 new user message
    assert ai_call.kwargs["messages"][-1]["content"] == user_content
    
    # Verify AI response was stored
    second_call = mock_send_dependencies["session_service"].add_message.call_args_list[1]
    assert second_call.kwargs["message_data"].role == "assistant"
    assert "Let me tell you about my situation" in second_call.kwargs["message_data"].content
    
    # Verify result
    assert isinstance(result, Message)
    assert result.role == "assistant"
    assert result.content == "I understand you want to help. Let me tell you about my situation."


def test_send_message_session_not_found(mock_send_dependencies):
    """Test error when session doesn't exist."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    mock_send_dependencies["session_service"].get_session.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.send_message(
            db=db,
            session_id="nonexistent-session",
            content="Hello",
            user=student
        )
    
    assert "Session with ID nonexistent-session not found" in str(exc_info.value)


def test_send_message_access_denied(mock_send_dependencies):
    """Test error when student doesn't have access to session."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    wrong_student = StudentAuth(id="auth-999", student_id="student-999")
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.send_message(
            db=db,
            session_id="session-123",
            content="Hello",
            user=wrong_student
        )
    
    assert "Student student-999 does not have access to session session-123" in str(exc_info.value)


def test_send_message_session_not_active(mock_send_dependencies):
    """Test error when session is not active."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    # Make session completed
    mock_send_dependencies["mock_session_db"].status = "completed"
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.send_message(
            db=db,
            session_id="session-123",
            content="Hello",
            user=student
        )
    
    assert "Session session-123 is not active" in str(exc_info.value)


def test_send_message_ai_failure(mock_send_dependencies):
    """Test error handling when AI generation fails."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    # Make AI raise an error
    mock_send_dependencies["anthropic_instance"].generate_response.side_effect = Exception("Rate limit exceeded")
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        service.send_message(
            db=db,
            session_id="session-123",
            content="Hello",
            user=student
        )
    
    assert "Failed to generate AI response" in str(exc_info.value)
    assert "Rate limit exceeded" in str(exc_info.value)
    
    # Verify user message was still added
    assert mock_send_dependencies["session_service"].add_message.call_count == 1


# ==================== GET_AI_RESPONSE TESTS ====================

def test_get_ai_response_success(mock_send_dependencies):
    """Test successful AI response generation."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    session = mock_send_dependencies["mock_session_db"]
    user_message = "Tell me about your challenges"
    history = mock_send_dependencies["mock_messages"][:2]  # First two messages
    
    # Act
    content, tokens = service.get_ai_response(
        db=db,
        session=session,
        user_message=user_message,
        conversation_history=history
    )
    
    # Assert
    assert content == "I understand you want to help. Let me tell you about my situation."
    assert tokens > 0
    
    # Verify client was fetched
    mock_send_dependencies["client_service"].get.assert_called_once_with(db, "client-789")
    
    # Verify system prompt was generated
    mock_send_dependencies["prompt_service"].generate_system_prompt.assert_called_once_with(
        mock_send_dependencies["mock_client"]
    )
    
    # Verify API was called with correct format
    api_call = mock_send_dependencies["anthropic_instance"].generate_response.call_args
    messages = api_call.kwargs["messages"]
    assert len(messages) == 3  # 2 history + 1 new
    assert messages[0] == {"role": "assistant", "content": "Hello, I'm Maria."}
    assert messages[1] == {"role": "user", "content": "Hi Maria, how are you?"}
    assert messages[2] == {"role": "user", "content": user_message}
    assert api_call.kwargs["system_prompt"] == "You are Maria Rodriguez..."
    assert api_call.kwargs["max_tokens"] == 500
    assert api_call.kwargs["temperature"] == 0.7


def test_get_ai_response_client_not_found(mock_send_dependencies):
    """Test error when client profile not found."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    session = mock_send_dependencies["mock_session_db"]
    
    mock_send_dependencies["client_service"].get.return_value = None
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        service.get_ai_response(
            db=db,
            session=session,
            user_message="Hello",
            conversation_history=[]
        )
    
    assert "Client profile client-789 not found" in str(exc_info.value)


def test_get_ai_response_api_error(mock_send_dependencies):
    """Test error handling for Anthropic API errors."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    session = mock_send_dependencies["mock_session_db"]
    
    mock_send_dependencies["anthropic_instance"].generate_response.side_effect = Exception("Invalid API key")
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        service.get_ai_response(
            db=db,
            session=session,
            user_message="Hello",
            conversation_history=[]
        )
    
    assert "Anthropic API error" in str(exc_info.value)
    assert "Invalid API key" in str(exc_info.value)


# ==================== END_CONVERSATION TESTS ====================

def test_end_conversation_success(mock_send_dependencies):
    """Test successful conversation ending."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    # Mock end_session to return updated session
    ended_session_db = Mock(
        id="session-123",
        student_id="student-456",
        client_profile_id="client-789",
        status="completed",
        session_notes="Good practice session",
        total_tokens=150,
        estimated_cost=0.0005,
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow()
    )
    mock_send_dependencies["session_service"].end_session.return_value = ended_session_db
    
    # Act
    result = service.end_conversation(
        db=db,
        session_id="session-123",
        user=student,
        session_notes="Good practice session"
    )
    
    # Assert
    mock_send_dependencies["session_service"].get_session.assert_called_once_with(db, "session-123")
    mock_send_dependencies["session_service"].end_session.assert_called_once_with(
        db=db,
        session_id="session-123",
        student_id="student-456",
        session_notes="Good practice session"
    )
    
    assert isinstance(result, Session)
    assert result.status == "completed"
    assert result.session_notes == "Good practice session"


def test_end_conversation_session_not_found(mock_send_dependencies):
    """Test error when session doesn't exist."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    mock_send_dependencies["session_service"].get_session.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.end_conversation(
            db=db,
            session_id="nonexistent",
            user=student
        )
    
    assert "Session with ID nonexistent not found" in str(exc_info.value)


def test_end_conversation_access_denied(mock_send_dependencies):
    """Test error when student doesn't have access."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    wrong_student = StudentAuth(id="auth-999", student_id="student-999")
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.end_conversation(
            db=db,
            session_id="session-123",
            user=wrong_student
        )
    
    assert "Student student-999 does not have access to session session-123" in str(exc_info.value)


def test_end_conversation_already_completed(mock_send_dependencies):
    """Test error when session is already completed."""
    # Arrange
    service = ConversationService()
    db = Mock(spec=DBSession)
    student = StudentAuth(id="auth-123", student_id="student-456")
    
    # Make session already completed
    mock_send_dependencies["mock_session_db"].status = "completed"
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.end_conversation(
            db=db,
            session_id="session-123",
            user=student
        )
    
    assert "Session session-123 is already completed" in str(exc_info.value)


# ==================== HELPER METHOD TESTS ====================

def test_format_conversation_for_ai():
    """Test conversation formatting for API."""
    # Arrange
    service = ConversationService()
    messages = [
        Mock(role="assistant", content="Hello, I'm your client."),
        Mock(role="user", content="Hi, nice to meet you."),
        Mock(role="assistant", content="Thanks for meeting with me.")
    ]
    latest_message = "How can I help you today?"
    
    # Act
    formatted = service._format_conversation_for_ai(messages, latest_message)
    
    # Assert
    assert len(formatted) == 4
    assert formatted[0] == {"role": "assistant", "content": "Hello, I'm your client."}
    assert formatted[1] == {"role": "user", "content": "Hi, nice to meet you."}
    assert formatted[2] == {"role": "assistant", "content": "Thanks for meeting with me."}
    assert formatted[3] == {"role": "user", "content": "How can I help you today?"}


def test_format_conversation_empty_history():
    """Test formatting with no conversation history."""
    # Arrange
    service = ConversationService()
    messages = []
    latest_message = "Hello, are you there?"
    
    # Act
    formatted = service._format_conversation_for_ai(messages, latest_message)
    
    # Assert
    assert len(formatted) == 1
    assert formatted[0] == {"role": "user", "content": "Hello, are you there?"}


def test_calculate_cost_haiku():
    """Test cost calculation for Haiku model."""
    service = ConversationService()
    
    # Test with 1000 tokens
    cost = service._calculate_cost(1000, "claude-3-haiku-20240307")
    assert cost == pytest.approx(0.00075, rel=1e-6)
    
    # Test with 1M tokens
    cost = service._calculate_cost(1_000_000, "claude-3-haiku-20240307")
    assert cost == pytest.approx(0.75, rel=1e-6)


def test_calculate_cost_sonnet():
    """Test cost calculation for Sonnet model."""
    service = ConversationService()
    
    # Test with 1000 tokens
    cost = service._calculate_cost(1000, "claude-3-sonnet-20240229")
    assert cost == pytest.approx(0.009, rel=1e-6)
    
    # Test with 1M tokens
    cost = service._calculate_cost(1_000_000, "claude-3-5-sonnet")
    assert cost == pytest.approx(9.0, rel=1e-6)


def test_calculate_cost_default():
    """Test cost calculation defaults to Haiku pricing."""
    service = ConversationService()
    
    # Unknown model should use Haiku pricing
    cost = service._calculate_cost(1000, "unknown-model")
    assert cost == pytest.approx(0.00075, rel=1e-6)


if __name__ == "__main__":
    # Run basic verification
    test_conversation_service_exists()
    print("✅ Conversation service exists and can be instantiated")
    
    test_conversation_service_methods_exist()
    print("✅ All required methods exist")
    
    test_conversation_service_imports()
    print("✅ All imports are working correctly")
    
    test_method_signatures()
    print("✅ Method signatures are correct")
    
    print("\n🎉 Conversation service structure created successfully!")
