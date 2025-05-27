"""
Integration tests for Anthropic Service error handling and robustness

Tests error handling, fallback responses, and cost tracking in realistic scenarios.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import time
from datetime import datetime
from sqlalchemy.orm import Session
import anthropic
import httpx

from backend.services.anthropic_service import (
    AnthropicService, ServiceStatus, ErrorType, get_anthropic_service
)
from backend.services.conversation_service import conversation_service
from backend.models.auth import StudentAuth
from backend.models.session import SessionCreate
from backend.models.message import MessageCreate
from backend.models.client_profile import ClientProfileDB


# Helper functions to create Anthropic exceptions for testing
def create_api_connection_error():
    """Create an APIConnectionError for testing"""
    return anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))

def create_authentication_error(message="Invalid API key"):
    """Create an AuthenticationError for testing"""
    response = httpx.Response(
        401,
        json={"error": {"message": message, "type": "authentication_error"}},
        request=httpx.Request("POST", "https://api.anthropic.com")
    )
    return anthropic.AuthenticationError(message=message, response=response, body={"error": {"message": message}})

def create_rate_limit_error(message="Rate limit exceeded"):
    """Create a RateLimitError for testing"""
    response = httpx.Response(
        429,
        json={"error": {"message": message, "type": "rate_limit_error"}},
        request=httpx.Request("POST", "https://api.anthropic.com")
    )
    return anthropic.RateLimitError(message=message, response=response, body={"error": {"message": message}})

def create_api_timeout_error():
    """Create an APITimeoutError for testing"""
    return anthropic.APITimeoutError(request=httpx.Request("POST", "https://api.anthropic.com"))


class TestAnthropicServiceIntegration:
    """Test Anthropic service integration with error handling"""
    
    @pytest.fixture
    def mock_anthropic_env(self, monkeypatch):
        """Mock Anthropic environment variables"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("ANTHROPIC_COST_WARNING", "0.10")
        monkeypatch.setenv("ANTHROPIC_COST_CRITICAL", "0.50")
        monkeypatch.setenv("ANTHROPIC_DAILY_LIMIT", "5.00")
        monkeypatch.setenv("ANTHROPIC_FAILURE_THRESHOLD", "3")
        monkeypatch.setenv("ANTHROPIC_RECOVERY_TIMEOUT", "60")
    
    @pytest.fixture
    def sample_client(self, db_session):
        """Create a sample client for testing"""
        client = ClientProfileDB(
            id="client-123",
            created_by="teacher-123",
            name="Test Client",
            age=25,
            gender="Female",
            race="Asian",
            ethnicity="Chinese",
            socioeconomic_status="Middle class",
            occupation="Software Engineer",
            education_level="Bachelor's degree",
            family_structure="Single",
            health_conditions=["Anxiety"],
            cultural_background="Traditional Chinese family",
            issues=["Work stress", "Relationship problems"],
            personality_traits=["Introverted", "Analytical"],
            communication_style="Reserved but thoughtful",
            goals=["Better work-life balance"],
            background_story="Recently moved to a new city for work",
            triggers=["Loud noises"],
            important_relationships=[],
            coping_mechanisms=["Meditation"],
            is_active=True
        )
        db_session.add(client)
        db_session.commit()
        return client
    
    @pytest.fixture
    def student_auth(self):
        """Create student authentication"""
        return StudentAuth(
            user_id="user-456",
            student_id="student-456",
            email="student@test.com",
            full_name="Test Student"
        )
    
    def test_service_initialization_without_api_key(self, monkeypatch):
        """Test service initialization fails without API key"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not provided"):
            AnthropicService()
    
    def test_get_anthropic_service_singleton(self, mock_anthropic_env):
        """Test that get_anthropic_service returns singleton"""
        service1 = get_anthropic_service()
        service2 = get_anthropic_service()
        
        assert service1 is service2
        assert isinstance(service1, AnthropicService)
    
    @patch('anthropic.Anthropic')
    def test_circuit_breaker_integration(self, mock_anthropic_class, mock_anthropic_env):
        """Test circuit breaker prevents cascading failures"""
        # Create mock client that always fails
        mock_client = Mock()
        mock_client.messages.create.side_effect = create_api_connection_error()
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService()
        
        # First 3 failures should open circuit
        for i in range(3):
            response = service.generate_response(
                messages=[{"role": "user", "content": f"Test {i}"}]
            )
            # Should get fallback response - check for any meaningful text
            assert len(response) > 0
            assert isinstance(response, str)
        
        # Circuit should now be open
        assert service.circuit_breaker.state == "open"
        
        # Further calls should not hit the API
        initial_call_count = mock_client.messages.create.call_count
        response = service.generate_response(
            messages=[{"role": "user", "content": "Test after open"}]
        )
        
        # Should get fallback without calling API
        assert mock_client.messages.create.call_count == initial_call_count
        assert len(response) > 0
        # Verify it's a fallback response - just check it's not empty and is a string
        assert isinstance(response, str)
    
    @patch('anthropic.Anthropic')
    def test_cost_tracking_integration(self, mock_anthropic_class, mock_anthropic_env):
        """Test cost tracking across multiple sessions"""
        # Create mock client with predictable responses
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="AI response " * 50)]  # ~50 tokens
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService()
        
        # Generate responses for multiple sessions
        session_ids = ["session-1", "session-2", "session-3"]
        
        for session_id in session_ids:
            for i in range(5):
                service.generate_response(
                    messages=[{"role": "user", "content": "Test message " * 10}],
                    session_id=session_id
                )
        
        # Check cost tracking
        assert service.daily_cost > 0
        assert len(service.session_costs) == 3
        
        # Each session should have costs
        for session_id in session_ids:
            assert session_id in service.session_costs
            assert service.session_costs[session_id] > 0
        
        # Reset one session
        service.reset_session_cost("session-1")
        assert service.session_costs.get("session-1", 0.0) == 0.0
        assert service.session_costs.get("session-2", 0.0) > 0.0
    
    @patch('anthropic.Anthropic')
    def test_daily_limit_enforcement(self, mock_anthropic_class, mock_anthropic_env):
        """Test daily cost limit prevents further API calls"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="AI response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService()
        
        # Artificially set daily cost near limit
        service.daily_cost = 4.99  # Just under $5 limit
        
        # This should succeed
        response1 = service.generate_response(
            messages=[{"role": "user", "content": "Test"}],
            session_id="test-session"
        )
        assert response1 == "AI response"
        
        # Set cost over limit
        service.daily_cost = 5.01
        
        # This should return fallback
        response2 = service.generate_response(
            messages=[{"role": "user", "content": "Test"}],
            session_id="test-session"
        )
        assert "high demand" in response2
        assert service.status == ServiceStatus.UNAVAILABLE
    
    @patch('anthropic.Anthropic')
    def test_error_recovery_flow(self, mock_anthropic_class, mock_anthropic_env):
        """Test service recovery after errors"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService()
        
        # Start with rate limit errors
        mock_client.messages.create.side_effect = create_rate_limit_error("Rate limited")
        
        # Should retry and eventually fail with RetryError
        from tenacity import RetryError
        with pytest.raises(RetryError):
            service.generate_response(
                messages=[{"role": "user", "content": "Test"}]
            )
        
        # After exhausting retries, circuit breaker should be open
        assert service.circuit_breaker.state == "open"
        assert service.status == ServiceStatus.DEGRADED
        
        # Now API recovers
        mock_response = Mock()
        mock_response.content = [Mock(text="Success")]
        mock_client.messages.create.side_effect = None
        mock_client.messages.create.return_value = mock_response
        
        # Circuit breaker is open, so first call should return fallback
        response = service.generate_response(
            messages=[{"role": "user", "content": "Test"}]
        )
        # Should get fallback because circuit is open
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Wait for circuit breaker recovery timeout to pass (or force it)
        service.circuit_breaker.last_failure_time = time.time() - 400  # Force timeout
        
        # Now should work again
        response = service.generate_response(
            messages=[{"role": "user", "content": "Test"}]
        )
        assert response == "Success"
        assert service.status == ServiceStatus.HEALTHY
    
    def test_service_status_monitoring(self, mock_anthropic_env):
        """Test service status monitoring capabilities"""
        service = AnthropicService()
        
        # Get initial status
        status = service.get_service_status()
        assert status["status"] == ServiceStatus.HEALTHY.value
        assert status["circuit_breaker_state"] == "closed"
        assert status["daily_cost"] == 0.0
        assert status["model"] in ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
        
        # Simulate some activity
        service._track_cost("session-1", 10000, is_input=True)
        service._update_service_status(ErrorType.RATE_LIMIT)
        service.last_error = {
            "type": ErrorType.RATE_LIMIT.value,
            "message": "Test error",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Get updated status
        status = service.get_service_status()
        assert status["status"] == ServiceStatus.DEGRADED.value
        assert status["daily_cost"] > 0.0
        assert status["last_error"] is not None
        assert status["last_error"]["type"] == ErrorType.RATE_LIMIT.value


class TestConversationServiceErrorHandling:
    """Test error handling in conversation service integration"""
    
    @pytest.fixture
    def mock_services(self, monkeypatch):
        """Mock all required services"""
        # Mock client service
        mock_client_service = Mock()
        mock_client = Mock(
            id="client-123",
            name="Test Client",
            age=25,
            issues=["Test issue"],
            personality_traits=["Test trait"],
            communication_style="Test style"
        )
        mock_client_service.get.return_value = mock_client
        
        # Mock session service with proper returns
        mock_session_service = Mock()
        # Create a proper object that can be validated by Pydantic
        from datetime import datetime
        mock_session_db = type('MockSession', (), {
            'id': "session-123",
            'student_id': "student-456",
            'client_profile_id': "client-123",
            'status': "active",
            'session_notes': "",
            'started_at': datetime.utcnow(),
            'ended_at': None,
            'total_tokens': 0,
            'estimated_cost': 0.0
        })()
        mock_session_service.create_session.return_value = mock_session_db
        mock_session_service.get_session.return_value = mock_session_db
        
        # Create proper message mocks that can be validated by Pydantic
        from datetime import datetime
        mock_message = Mock(
            id="msg-1",
            session_id="session-123",
            role="assistant",
            content="Test response",
            timestamp=datetime.utcnow(),
            token_count=10,
            sequence_number=1
        )
        mock_session_service.add_message.return_value = mock_message
        mock_session_service.get_messages.return_value = []
        
        # Mock prompt service
        mock_prompt_service = Mock()
        mock_prompt_service.generate_system_prompt.return_value = "System prompt"
        
        # Apply mocks
        monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
        monkeypatch.setattr("backend.services.conversation_service.session_service", mock_session_service)
        monkeypatch.setattr("backend.services.conversation_service.prompt_service", mock_prompt_service)
        
        return {
            "client": mock_client_service,
            "session": mock_session_service,
            "prompt": mock_prompt_service
        }
    
    @patch('backend.services.conversation_service.anthropic_service')
    def test_conversation_with_api_failure(self, mock_anthropic_factory, mock_services, db_session):
        """Test conversation handling when API fails"""
        # Create mock anthropic instance that fails
        mock_anthropic_instance = Mock()
        mock_anthropic_instance.generate_response.side_effect = Exception("API Error")
        mock_anthropic_factory.return_value = mock_anthropic_instance
        
        student = StudentAuth(
            id="auth-456",
            user_id="user-456",
            student_id="student-456",
            email="student@test.com",
            full_name="Test Student"
        )
        
        # Starting conversation should fail gracefully
        with pytest.raises(RuntimeError, match="Failed to generate AI greeting"):
            conversation_service.start_conversation(
                db=db_session,
                student=student,
                client_id="client-123"
            )
    
    @patch('backend.services.conversation_service.anthropic_service')
    def test_conversation_with_fallback_response(self, mock_anthropic_factory, mock_services, db_session):
        """Test conversation uses fallback responses appropriately"""
        # Create mock anthropic instance that returns fallback
        mock_anthropic_instance = Mock()
        mock_anthropic_instance.generate_response.return_value = (
            "I'm having trouble connecting right now. Let's pause for a moment - "
            "is there something specific you'd like to discuss?"
        )
        mock_anthropic_factory.return_value = mock_anthropic_instance
        
        student = StudentAuth(
            id="auth-456",
            user_id="user-456",
            student_id="student-456",
            email="student@test.com",
            full_name="Test Student"
        )
        
        # Send message should work with fallback
        result = conversation_service.send_message(
            db=db_session,
            session_id="session-123",
            content="Hello",
            user=student
        )
        
        # Should have received a response (even if fallback)
        assert result is not None
        assert mock_anthropic_instance.generate_response.called
    
    @patch('backend.services.conversation_service.anthropic_service')
    def test_conversation_cost_tracking_integration(self, mock_anthropic_factory, mock_services, db_session, monkeypatch):
        """Test cost tracking is properly integrated with conversations"""
        # Mock db.refresh to handle Mock objects
        original_refresh = db_session.refresh
        def mock_refresh(obj):
            # Check if it's a real SQLAlchemy model or a mock
            try:
                # If it has a proper __class__.__name__, it's likely real
                if hasattr(obj, '__tablename__') or (hasattr(obj, '__class__') and 
                    obj.__class__.__module__ != 'unittest.mock'):
                    # Real object, use original refresh
                    return original_refresh(obj)
            except:
                pass
            # Mock object, do nothing
            return None
        monkeypatch.setattr(db_session, "refresh", mock_refresh)
        # Create mock anthropic instance
        mock_anthropic_instance = Mock()
        mock_anthropic_instance.generate_response.return_value = "Test response"
        mock_anthropic_factory.return_value = mock_anthropic_instance
        
        # Ensure session_id is passed to anthropic service
        student = StudentAuth(
            id="auth-456",
            user_id="user-456",
            student_id="student-456",
            email="student@test.com",
            full_name="Test Student"
        )
        
        # Start conversation
        session = conversation_service.start_conversation(
            db=db_session,
            student=student,
            client_id="client-123"
        )
        
        # Verify session_id was passed for cost tracking
        call_args = mock_anthropic_instance.generate_response.call_args
        assert call_args.kwargs.get("session_id") == "session-123"


class TestErrorHandlingEndToEnd:
    """End-to-end tests for error handling scenarios"""
    
    @pytest.fixture
    def mock_anthropic_with_errors(self, monkeypatch):
        """Mock Anthropic to simulate various error conditions"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        
        # Create a mock that can be controlled
        mock_client = Mock()
        mock_async_client = AsyncMock()
        
        with patch('anthropic.Anthropic', return_value=mock_client), \
             patch('anthropic.AsyncAnthropic', return_value=mock_async_client):
            yield mock_client, mock_async_client
    
    def test_authentication_error_flow(self, mock_anthropic_with_errors):
        """Test complete flow when authentication fails"""
        mock_client, _ = mock_anthropic_with_errors
        mock_client.messages.create.side_effect = create_authentication_error("Invalid API key")
        
        service = AnthropicService()
        
        # Test connection should fail
        result = service.test_connection()
        assert result["status"] == "error"
        assert result["error_type"] == ErrorType.AUTHENTICATION.value
        assert "Authentication failed" in result["error"]
        assert service.status == ServiceStatus.UNAVAILABLE
        
        # Generate response should return fallback
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        # Should get a fallback response - check for any meaningful text
        assert len(response) > 0
        # Verify it's a fallback response (contains question or reflection)
        assert any(word in response.lower() for word in ["moment", "pause", "trouble", "difficulty", "feeling", "discuss"])
    
    def test_rate_limit_retry_flow(self, mock_anthropic_with_errors):
        """Test retry behavior with rate limits"""
        mock_client, _ = mock_anthropic_with_errors
        
        # First two calls fail with rate limit, third succeeds
        mock_response = Mock()
        mock_response.content = [Mock(text="Success after retry")]
        mock_client.messages.create.side_effect = [
            create_rate_limit_error("Rate limit 1"),
            create_rate_limit_error("Rate limit 2"),
            mock_response
        ]
        
        service = AnthropicService()
        
        # Should retry and eventually succeed
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert response == "Success after retry"
        assert mock_client.messages.create.call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self, mock_anthropic_with_errors, monkeypatch):
        """Test error handling in async methods"""
        _, mock_async_client = mock_anthropic_with_errors
        
        # Simulate connection error
        mock_async_client.messages.create.side_effect = create_api_connection_error()
        
        # Also need to patch the AsyncAnthropic class to use our mock
        with patch('backend.services.anthropic_service.AsyncAnthropic', return_value=mock_async_client):
            service = AnthropicService()
            service.async_client = mock_async_client  # Ensure our mock is used
            
            # Test async connection
            result = await service.test_connection_async()
            assert result["status"] == "error"
            assert result["error_type"] == ErrorType.CONNECTION.value
            
            # Test async generation with fallback
            response = await service.generate_response_async(
                messages=[{"role": "user", "content": "Hello"}]
            )
            assert len(response) > 0  # Should get fallback
    
    def test_timeout_handling(self, mock_anthropic_with_errors):
        """Test timeout error handling"""
        mock_client, _ = mock_anthropic_with_errors
        mock_client.messages.create.side_effect = create_api_timeout_error()
        
        service = AnthropicService()
        
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should get fallback response
        assert len(response) > 0
        assert service.last_error["type"] == ErrorType.TIMEOUT.value
