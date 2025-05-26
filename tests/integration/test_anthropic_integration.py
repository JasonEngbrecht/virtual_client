"""
Integration tests for Anthropic service with the rest of the system
"""
import os
import pytest
from unittest.mock import patch, Mock
import anthropic

from backend.services.anthropic_service import get_anthropic_service, AnthropicService
from backend.utils.token_counter import count_tokens, calculate_cost


class TestAnthropicServiceIntegration:
    """Test Anthropic service integration with other components"""
    
    def test_anthropic_service_imports(self):
        """Test that anthropic service can be imported"""
        # This test verifies no import errors
        from backend.services.anthropic_service import AnthropicService, get_anthropic_service
        assert AnthropicService is not None
        assert get_anthropic_service is not None
    
    def test_token_counter_integration(self):
        """Test that anthropic service integrates with token counter"""
        service = AnthropicService(api_key="test-key")
        
        # Test token counting
        test_text = "This is a test message for token counting"
        token_count = service.count_tokens(test_text)
        
        # Should use the centralized token counter
        assert token_count == count_tokens(test_text)
        assert token_count == 10  # 41 chars / 4 ≈ 10
    
    def test_pricing_integration(self):
        """Test that pricing information aligns with token counter"""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "ENVIRONMENT": "development"
        }):
            service = AnthropicService()
            pricing = service.get_model_pricing()
            
            # Calculate cost for 1000 tokens
            cost = calculate_cost(1000, model="haiku")
            expected_cost = (1000 / 1_000_000) * pricing["average"]
            
            assert cost == expected_cost
    
    @patch('anthropic.Anthropic')
    def test_message_token_tracking_pattern(self, mock_anthropic_class):
        """Test the pattern for tracking tokens in messages"""
        # This demonstrates how the service will be used with sessions
        
        # Mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="I understand. How can I help you today?")]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        # Simulate a conversation flow
        user_message = "Hello, I need help with a client issue"
        assistant_response = service.generate_response([
            {"role": "user", "content": user_message}
        ])
        
        # Calculate tokens for both messages
        user_tokens = service.count_tokens(user_message)
        assistant_tokens = service.count_tokens(assistant_response)
        
        # This is how it would be used in session tracking
        total_tokens = user_tokens + assistant_tokens
        session_cost = calculate_cost(total_tokens, model="haiku")
        
        assert user_tokens > 0
        assert assistant_tokens > 0
        assert total_tokens == user_tokens + assistant_tokens
        assert session_cost > 0
    
    def test_environment_based_model_selection(self):
        """Test that model selection works correctly in different environments"""
        # Development environment
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "development"
        }):
            dev_service = AnthropicService()
            assert "haiku" in dev_service.model.lower()
            
            # Verify cost is lower for development
            dev_cost = calculate_cost(10000, model="haiku")
            
        # Production environment  
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "APP_ENV": "production"
        }):
            prod_service = AnthropicService()
            assert "sonnet" in prod_service.model.lower()
            
            # Verify cost is higher for production
            prod_cost = calculate_cost(10000, model="sonnet")
            
        # Development should be cheaper
        assert dev_cost < prod_cost
    
    def test_error_handling_patterns(self):
        """Test that error handling follows project patterns"""
        # Test missing API key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AnthropicService()
            
            assert "ANTHROPIC_API_KEY" in str(exc_info.value)
    
    @patch('anthropic.Anthropic')
    def test_retry_mechanism(self, mock_anthropic_class):
        """Test that retry mechanism works as configured"""
        # Mock to fail twice then succeed
        mock_response = Mock()
        mock_response.content = [Mock(text="Success")]
        
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            anthropic.RateLimitError("Rate limit", response=Mock(status_code=429, headers={}), body=None),
            anthropic.RateLimitError("Rate limit", response=Mock(status_code=429, headers={}), body=None),
            mock_response
        ]
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(api_key="test-key")
        
        # Should succeed on third attempt
        with patch('time.sleep'):  # Speed up test
            result = service.generate_response([{"role": "user", "content": "Test"}])
        
        assert result == "Success"
        assert mock_client.messages.create.call_count == 3
