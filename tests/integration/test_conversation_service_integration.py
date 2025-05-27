"""
Integration tests for conversation service.
Tests the actual integration between services using a test database.
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

from backend.models.auth import StudentAuth
from backend.models.client_profile import ClientProfileCreate
from backend.models.session import Session as SessionModel, SessionDB
from backend.models.message import MessageDB
from backend.services.conversation_service import conversation_service
from backend.services.client_service import client_service
from backend.services.session_service import session_service


@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return ClientProfileCreate(
        name="Carlos Martinez",
        age=28,
        gender="male",
        race="Latino",
        socioeconomic_status="working_class",
        background_story="Recently lost his job at the factory. Struggling to support his family.",
        issues=["unemployment", "financial_crisis"],
        personality_traits=["anxious", "defensive"],
        communication_style="direct",
        psychological_assessment="High stress due to financial pressures.",
        triggers=["Questions about job hunting"],
        coping_mechanisms=["Exercise", "Talking to friends"],
        family_history="Married with two young children.",
        education_level="High school diploma",
        current_situation="Looking for work while wife works part-time."
    )


@pytest.fixture
def test_client(db_session: Session, sample_client_data):
    """Create a test client in the database."""
    client = client_service.create_client_for_teacher(
        db=db_session,
        client_data=sample_client_data,
        teacher_id="teacher-123"
    )
    return client


@pytest.fixture
def mock_anthropic_response(monkeypatch):
    """Mock the Anthropic API responses."""
    # Mock the anthropic service as a function that returns an instance
    mock_anthropic_instance = Mock()
    mock_anthropic_instance.generate_response.return_value = "Hi there. I'm Carlos. What do you want?"
    
    mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
    
    monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
    
    return mock_anthropic_instance


def test_start_conversation_integration(db_session: Session, test_client, mock_anthropic_response):
    """Test starting a conversation with real database operations."""
    # Arrange
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Act
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # Assert - Session was created
    assert session is not None
    assert isinstance(session, SessionModel)
    assert session.student_id == "student-789"
    assert session.client_profile_id == test_client.id
    assert session.status == "active"
    
    # Verify in database
    db_session_record = db_session.query(SessionDB).filter_by(id=session.id).first()
    assert db_session_record is not None
    assert db_session_record.student_id == "student-789"
    assert db_session_record.client_profile_id == test_client.id
    
    # Verify initial message was created
    messages = db_session.query(MessageDB).filter_by(session_id=session.id).all()
    assert len(messages) == 1
    assert messages[0].role == "assistant"
    assert messages[0].content == "Hi there. I'm Carlos. What do you want?"
    assert messages[0].sequence_number == 1
    assert messages[0].token_count > 0
    
    # Verify session token count was updated
    assert db_session_record.total_tokens > 0
    assert db_session_record.estimated_cost > 0
    
    # Verify Anthropic was called with correct system prompt
    mock_anthropic_response.generate_response.assert_called_once()
    call_args = mock_anthropic_response.generate_response.call_args
    assert "Carlos Martinez" in call_args.kwargs["system_prompt"]
    assert "28-year-old" in call_args.kwargs["system_prompt"]
    assert "unemployment" in call_args.kwargs["system_prompt"]


def test_start_conversation_client_not_found(db_session: Session):
    """Test error when trying to start conversation with non-existent client."""
    # Arrange
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id="nonexistent-client-999"
        )
    
    assert "Client with ID nonexistent-client-999 not found" in str(exc_info.value)
    
    # Verify no session was created
    sessions = db_session.query(SessionDB).all()
    assert len(sessions) == 0


def test_start_conversation_creates_unique_sessions(db_session: Session, test_client, mock_anthropic_response):
    """Test that multiple conversations create separate sessions."""
    # Arrange
    student1 = StudentAuth(id="auth-1", student_id="student-1")
    student2 = StudentAuth(id="auth-2", student_id="student-2")
    
    # Act - Start two conversations
    session1 = conversation_service.start_conversation(
        db=db_session,
        student=student1,
        client_id=test_client.id
    )
    
    session2 = conversation_service.start_conversation(
        db=db_session,
        student=student2,
        client_id=test_client.id
    )
    
    # Assert - Different sessions created
    assert session1.id != session2.id
    assert session1.student_id == "student-1"
    assert session2.student_id == "student-2"
    
    # Both should have the same client
    assert session1.client_profile_id == test_client.id
    assert session2.client_profile_id == test_client.id
    
    # Verify in database
    sessions = db_session.query(SessionDB).all()
    assert len(sessions) == 2
    
    # Each session should have one message
    messages1 = db_session.query(MessageDB).filter_by(session_id=session1.id).all()
    messages2 = db_session.query(MessageDB).filter_by(session_id=session2.id).all()
    assert len(messages1) == 1
    assert len(messages2) == 1


def test_start_conversation_with_different_client_personalities(db_session: Session, mock_anthropic_response):
    """Test that different clients generate different system prompts."""
    # Create two different clients
    anxious_client_data = ClientProfileCreate(
        name="Sarah Johnson",
        age=35,
        gender="female",
        issues=["anxiety", "grief_loss"],
        personality_traits=["anxious", "withdrawn"],
        communication_style="indirect"
    )
    
    confident_client_data = ClientProfileCreate(
        name="Mike Thompson",
        age=42,
        gender="male",
        issues=["substance_abuse"],
        personality_traits=["defensive", "confrontational"],
        communication_style="direct"
    )
    
    anxious_client = client_service.create_client_for_teacher(
        db=db_session,
        client_data=anxious_client_data,
        teacher_id="teacher-123"
    )
    
    confident_client = client_service.create_client_for_teacher(
        db=db_session,
        client_data=confident_client_data,
        teacher_id="teacher-123"
    )
    
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Start conversations with both clients
    session1 = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=anxious_client.id
    )
    
    session2 = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=confident_client.id
    )
    
    # Verify different system prompts were generated
    calls = mock_anthropic_response.generate_response.call_args_list
    assert len(calls) == 2
    
    # First call should have Sarah's personality
    prompt1 = calls[0].kwargs["system_prompt"]
    assert "Sarah Johnson" in prompt1
    assert "anxious" in prompt1.lower()
    assert "withdrawn" in prompt1.lower()
    assert "indirect" in prompt1.lower()
    
    # Second call should have Mike's personality
    prompt2 = calls[1].kwargs["system_prompt"]
    assert "Mike Thompson" in prompt2
    assert "defensive" in prompt2.lower()
    assert "confrontational" in prompt2.lower()
    assert "direct" in prompt2.lower()


def test_start_conversation_handles_anthropic_failure(db_session: Session, test_client, monkeypatch):
    """Test graceful handling of Anthropic API failures."""
    # Setup mock to fail
    mock_anthropic_instance = Mock()
    mock_anthropic_instance.generate_response.side_effect = Exception("API key invalid")
    
    mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
    
    monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
    
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id=test_client.id
        )
    
    assert "Failed to generate AI greeting" in str(exc_info.value)
    assert "API key invalid" in str(exc_info.value)
    
    # Verify session was created but no messages
    sessions = db_session.query(SessionDB).all()
    assert len(sessions) == 1  # Session created
    
    messages = db_session.query(MessageDB).all()
    assert len(messages) == 0  # But no message due to API failure


def test_send_message_integration(db_session: Session, test_client, mock_anthropic_response):
    """Test sending a message and receiving AI response."""
    # First, start a conversation
    student = StudentAuth(id="auth-456", student_id="student-789")
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # Configure mock for the second AI response
    mock_anthropic_response.generate_response.return_value = "Well, it's been really tough. I lost my job last month and we're behind on rent."
    
    # Send a message
    user_message = "I'm sorry to hear that. Can you tell me more about what happened?"
    ai_response = conversation_service.send_message(
        db=db_session,
        session_id=session.id,
        content=user_message,
        user=student
    )
    
    # Assert AI response
    assert ai_response.role == "assistant"
    assert "tough" in ai_response.content
    assert "lost my job" in ai_response.content
    
    # Verify messages in database
    messages = db_session.query(MessageDB).filter_by(session_id=session.id).order_by(MessageDB.sequence_number).all()
    assert len(messages) == 3  # Initial greeting + user message + AI response
    
    # Check message sequence
    assert messages[0].role == "assistant"  # Initial greeting
    assert messages[0].sequence_number == 1
    
    assert messages[1].role == "user"
    assert messages[1].content == user_message
    assert messages[1].sequence_number == 2
    
    assert messages[2].role == "assistant"
    assert messages[2].content == ai_response.content
    assert messages[2].sequence_number == 3
    
    # Verify session token count was updated
    db_session.refresh(db_session.query(SessionDB).filter_by(id=session.id).first())
    updated_session = db_session.query(SessionDB).filter_by(id=session.id).first()
    assert updated_session.total_tokens > session.total_tokens  # More tokens after new messages


def test_send_message_wrong_student(db_session: Session, test_client, mock_anthropic_response):
    """Test that students can't send messages to other students' sessions."""
    # Start a conversation as one student
    student1 = StudentAuth(id="auth-1", student_id="student-1")
    session = conversation_service.start_conversation(
        db=db_session,
        student=student1,
        client_id=test_client.id
    )
    
    # Try to send a message as a different student
    student2 = StudentAuth(id="auth-2", student_id="student-2")
    
    with pytest.raises(ValueError) as exc_info:
        conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content="Hello",
            user=student2
        )
    
    assert "Student student-2 does not have access to session" in str(exc_info.value)


def test_send_message_to_ended_session(db_session: Session, test_client, mock_anthropic_response):
    """Test error when trying to send message to completed session."""
    # Start and end a conversation
    student = StudentAuth(id="auth-456", student_id="student-789")
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # End the session
    conversation_service.end_conversation(
        db=db_session,
        session_id=session.id,
        user=student
    )
    
    # Try to send a message
    with pytest.raises(ValueError) as exc_info:
        conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content="One more question",
            user=student
        )
    
    assert "is not active" in str(exc_info.value)


def test_conversation_flow_integration(db_session: Session, test_client, mock_anthropic_response):
    """Test a complete conversation flow from start to end."""
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Start conversation
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    initial_tokens = session.total_tokens
    
    # Exchange multiple messages
    messages_to_send = [
        ("How are you feeling today?", "Not great. The stress is really getting to me."),
        ("What's causing the most stress?", "Bills are piling up and I can't find work."),
        ("Have you looked into any assistance programs?", "I don't even know where to start.")
    ]
    
    for user_msg, ai_response_text in messages_to_send:
        mock_anthropic_response.generate_response.return_value = ai_response_text
        
        ai_response = conversation_service.send_message(
            db=db_session,
            session_id=session.id,
            content=user_msg,
            user=student
        )
        
        assert ai_response.content == ai_response_text
    
    # End conversation with notes
    ended_session = conversation_service.end_conversation(
        db=db_session,
        session_id=session.id,
        user=student,
        session_notes="Client showing signs of financial stress. Needs resources for job assistance and financial aid."
    )
    
    # Verify final state
    assert ended_session.status == "completed"
    assert ended_session.session_notes is not None
    assert "financial stress" in ended_session.session_notes
    assert ended_session.total_tokens > initial_tokens
    assert ended_session.estimated_cost > 0
    
    # Verify all messages are in database
    messages = db_session.query(MessageDB).filter_by(session_id=session.id).all()
    assert len(messages) == 7  # 1 greeting + 3 pairs of messages
    
    # Verify conversation history formatting
    messages_list = db_session.query(MessageDB).filter_by(session_id=session.id).order_by(MessageDB.sequence_number).all()
    formatted = conversation_service._format_conversation_for_ai(
        messages_list[:-1],  # All but last
        "Final question?"
    )
    
    assert len(formatted) == 7  # 6 historical + 1 new
    assert formatted[-1]["content"] == "Final question?"
    assert formatted[-1]["role"] == "user"


def test_end_conversation_integration(db_session: Session, test_client, mock_anthropic_response):
    """Test ending a conversation updates database correctly."""
    # Start a conversation
    student = StudentAuth(id="auth-456", student_id="student-789")
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # End it
    notes = "Client was cooperative but needs follow-up for housing resources."
    ended_session = conversation_service.end_conversation(
        db=db_session,
        session_id=session.id,
        user=student,
        session_notes=notes
    )
    
    # Verify in database
    db_session_record = db_session.query(SessionDB).filter_by(id=session.id).first()
    assert db_session_record.status == "completed"
    assert db_session_record.session_notes == notes
    assert db_session_record.ended_at is not None
    assert db_session_record.ended_at > db_session_record.started_at


def test_cannot_end_already_ended_session(db_session: Session, test_client, mock_anthropic_response):
    """Test that ending an already ended session raises error."""
    # Start and end a conversation
    student = StudentAuth(id="auth-456", student_id="student-789")
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # End it once
    conversation_service.end_conversation(
        db=db_session,
        session_id=session.id,
        user=student
    )
    
    # Try to end it again
    with pytest.raises(ValueError) as exc_info:
        conversation_service.end_conversation(
            db=db_session,
            session_id=session.id,
            user=student
        )
    
    assert "already completed" in str(exc_info.value)


def test_ai_response_uses_full_context(db_session: Session, test_client, monkeypatch):
    """Test that AI responses use the full conversation context."""
    # Custom mock to verify context
    context_messages = []
    
    def capture_context(*args, **kwargs):
        context_messages.extend(kwargs.get("messages", []))
        return "I'll help you with that."
    
    mock_anthropic_instance = Mock()
    mock_anthropic_instance.generate_response.side_effect = capture_context
    mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
    
    monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
    
    student = StudentAuth(id="auth-456", student_id="student-789")
    
    # Start conversation
    session = conversation_service.start_conversation(
        db=db_session,
        student=student,
        client_id=test_client.id
    )
    
    # Clear captured messages from initial greeting
    context_messages.clear()
    
    # Send first message
    conversation_service.send_message(
        db=db_session,
        session_id=session.id,
        content="What brings you here today?",
        user=student
    )
    
    # Check context had greeting + new message
    assert len(context_messages) == 2
    assert context_messages[0]["role"] == "assistant"  # Initial greeting
    assert context_messages[1]["role"] == "user"
    assert context_messages[1]["content"] == "What brings you here today?"
    
    # Clear and send another message
    context_messages.clear()
    conversation_service.send_message(
        db=db_session,
        session_id=session.id,
        content="Can you elaborate?",
        user=student
    )
    
    # Should now have 4 messages in context (greeting, user1, ai1, user2)
    assert len(context_messages) == 4
    assert context_messages[-1]["content"] == "Can you elaborate?"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
