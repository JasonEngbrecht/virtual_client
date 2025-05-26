"""
Unit tests for Anthropic API Service
"""
import os
import pytest
from unittest.mock import Mock, patch
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend.services.anthropic_service import AnthropicService, get_anthropic_service


class TestAnthropicService:
    """Test suite for AnthropicService"""
    
    def test_init_with_api_key(self):
        """Test initialization with provided API key"""
        service = AnthropicService(api_key="test-api-key")
        assert service.api_key == "test-api-key"
        assert service.client is not None
        assert service.async_client is not None
    
    def test_init_from_environment(self):
        """Test initialization from environment variable"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-api-key"}):
            service = AnthropicService()
            assert service.api_key == "env-api-key"
    
    def test_init_no_api_key_raises_error(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not provided"):
                AnthropicService()
    
    def test_model_selection_development(self):
        """Test model selection for development environment"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "development"
        }):
            service = AnthropicService()
            assert "haiku" in service.model.lower()
            assert service.environment == "development"
    
    def test_model_selection_production(self):
        """Test model selection for production environment"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "production"
        }):
            service = AnthropicService()
            assert "sonnet" in service.model.lower()
            assert service.environment == "production"
    
    def test_model_override(self):
        """Test explicit model override via environment"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "development",
            "ANTHROPIC_MODEL": "claude-3-opus-20240229"
        }):
            service = AnthropicService()
            assert service.model == "claude-3-opus-20240229"
    
    @patch('anthropic.Anthropic')
    def test_test_connection_success(self, mock_anthropic_class):
        """Test successful connection test"""
        # Create mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="Connection successful")]
        
        # Setup mock client
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        result = service.test_connection()
        
        assert result["status"] == "connected"
        assert result["model"] == service.model
        assert result["test_response"] == "Connection successful"
        assert "environment" in result
    
    @patch('anthropic.Anthropic')
    def test_test_connection_auth_error(self, mock_anthropic_class):
        """Test connection with authentication error"""
        # Setup mock client to raise auth error
        mock_client = Mock()
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid API key",
            response=Mock(status_code=401),
            body=None
        )
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        result = service.test_connection()
        
        assert result["status"] == "error"
        assert result["error_type"] == "authentication"
        assert "Invalid API key" in result["error"]
    
    @patch('anthropic.Anthropic')
    def test_test_connection_connection_error(self, mock_anthropic_class):
        """Test connection with network error"""
        # Setup mock client to raise connection error
        mock_client = Mock()
        mock_request = Mock()
        mock_client.messages.create.side_effect = anthropic.APIConnectionError(
            message="Network error",
            request=mock_request
        )
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        result = service.test_connection()
        
        assert result["status"] == "error"
        assert result["error_type"] == "connection"
        assert "Network error" in result["error"]
    
    @patch('anthropic.Anthropic')
    def test_generate_response_success(self, mock_anthropic_class):
        """Test successful response generation"""
        # Create mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="Hello! How can I help you today?")]
        
        # Setup mock client
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        messages = [{"role": "user", "content": "Hello"}]
        response = service.generate_response(messages)
        
        assert response == "Hello! How can I help you today?"
        
        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        assert call_args["model"] == service.model
        assert call_args["messages"] == messages
        assert call_args["max_tokens"] == 500
        assert call_args["temperature"] == 0.7
    
    @patch('anthropic.Anthropic')
    def test_generate_response_with_system_prompt(self, mock_anthropic_class):
        """Test response generation with system prompt"""
        # Create mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="I am a helpful assistant.")]
        
        # Setup mock client
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        messages = [{"role": "user", "content": "Who are you?"}]
        system_prompt = "You are a helpful AI assistant."
        response = service.generate_response(messages, system_prompt=system_prompt)
        
        assert response == "I am a helpful assistant."
        
        # Verify system prompt was included
        call_args = mock_client.messages.create.call_args[1]
        assert call_args["system"] == system_prompt
    
    @patch('anthropic.Anthropic')
    def test_generate_response_rate_limit_retry(self, mock_anthropic_class):
        """Test retry on rate limit error"""
        # Create mock response for successful attempt
        mock_response = Mock()
        mock_response.content = [Mock(text="Success after retry")]
        
        # Setup mock client to fail once then succeed
        mock_client = Mock()
        mock_request = Mock()
        mock_client.messages.create.side_effect = [
            anthropic.RateLimitError(
                message="Rate limit exceeded",
                response=Mock(status_code=429, headers={}),
                body=None
            ),
            mock_response  # Success on second attempt
        ]
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Use patch to speed up retry wait time
        with patch('time.sleep'):
            response = service.generate_response(messages)
        
        assert response == "Success after retry"
        assert mock_client.messages.create.call_count == 2
    
    @patch('anthropic.Anthropic')
    def test_generate_response_api_error(self, mock_anthropic_class):
        """Test handling of general API errors"""
        # Setup mock client to raise API error
        mock_client = Mock()
        mock_request = Mock()
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="API error occurred",
            request=mock_request,
            body=None
        )
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        messages = [{"role": "user", "content": "Test"}]
        
        with pytest.raises(anthropic.APIError):
            service.generate_response(messages)
    
    def test_async_response_method_exists(self):
        """Test that async response method exists and is callable"""
        service = AnthropicService(api_key="test-key")
        assert hasattr(service, 'generate_response_async')
        assert callable(service.generate_response_async)
    
    @patch('backend.services.anthropic_service.AsyncAnthropic')
    @patch('anthropic.Anthropic')
    def test_async_client_initialization(self, mock_anthropic_class, mock_async_anthropic_class):
        """Test that async client is properly initialized"""
        mock_anthropic_class.return_value = Mock()
        mock_async_anthropic_class.return_value = Mock()
        
        service = AnthropicService(api_key="test-key")
        
        assert service.client is not None
        assert service.async_client is not None
        mock_anthropic_class.assert_called_once_with(api_key="test-key")
        mock_async_anthropic_class.assert_called_once_with(api_key="test-key")
    
    def test_count_tokens(self):
        """Test token counting integration"""
        service = AnthropicService(api_key="test-key")
        
        # Test various strings
        assert service.count_tokens("") == 0
        assert service.count_tokens("Hello") == 1  # 5 chars / 4 ≈ 1
        assert service.count_tokens("This is a test message") == 5  # 22 chars / 4 ≈ 5
    
    def test_get_model_pricing_haiku(self):
        """Test pricing retrieval for Haiku model"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "development"
        }):
            service = AnthropicService()
            pricing = service.get_model_pricing()
            
            assert "input" in pricing
            assert "output" in pricing
            assert "average" in pricing
            assert pricing["average"] == 0.75  # Haiku average price
    
    def test_get_model_pricing_sonnet(self):
        """Test pricing retrieval for Sonnet model"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "production"
        }):
            service = AnthropicService()
            pricing = service.get_model_pricing()
            
            assert "input" in pricing
            assert "output" in pricing
            assert "average" in pricing
            assert pricing["average"] == 9.00  # Sonnet average price
    
    def test_get_model_pricing_unknown_model(self):
        """Test pricing defaults to Haiku for unknown models"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "ANTHROPIC_MODEL": "unknown-model-123"
        }):
            service = AnthropicService()
            pricing = service.get_model_pricing()
            
            # Should default to Haiku pricing
            assert pricing["average"] == 0.75
    
    def test_live_connection(self):
        """Test actual API connection (only runs with valid API key)"""
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        if not api_key.startswith("sk-ant-"):
            pytest.skip(f"Requires valid ANTHROPIC_API_KEY for live test (found: {api_key[:10] if api_key else 'None'}...)")
        
        print(f"\nTesting with API key: {api_key[:20]}...{api_key[-5:]}")
        
        service = get_anthropic_service()
        result = service.test_connection()
        
        assert result["status"] == "connected"
        assert "Connection successful" in result["test_response"]
        print(f"Live test successful with model: {result['model']} in {result['environment']} mode")
    
    def test_get_anthropic_service_singleton(self):
        """Test that get_anthropic_service returns singleton"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            service1 = get_anthropic_service()
            service2 = get_anthropic_service()
            
            assert service1 is service2  # Same instance
    
    def test_custom_parameters(self):
        """Test custom max_tokens and temperature parameters"""
        with patch('anthropic.Anthropic') as mock_anthropic_class:
            # Create mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="Custom response")]
            
            # Setup mock client
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic_class.return_value = mock_client
            
            service = AnthropicService(api_key="test-key")
            
            messages = [{"role": "user", "content": "Test"}]
            response = service.generate_response(
                messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Verify custom parameters were used
            call_args = mock_client.messages.create.call_args[1]
            assert call_args["max_tokens"] == 1000
            assert call_args["temperature"] == 0.3
