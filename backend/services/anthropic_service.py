"""
Anthropic API Service for Virtual Client

Handles all interactions with the Anthropic Claude API, including:
- API client setup and configuration
- Model selection based on environment
- Response generation with retry logic
- Comprehensive error handling and fallback responses
- Cost tracking and alerts
- Circuit breaker for API protection
- Structured logging and monitoring
"""
import os
import time
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import anthropic
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ErrorType(Enum):
    """Categorized error types for better handling"""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    CONNECTION = "connection"
    INVALID_REQUEST = "invalid_request"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class CostAlert:
    """Cost alert configuration"""
    warning_threshold: float = 0.10  # $0.10
    critical_threshold: float = 0.50  # $0.50
    daily_limit: float = 10.00  # $10.00
    

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 300  # Seconds before attempting recovery
    half_open_requests: int = 3  # Test requests in half-open state


class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_attempts = 0
        
    def record_success(self):
        """Record a successful call"""
        if self.state == "half_open":
            self.half_open_attempts += 1
            if self.half_open_attempts >= self.config.half_open_requests:
                self.state = "closed"
                self.failure_count = 0
                self.half_open_attempts = 0
                logger.info("Circuit breaker closed after successful recovery")
        else:
            self.failure_count = 0
            
    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
        if self.state == "half_open":
            self.state = "open"
            self.half_open_attempts = 0
            logger.warning("Circuit breaker reopened after failure in half-open state")
            
    def can_execute(self) -> Tuple[bool, Optional[str]]:
        """Check if request can be executed"""
        if self.state == "closed":
            return True, None
            
        if self.state == "open":
            # Check if we should try half-open
            if self.last_failure_time and \
               time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = "half_open"
                self.half_open_attempts = 0
                logger.info("Circuit breaker entering half-open state")
                return True, None
            else:
                if self.last_failure_time:
                    time_remaining = self.config.recovery_timeout - (time.time() - self.last_failure_time)
                    return False, f"Service temporarily unavailable. Try again in {int(max(0, time_remaining))} seconds."
                return False, "Service temporarily unavailable."
                
        # half_open state
        return True, None


class AnthropicService:
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic service.
        
        Args:
            api_key: Optional API key. If not provided, will look for ANTHROPIC_API_KEY env var.
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided or found in environment variables")
        
        # Initialize both sync and async clients
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        
        # Get model configuration
        self.model = self._get_model_config()
        self.environment = os.getenv("APP_ENV", "development")
        
        # Initialize cost tracking
        self.cost_alert = CostAlert(
            warning_threshold=float(os.getenv("ANTHROPIC_COST_WARNING", "0.10")),
            critical_threshold=float(os.getenv("ANTHROPIC_COST_CRITICAL", "0.50")),
            daily_limit=float(os.getenv("ANTHROPIC_DAILY_LIMIT", "10.00"))
        )
        self.session_costs: Dict[str, float] = {}
        self.daily_cost = 0.0
        self.cost_reset_date = datetime.utcnow().date()
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=int(os.getenv("ANTHROPIC_FAILURE_THRESHOLD", "5")),
            recovery_timeout=int(os.getenv("ANTHROPIC_RECOVERY_TIMEOUT", "300")),
            half_open_requests=int(os.getenv("ANTHROPIC_HALF_OPEN_REQUESTS", "3"))
        ))
        
        # Service status
        self.status = ServiceStatus.HEALTHY
        self.last_error: Optional[Dict[str, Any]] = None
        
        logger.info(f"Anthropic service initialized with model: {self.model} in {self.environment} mode")
    
    def _get_model_config(self) -> str:
        """
        Get model based on environment configuration.
        
        Returns:
            Model name string (Haiku for development/testing, Sonnet for production)
        """
        environment = os.getenv("APP_ENV", "development")
        model_override = os.getenv("ANTHROPIC_MODEL")  # Allow explicit override
        
        if model_override:
            logger.info(f"Using model override: {model_override}")
            return model_override
        
        if environment == "production":
            return "claude-3-sonnet-20240229"
        else:
            # Use Haiku for development/testing (cheaper)
            return "claude-3-haiku-20240307"
    
    def _categorize_error(self, error: Exception) -> ErrorType:
        """Categorize an exception into an error type"""
        error_class_name = error.__class__.__name__
        
        # Handle by class name for better compatibility
        if "AuthenticationError" in error_class_name:
            return ErrorType.AUTHENTICATION
        elif "RateLimitError" in error_class_name:
            return ErrorType.RATE_LIMIT
        elif "APIConnectionError" in error_class_name:
            return ErrorType.CONNECTION
        elif "APITimeoutError" in error_class_name:
            return ErrorType.TIMEOUT
        elif "BadRequestError" in error_class_name:
            return ErrorType.INVALID_REQUEST
        elif "APIStatusError" in error_class_name:
            if hasattr(error, 'status_code') and error.status_code >= 500:
                return ErrorType.SERVER_ERROR
            return ErrorType.INVALID_REQUEST
        else:
            return ErrorType.UNKNOWN
    
    def _get_user_friendly_error(self, error_type: ErrorType, details: str = "") -> str:
        """Get user-friendly error message"""
        messages = {
            ErrorType.AUTHENTICATION: "Authentication failed. Please check your credentials.",
            ErrorType.RATE_LIMIT: "Too many requests. Please wait a moment and try again.",
            ErrorType.CONNECTION: "Unable to connect to the AI service. Please check your internet connection.",
            ErrorType.INVALID_REQUEST: "Invalid request. Please try rephrasing your message.",
            ErrorType.SERVER_ERROR: "The AI service is temporarily unavailable. Please try again later.",
            ErrorType.TIMEOUT: "The request took too long. Please try again.",
            ErrorType.UNKNOWN: "An unexpected error occurred. Please try again."
        }
        return messages.get(error_type, messages[ErrorType.UNKNOWN])
    
    def _update_service_status(self, error_type: Optional[ErrorType] = None):
        """Update service status based on errors"""
        if error_type is None:
            self.status = ServiceStatus.HEALTHY
            self.last_error = None
        elif error_type in [ErrorType.AUTHENTICATION, ErrorType.CONNECTION]:
            self.status = ServiceStatus.UNAVAILABLE
        elif error_type == ErrorType.RATE_LIMIT:
            self.status = ServiceStatus.DEGRADED
        else:
            if self.circuit_breaker.state == "open":
                self.status = ServiceStatus.UNAVAILABLE
            else:
                self.status = ServiceStatus.DEGRADED
    
    def _track_cost(self, session_id: Optional[str], tokens: int, is_input: bool = True, model_name: Optional[str] = None):
        """Track API usage costs"""
        # Reset daily cost if needed
        current_date = datetime.utcnow().date()
        if current_date > self.cost_reset_date:
            self.daily_cost = 0.0
            self.cost_reset_date = current_date
            self.session_costs.clear()
        
        # Calculate cost using the specified model or default
        from ..utils.token_counter import calculate_cost
        current_model = model_name if model_name else self.model
        
        # Determine model type from model name
        if "haiku" in current_model.lower():
            model_type = "haiku"
        elif "opus" in current_model.lower():
            model_type = "opus"
        else:
            model_type = "sonnet"  # Default for all other Sonnet variants
        
        token_type = "input" if is_input else "output"
        cost = calculate_cost(tokens, model_type, token_type)
        
        # Update tracking
        self.daily_cost += cost
        if session_id:
            self.session_costs[session_id] = self.session_costs.get(session_id, 0.0) + cost
        
        # Check alerts
        if session_id and self.session_costs[session_id] >= self.cost_alert.critical_threshold:
            logger.critical(f"Session {session_id} cost (${self.session_costs[session_id]:.3f}) exceeds critical threshold")
        elif session_id and self.session_costs[session_id] >= self.cost_alert.warning_threshold:
            logger.warning(f"Session {session_id} cost (${self.session_costs[session_id]:.3f}) exceeds warning threshold")
        
        if self.daily_cost >= self.cost_alert.daily_limit:
            logger.critical(f"Daily cost limit (${self.cost_alert.daily_limit:.2f}) reached!")
            self.status = ServiceStatus.UNAVAILABLE
    
    def _generate_fallback_response(self, context: str = "") -> str:
        """Generate educational fallback response when API is unavailable"""
        # Check if we're in mock mode due to authentication failure
        if self.last_error and self.last_error.get('type') == 'authentication':
            # Generate more contextual mock responses for testing
            mock_responses = [
                "That's a really good question. I've been thinking about it a lot lately. The stress has been affecting my sleep and my appetite.",
                "I appreciate you asking. It's been difficult to talk about this with anyone. My family doesn't really understand what I'm going through.",
                "Yes, exactly. That's what makes it so hard. I feel like I should be able to handle this better, but I just can't seem to shake this feeling.",
                "I've tried a few things, but nothing seems to work for very long. Maybe I'm not doing them right, or maybe I need to try something different.",
                "Thank you for listening. It helps to talk about it. Sometimes I feel so alone with these problems.",
            ]
        else:
            mock_responses = [
                "I apologize, but I'm having trouble responding right now. Let's take a moment to reflect on what we've discussed so far.",
                "I seem to be having some difficulty at the moment. Perhaps we could explore this topic from a different angle?",
                "I'm experiencing some technical issues. While we wait, what aspects of our conversation would you like to focus on?",
                "I need a moment to gather my thoughts. In the meantime, how are you feeling about our conversation so far?",
                "I'm having trouble connecting right now. Let's pause for a moment - is there something specific you'd like to discuss?"
            ]
        
        # Use context to select appropriate response
        import random
        response = random.choice(mock_responses)
        
        if context:
            response += f" {context}"
            
        return response
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and health information"""
        return {
            "status": self.status.value,
            "circuit_breaker_state": self.circuit_breaker.state,
            "daily_cost": round(self.daily_cost, 4),
            "daily_limit": self.cost_alert.daily_limit,
            "model": self.model,
            "environment": self.environment,
            "last_error": self.last_error
        }
    
    def reset_session_cost(self, session_id: str):
        """Reset cost tracking for a specific session"""
        if session_id in self.session_costs:
            self.session_costs[session_id] = 0.0
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection with a simple synchronous message.
        
        Returns:
            Dictionary with connection status and test response
        """
        # Check circuit breaker first
        can_execute, error_msg = self.circuit_breaker.can_execute()
        if not can_execute:
            return {
                "status": "error",
                "error_type": "circuit_breaker",
                "error": error_msg,
                "service_status": self.status.value
            }
        
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, respond with 'Connection successful' only."}],
                max_tokens=20
            )
            
            self.circuit_breaker.record_success()
            self._update_service_status()
            
            return {
                "status": "connected",
                "model": self.model,
                "environment": self.environment,
                "test_response": response.content[0].text,
                "service_status": self.status.value
            }
        except Exception as e:
            error_type = self._categorize_error(e)
            user_message = self._get_user_friendly_error(error_type)
            
            self.circuit_breaker.record_failure()
            self._update_service_status(error_type)
            self.last_error = {
                "type": error_type.value,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.error(f"Connection test failed - {error_type.value}: {e}")
            
            return {
                "status": "error",
                "error_type": error_type.value,
                "error": user_message,
                "technical_details": str(e) if self.environment == "development" else None,
                "service_status": self.status.value
            }
    
    async def test_connection_async(self) -> Dict[str, Any]:
        """
        Test API connection with a simple asynchronous message.
        
        Returns:
            Dictionary with connection status and test response
        """
        # Check circuit breaker first
        can_execute, error_msg = self.circuit_breaker.can_execute()
        if not can_execute:
            return {
                "status": "error",
                "error_type": "circuit_breaker",
                "error": error_msg,
                "service_status": self.status.value
            }
        
        try:
            response = await self.async_client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, respond with 'Connection successful' only."}],
                max_tokens=20
            )
            
            self.circuit_breaker.record_success()
            self._update_service_status()
            
            return {
                "status": "connected",
                "model": self.model,
                "environment": self.environment,
                "test_response": response.content[0].text,
                "service_status": self.status.value
            }
        except Exception as e:
            error_type = self._categorize_error(e)
            user_message = self._get_user_friendly_error(error_type)
            
            self.circuit_breaker.record_failure()
            self._update_service_status(error_type)
            self.last_error = {
                "type": error_type.value,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.error(f"Async connection test failed - {error_type.value}: {e}")
            
            return {
                "status": "error",
                "error_type": error_type.value,
                "error": user_message,
                "technical_details": str(e) if self.environment == "development" else None,
                "service_status": self.status.value
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate a synchronous response from Claude with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens in response (default: 500)
            temperature: Response randomness 0-1 (default: 0.7)
            session_id: Optional session ID for cost tracking
            model: Optional model name to override default
            
        Returns:
            Generated response text
            
        Raises:
            anthropic.RateLimitError: If rate limit is exceeded after retries
            Exception: For other API errors
        """
        # Check circuit breaker
        can_execute, error_msg = self.circuit_breaker.can_execute()
        if not can_execute:
            logger.warning(f"Circuit breaker open: {error_msg}")
            return self._generate_fallback_response("Let me take a moment to gather my thoughts.")
        
        # Check daily cost limit
        if self.daily_cost >= self.cost_alert.daily_limit:
            logger.error("Daily cost limit reached, using fallback response")
            self.status = ServiceStatus.UNAVAILABLE
            return self._generate_fallback_response(
                "I'm currently experiencing high demand. Let's continue our conversation thoughtfully."
            )
        
        try:
            # Use provided model or fall back to default
            selected_model = model if model else self.model
            
            # Track input tokens for cost
            input_tokens = sum(self.count_tokens(msg['content']) for msg in messages)
            if system_prompt:
                input_tokens += self.count_tokens(system_prompt)
            self._track_cost(session_id, input_tokens, is_input=True, model_name=selected_model)
            
            kwargs = {
                "model": selected_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt
            
            # Log the request
            logger.info(f"Generating response for session {session_id or 'unknown'} with {len(messages)} messages")
            
            response = self.client.messages.create(**kwargs)
            
            # Extract text from response
            response_text = response.content[0].text
            
            # Track output tokens with selected model
            output_tokens = self.count_tokens(response_text)
            self._track_cost(session_id, output_tokens, is_input=False, model_name=selected_model)
            
            # Record success
            self.circuit_breaker.record_success()
            self._update_service_status()
            
            # Log success metrics
            total_cost = self.session_costs.get(session_id, 0.0) if session_id else 0.0
            logger.info(
                f"Response generated successfully - "
                f"Session: {session_id or 'unknown'}, "
                f"Input tokens: {input_tokens}, "
                f"Output tokens: {output_tokens}, "
                f"Session cost: ${total_cost:.4f}"
            )
            
            return response_text
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit, will retry: {e}")
            self.circuit_breaker.record_failure()
            self._update_service_status(ErrorType.RATE_LIMIT)
            raise  # Let retry decorator handle it
        except Exception as e:
            error_type = self._categorize_error(e)
            self.circuit_breaker.record_failure()
            self._update_service_status(error_type)
            self.last_error = {
                "type": error_type.value,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.error(f"Failed to generate response - {error_type.value}: {e}")
            
            # For critical errors, don't retry
            if error_type in [ErrorType.AUTHENTICATION, ErrorType.INVALID_REQUEST]:
                return self._generate_fallback_response(
                    "I'm having trouble understanding. Could you rephrase that?"
                )
            
            # For other errors, let retry mechanism handle or return fallback
            if error_type != ErrorType.RATE_LIMIT:
                return self._generate_fallback_response()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def generate_response_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate an asynchronous response from Claude with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens in response (default: 500)
            temperature: Response randomness 0-1 (default: 0.7)
            session_id: Optional session ID for cost tracking
            model: Optional model name to override default
            
        Returns:
            Generated response text
            
        Raises:
            anthropic.RateLimitError: If rate limit is exceeded after retries
            Exception: For other API errors
        """
        # Check circuit breaker
        can_execute, error_msg = self.circuit_breaker.can_execute()
        if not can_execute:
            logger.warning(f"Circuit breaker open: {error_msg}")
            return self._generate_fallback_response("Let me take a moment to gather my thoughts.")
        
        # Check daily cost limit
        if self.daily_cost >= self.cost_alert.daily_limit:
            logger.error("Daily cost limit reached, using fallback response")
            self.status = ServiceStatus.UNAVAILABLE
            return self._generate_fallback_response(
                "I'm currently experiencing high demand. Let's continue our conversation thoughtfully."
            )
        
        try:
            # Use provided model or fall back to default
            selected_model = model if model else self.model
            
            # Track input tokens for cost
            input_tokens = sum(self.count_tokens(msg['content']) for msg in messages)
            if system_prompt:
                input_tokens += self.count_tokens(system_prompt)
            self._track_cost(session_id, input_tokens, is_input=True, model_name=selected_model)
            
            kwargs = {
                "model": selected_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt
            
            # Log the request
            logger.info(f"Generating async response for session {session_id or 'unknown'} with {len(messages)} messages")
            
            response = await self.async_client.messages.create(**kwargs)
            
            # Extract text from response
            response_text = response.content[0].text
            
            # Track output tokens with selected model
            output_tokens = self.count_tokens(response_text)
            self._track_cost(session_id, output_tokens, is_input=False, model_name=selected_model)
            
            # Record success
            self.circuit_breaker.record_success()
            self._update_service_status()
            
            # Log success metrics
            total_cost = self.session_costs.get(session_id, 0.0) if session_id else 0.0
            logger.info(
                f"Async response generated successfully - "
                f"Session: {session_id or 'unknown'}, "
                f"Input tokens: {input_tokens}, "
                f"Output tokens: {output_tokens}, "
                f"Session cost: ${total_cost:.4f}"
            )
            
            return response_text
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit, will retry: {e}")
            self.circuit_breaker.record_failure()
            self._update_service_status(ErrorType.RATE_LIMIT)
            raise  # Let retry decorator handle it
        except Exception as e:
            error_type = self._categorize_error(e)
            self.circuit_breaker.record_failure()
            self._update_service_status(error_type)
            self.last_error = {
                "type": error_type.value,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.error(f"Failed to generate async response - {error_type.value}: {e}")
            
            # For critical errors, don't retry
            if error_type in [ErrorType.AUTHENTICATION, ErrorType.INVALID_REQUEST]:
                return self._generate_fallback_response(
                    "I'm having trouble understanding. Could you rephrase that?"
                )
            
            # For other errors, let retry mechanism handle or return fallback
            if error_type != ErrorType.RATE_LIMIT:
                return self._generate_fallback_response()
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Note: This is an approximation. For exact counts, we'll use the 
        token_counter utility that follows the 4 chars ≈ 1 token rule.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Import the centralized token counter
        from ..utils.token_counter import count_tokens
        return count_tokens(text)
    
    def get_model_pricing(self) -> Dict[str, float]:
        """
        Get pricing information for the current model.
        
        Returns:
            Dictionary with pricing per million tokens
        """
        from ..utils.token_counter import PRICING
        
        if "haiku" in self.model.lower():
            return PRICING["haiku"]
        elif "sonnet" in self.model.lower():
            return PRICING["sonnet"]
        else:
            # Default to Haiku pricing if model unknown
            logger.warning(f"Unknown model {self.model}, using Haiku pricing")
            return PRICING["haiku"]


# Create a default instance (will be initialized on first import if API key is available)
_anthropic_service_instance = None

def get_anthropic_service() -> AnthropicService:
    """
    Get or create the global Anthropic service instance.
    
    Returns:
        AnthropicService instance
        
    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    global _anthropic_service_instance
    if _anthropic_service_instance is None:
        _anthropic_service_instance = AnthropicService()
    return _anthropic_service_instance


# For backward compatibility and convenience
def anthropic_service() -> AnthropicService:
    """Convenience function to get the Anthropic service instance."""
    return get_anthropic_service()
