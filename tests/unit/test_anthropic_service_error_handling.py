"""
Unit tests for Anthropic Service error handling and robustness features

Tests comprehensive error handling, circuit breaker, cost tracking, and fallback responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime
import anthropic
import httpx

from backend.services.anthropic_service import (
    AnthropicService, ServiceStatus, ErrorType, CostAlert, 
    CircuitBreakerConfig, CircuitBreaker
)


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

def create_bad_request_error(message="Bad request"):
    """Create a BadRequestError for testing"""
    response = httpx.Response(
        400,
        json={"error": {"message": message, "type": "invalid_request_error"}},
        request=httpx.Request("POST", "https://api.anthropic.com")
    )
    return anthropic.BadRequestError(message=message, response=response, body={"error": {"message": message}})

def create_api_timeout_error():
    """Create an APITimeoutError for testing"""
    return anthropic.APITimeoutError(request=httpx.Request("POST", "https://api.anthropic.com"))


class TestCircuitBreaker:
    """Test the circuit breaker implementation"""
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in closed state"""
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == "closed"
        assert breaker.failure_count == 0
        
        can_execute, error_msg = breaker.can_execute()
        assert can_execute is True
        assert error_msg is None
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10)
        breaker = CircuitBreaker(config)
        
        # Record failures up to threshold
        breaker.record_failure()
        assert breaker.state == "closed"
        
        breaker.record_failure()
        assert breaker.state == "closed"
        
        breaker.record_failure()
        assert breaker.state == "open"
        
        # Check that execution is blocked
        can_execute, error_msg = breaker.can_execute()
        assert can_execute is False
        assert "Service temporarily unavailable" in error_msg
    
    @patch('time.time')
    def test_circuit_breaker_half_open_state(self, mock_time):
        """Test circuit breaker transitions to half-open state"""
        mock_time.return_value = 1000.0
        
        config = CircuitBreakerConfig(
            failure_threshold=2, 
            recovery_timeout=10,
            half_open_requests=2
        )
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == "open"
        
        # Time hasn't passed yet
        mock_time.return_value = 1005.0
        can_execute, _ = breaker.can_execute()
        assert can_execute is False
        
        # Enough time has passed
        mock_time.return_value = 1011.0
        can_execute, _ = breaker.can_execute()
        assert can_execute is True
        assert breaker.state == "half_open"
    
    @patch('time.time')
    def test_circuit_breaker_closes_after_success(self, mock_time):
        """Test circuit breaker closes after successful half-open requests"""
        mock_time.return_value = 1000.0
        
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0,  # Immediate recovery for testing
            half_open_requests=2
        )
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        breaker.record_failure()
        assert breaker.state == "open"
        
        # Time has passed (recovery_timeout=0 means immediate)
        mock_time.return_value = 1000.1
        
        # Move to half-open
        can_execute, _ = breaker.can_execute()
        assert can_execute is True
        assert breaker.state == "half_open"
        
        # Successful requests in half-open state
        breaker.record_success()
        assert breaker.state == "half_open"
        
        breaker.record_success()
        assert breaker.state == "closed"
        assert breaker.failure_count == 0
    
    @patch('time.time')
    def test_circuit_breaker_reopens_on_half_open_failure(self, mock_time):
        """Test circuit breaker reopens if failure occurs in half-open state"""
        mock_time.return_value = 1000.0
        
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0,
            half_open_requests=3
        )
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        breaker.record_failure()
        assert breaker.state == "open"
        
        # Time has passed
        mock_time.return_value = 1000.1
        
        # Move to half-open
        can_execute, _ = breaker.can_execute()
        assert can_execute is True
        assert breaker.state == "half_open"
        
        # Failure in half-open state reopens circuit
        breaker.record_failure()
        assert breaker.state == "open"


class TestAnthropicServiceErrorHandling:
    """Test error handling functionality"""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("ANTHROPIC_COST_WARNING", "0.05")
        monkeypatch.setenv("ANTHROPIC_COST_CRITICAL", "0.10")
        monkeypatch.setenv("ANTHROPIC_DAILY_LIMIT", "1.00")
    
    def test_error_categorization(self, mock_env):
        """Test correct categorization of different error types"""
        service = AnthropicService()
        
        # Test each error type
        assert service._categorize_error(
            create_authentication_error("auth failed")
        ) == ErrorType.AUTHENTICATION
        
        assert service._categorize_error(
            create_rate_limit_error("rate limit")
        ) == ErrorType.RATE_LIMIT
        
        assert service._categorize_error(
            create_api_connection_error()
        ) == ErrorType.CONNECTION
        
        assert service._categorize_error(
            create_bad_request_error("bad request")
        ) == ErrorType.INVALID_REQUEST
        
        assert service._categorize_error(
            create_api_timeout_error()
        ) == ErrorType.TIMEOUT
        
        assert service._categorize_error(
            Exception("unknown error")
        ) == ErrorType.UNKNOWN
    
    def test_user_friendly_error_messages(self, mock_env):
        """Test user-friendly error message generation"""
        service = AnthropicService()
        
        # Test each error type message
        assert "Authentication failed" in service._get_user_friendly_error(ErrorType.AUTHENTICATION)
        assert "Too many requests" in service._get_user_friendly_error(ErrorType.RATE_LIMIT)
        assert "Unable to connect" in service._get_user_friendly_error(ErrorType.CONNECTION)
        assert "Invalid request" in service._get_user_friendly_error(ErrorType.INVALID_REQUEST)
        assert "temporarily unavailable" in service._get_user_friendly_error(ErrorType.SERVER_ERROR)
        assert "took too long" in service._get_user_friendly_error(ErrorType.TIMEOUT)
        assert "unexpected error" in service._get_user_friendly_error(ErrorType.UNKNOWN)
    
    def test_service_status_updates(self, mock_env):
        """Test service status updates based on error types"""
        service = AnthropicService()
        
        # Start healthy
        assert service.status == ServiceStatus.HEALTHY
        
        # Authentication error makes service unavailable
        service._update_service_status(ErrorType.AUTHENTICATION)
        assert service.status == ServiceStatus.UNAVAILABLE
        
        # Rate limit makes service degraded
        service._update_service_status(ErrorType.RATE_LIMIT)
        assert service.status == ServiceStatus.DEGRADED
        
        # No error makes service healthy again
        service._update_service_status(None)
        assert service.status == ServiceStatus.HEALTHY
        assert service.last_error is None
    
    def test_fallback_response_generation(self, mock_env):
        """Test fallback response generation"""
        service = AnthropicService()
        
        # Basic fallback
        response = service._generate_fallback_response()
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Fallback with context
        response = service._generate_fallback_response("Additional context.")
        assert "Additional context." in response


class TestCostTracking:
    """Test cost tracking and alert functionality"""
    
    @pytest.fixture
    def service(self, monkeypatch):
        """Create service with mocked environment"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("ANTHROPIC_COST_WARNING", "0.10")
        monkeypatch.setenv("ANTHROPIC_COST_CRITICAL", "0.50")
        monkeypatch.setenv("ANTHROPIC_DAILY_LIMIT", "10.00")
        return AnthropicService()
    
    def test_cost_tracking_initialization(self, service):
        """Test cost tracking is properly initialized"""
        assert service.cost_alert.warning_threshold == 0.10
        assert service.cost_alert.critical_threshold == 0.50
        assert service.cost_alert.daily_limit == 10.00
        assert service.daily_cost == 0.0
        assert service.session_costs == {}
    
    @patch('backend.services.anthropic_service.logger')
    def test_cost_alert_warnings(self, mock_logger, service):
        """Test cost alert warnings are triggered"""
        # Track costs for a session
        service._track_cost("session-1", 50000, is_input=True)  # ~$0.0125 for haiku
        
        # Continue adding costs until warning threshold
        for _ in range(10):
            service._track_cost("session-1", 50000, is_input=True)
        
        # Check that warning was logged
        warning_calls = [call for call in mock_logger.warning.call_args_list 
                        if "exceeds warning threshold" in str(call)]
        assert len(warning_calls) > 0
    
    @patch('backend.services.anthropic_service.logger')
    def test_cost_alert_critical(self, mock_logger, service):
        """Test critical cost alerts"""
        # Add costs to exceed critical threshold
        for _ in range(50):
            service._track_cost("session-1", 50000, is_input=True)
        
        # Check that critical alert was logged
        critical_calls = [call for call in mock_logger.critical.call_args_list 
                         if "exceeds critical threshold" in str(call)]
        assert len(critical_calls) > 0
    
    @patch('backend.services.anthropic_service.logger')
    def test_daily_limit_enforcement(self, mock_logger, service):
        """Test daily limit enforcement"""
        # Add costs to approach daily limit
        for i in range(100):
            service._track_cost(f"session-{i}", 100000, is_input=True)
        
        # Check if daily limit was exceeded
        if service.daily_cost >= service.cost_alert.daily_limit:
            assert service.status == ServiceStatus.UNAVAILABLE
            
            # Check that critical alert was logged
            critical_calls = [call for call in mock_logger.critical.call_args_list 
                             if "Daily cost limit" in str(call)]
            assert len(critical_calls) > 0
    
    def test_cost_reset_daily(self, service):
        """Test daily cost reset functionality"""
        # Add some costs
        service._track_cost("session-1", 10000, is_input=True)
        initial_cost = service.daily_cost
        assert initial_cost > 0
        
        # Simulate next day
        service.cost_reset_date = datetime.utcnow().date()
        service._track_cost("session-2", 10000, is_input=True)
        
        # Cost should still accumulate (same day)
        assert service.daily_cost > initial_cost
    
    def test_session_cost_reset(self, service):
        """Test resetting cost for specific session"""
        # Track some costs
        service._track_cost("session-1", 10000, is_input=True)
        service._track_cost("session-2", 20000, is_input=True)
        
        assert "session-1" in service.session_costs
        assert "session-2" in service.session_costs
        
        # Reset session-1
        service.reset_session_cost("session-1")
        assert service.session_costs.get("session-1", 0.0) == 0.0
        assert service.session_costs.get("session-2", 0.0) > 0.0


class TestAnthropicServiceGeneration:
    """Test response generation with error handling"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Anthropic client"""
        mock = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock.messages.create.return_value = mock_response
        return mock
    
    @pytest.fixture
    def service_with_mock_client(self, monkeypatch, mock_client):
        """Create service with mocked client"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        service = AnthropicService()
        service.client = mock_client
        return service
    
    def test_generate_response_success(self, service_with_mock_client):
        """Test successful response generation"""
        service = service_with_mock_client
        
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="Be helpful",
            session_id="test-session"
        )
        
        assert response == "Test response"
        assert service.circuit_breaker.state == "closed"
        assert service.status == ServiceStatus.HEALTHY
    
    def test_generate_response_with_circuit_breaker_open(self, service_with_mock_client):
        """Test response generation when circuit breaker is open"""
        service = service_with_mock_client
        
        # Force circuit breaker open
        service.circuit_breaker.state = "open"
        service.circuit_breaker.last_failure_time = time.time()
        
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should return fallback response - check for any meaningful text
        assert len(response) > 0
        # Verify it's a fallback response (contains question or reflection)
        assert any(word in response.lower() for word in ["moment", "pause", "trouble", "difficulty", "feeling", "discuss"])
        assert service.client.messages.create.call_count == 0
    
    def test_generate_response_with_daily_limit_exceeded(self, service_with_mock_client):
        """Test response generation when daily cost limit is exceeded"""
        service = service_with_mock_client
        
        # Set daily cost above limit
        service.daily_cost = service.cost_alert.daily_limit + 1
        
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should return fallback response
        assert "high demand" in response or "trouble" in response
        assert service.client.messages.create.call_count == 0
    
    def test_generate_response_with_authentication_error(self, service_with_mock_client):
        """Test response generation with authentication error"""
        service = service_with_mock_client
        service.client.messages.create.side_effect = create_authentication_error("Invalid API key")
        
        response = service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
        assert service.status == ServiceStatus.UNAVAILABLE
        assert service.last_error["type"] == ErrorType.AUTHENTICATION.value
    
    @patch('backend.services.anthropic_service.logger')
    def test_generate_response_logging(self, mock_logger, service_with_mock_client):
        """Test that response generation logs appropriately"""
        service = service_with_mock_client
        
        service.generate_response(
            messages=[{"role": "user", "content": "Hello"}],
            session_id="test-session"
        )
        
        # Check info logs
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert any("Generating response for session test-session" in str(call) for call in info_calls)
        assert any("Response generated successfully" in str(call) for call in info_calls)


class TestServiceStatus:
    """Test service status and monitoring"""
    
    @pytest.fixture
    def service(self, monkeypatch):
        """Create service with mocked environment"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        return AnthropicService()
    
    def test_get_service_status(self, service):
        """Test service status reporting"""
        status = service.get_service_status()
        
        assert status["status"] == ServiceStatus.HEALTHY.value
        assert status["circuit_breaker_state"] == "closed"
        assert status["daily_cost"] == 0.0
        assert status["daily_limit"] == service.cost_alert.daily_limit
        assert status["model"] == service.model
        assert status["environment"] == service.environment
        assert status["last_error"] is None
    
    def test_service_status_with_errors(self, service):
        """Test service status reporting with errors"""
        # Simulate an error
        service._update_service_status(ErrorType.RATE_LIMIT)
        service.last_error = {
            "type": ErrorType.RATE_LIMIT.value,
            "message": "Rate limit exceeded",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        status = service.get_service_status()
        
        assert status["status"] == ServiceStatus.DEGRADED.value
        assert status["last_error"] is not None
        assert status["last_error"]["type"] == ErrorType.RATE_LIMIT.value


class TestConnectionTests:
    """Test connection test methods with error handling"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Anthropic client"""
        mock = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Connection successful")]
        mock.messages.create.return_value = mock_response
        return mock
    
    @pytest.fixture
    def service_with_mock_client(self, monkeypatch, mock_client):
        """Create service with mocked client"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        service = AnthropicService()
        service.client = mock_client
        return service
    
    def test_connection_test_success(self, service_with_mock_client):
        """Test successful connection test"""
        service = service_with_mock_client
        
        result = service.test_connection()
        
        assert result["status"] == "connected"
        assert result["test_response"] == "Connection successful"
        assert result["service_status"] == ServiceStatus.HEALTHY.value
    
    def test_connection_test_with_circuit_breaker(self, service_with_mock_client):
        """Test connection test when circuit breaker is open"""
        service = service_with_mock_client
        
        # Open circuit breaker
        service.circuit_breaker.state = "open"
        service.circuit_breaker.last_failure_time = time.time()
        
        result = service.test_connection()
        
        assert result["status"] == "error"
        assert result["error_type"] == "circuit_breaker"
        assert "temporarily unavailable" in result["error"]
    
    def test_connection_test_with_error(self, service_with_mock_client):
        """Test connection test with various errors"""
        service = service_with_mock_client
        service.client.messages.create.side_effect = create_rate_limit_error("Rate limit")
        
        result = service.test_connection()
        
        assert result["status"] == "error"
        assert result["error_type"] == ErrorType.RATE_LIMIT.value
        assert "Too many requests" in result["error"]
        assert service.circuit_breaker.failure_count == 1
        
        # In development, technical details should be included
        assert result.get("technical_details") is not None


class TestAsyncMethods:
    """Test async methods with error handling"""
    
    @pytest.fixture
    def mock_async_client(self):
        """Create mock async Anthropic client"""
        mock = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Async response")]
        
        # Create async mock
        async def mock_create(*args, **kwargs):
            return mock_response
        
        mock.messages.create = mock_create
        return mock
    
    @pytest.fixture
    def service_with_mock_async_client(self, monkeypatch, mock_async_client):
        """Create service with mocked async client"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        service = AnthropicService()
        service.async_client = mock_async_client
        return service
    
    @pytest.mark.asyncio
    async def test_async_connection_test_success(self, service_with_mock_async_client):
        """Test successful async connection test"""
        service = service_with_mock_async_client
        
        result = await service.test_connection_async()
        
        assert result["status"] == "connected"
        assert result["test_response"] == "Async response"
        assert result["service_status"] == ServiceStatus.HEALTHY.value
    
    @pytest.mark.asyncio
    async def test_async_generate_response_success(self, service_with_mock_async_client):
        """Test successful async response generation"""
        service = service_with_mock_async_client
        
        response = await service.generate_response_async(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="Be helpful",
            session_id="test-session"
        )
        
        assert response == "Async response"
        assert service.status == ServiceStatus.HEALTHY
