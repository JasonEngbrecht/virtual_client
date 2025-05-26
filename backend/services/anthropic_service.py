"""
Anthropic API Service for Virtual Client

Handles all interactions with the Anthropic Claude API, including:
- API client setup and configuration
- Model selection based on environment
- Response generation with retry logic
- Error handling and logging
"""
import os
from typing import Optional, List, Dict, Any
import anthropic
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)


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
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection with a simple synchronous message.
        
        Returns:
            Dictionary with connection status and test response
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, respond with 'Connection successful' only."}],
                max_tokens=20
            )
            
            return {
                "status": "connected",
                "model": self.model,
                "environment": self.environment,
                "test_response": response.content[0].text
            }
        except anthropic.APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            return {
                "status": "error",
                "error_type": "connection",
                "error": str(e)
            }
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return {
                "status": "error",
                "error_type": "authentication",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "status": "error",
                "error_type": "unknown",
                "error": str(e)
            }
    
    async def test_connection_async(self) -> Dict[str, Any]:
        """
        Test API connection with a simple asynchronous message.
        
        Returns:
            Dictionary with connection status and test response
        """
        try:
            response = await self.async_client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, respond with 'Connection successful' only."}],
                max_tokens=20
            )
            
            return {
                "status": "connected",
                "model": self.model,
                "environment": self.environment,
                "test_response": response.content[0].text
            }
        except anthropic.APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            return {
                "status": "error",
                "error_type": "connection",
                "error": str(e)
            }
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return {
                "status": "error",
                "error_type": "authentication",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "status": "error",
                "error_type": "unknown",
                "error": str(e)
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError)
    )
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a synchronous response from Claude with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens in response (default: 500)
            temperature: Response randomness 0-1 (default: 0.7)
            
        Returns:
            Generated response text
            
        Raises:
            anthropic.RateLimitError: If rate limit is exceeded after retries
            Exception: For other API errors
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = self.client.messages.create(**kwargs)
            
            # Extract text from response
            return response.content[0].text
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit, will retry: {e}")
            raise  # Let retry decorator handle it
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError)
    )
    async def generate_response_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate an asynchronous response from Claude with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens in response (default: 500)
            temperature: Response randomness 0-1 (default: 0.7)
            
        Returns:
            Generated response text
            
        Raises:
            anthropic.RateLimitError: If rate limit is exceeded after retries
            Exception: For other API errors
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = await self.async_client.messages.create(**kwargs)
            
            # Extract text from response
            return response.content[0].text
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit, will retry: {e}")
            raise  # Let retry decorator handle it
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}")
            raise
    
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
