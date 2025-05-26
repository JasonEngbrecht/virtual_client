"""
Unit tests for token counting utility
"""

import pytest
from backend.utils.token_counter import (
    count_tokens, 
    calculate_cost, 
    estimate_conversation_cost,
    format_cost,
    PRICING
)


class TestTokenCounter:
    """Test the token counting functionality"""
    
    def test_count_tokens_empty_string(self):
        """Test counting tokens for empty string"""
        assert count_tokens("") == 0
        assert count_tokens(None) == 0
    
    def test_count_tokens_simple_text(self):
        """Test counting tokens for simple text"""
        # Approximately 4 characters per token
        assert count_tokens("test") == 1  # 4 chars
        assert count_tokens("hello world") == 2  # 11 chars -> 2 tokens
        assert count_tokens("a" * 20) == 5  # 20 chars -> 5 tokens
    
    def test_count_tokens_longer_text(self):
        """Test counting tokens for longer text"""
        text = "This is a longer test message to verify token counting. " * 10
        # 56 chars * 10 = 560 chars -> ~140 tokens
        tokens = count_tokens(text)
        assert 135 <= tokens <= 145  # Allow some margin
    
    def test_count_tokens_minimum_one(self):
        """Test that non-empty text always returns at least 1 token"""
        assert count_tokens("a") == 1
        assert count_tokens("ab") == 1
        assert count_tokens("abc") == 1


class TestCostCalculation:
    """Test cost calculation functionality"""
    
    def test_calculate_cost_haiku_model(self):
        """Test cost calculation for Haiku model"""
        # Test with 1000 tokens
        cost = calculate_cost(1000, model="haiku", token_type="average")
        expected = (1000 / 1_000_000) * 0.75  # $0.75 per 1M tokens
        assert cost == pytest.approx(expected)
        
        # Test with 1M tokens
        cost = calculate_cost(1_000_000, model="haiku", token_type="average")
        assert cost == pytest.approx(0.75)
    
    def test_calculate_cost_sonnet_model(self):
        """Test cost calculation for Sonnet model"""
        # Test with 1000 tokens
        cost = calculate_cost(1000, model="sonnet", token_type="average")
        expected = (1000 / 1_000_000) * 9.00  # $9.00 per 1M tokens
        assert cost == pytest.approx(expected)
        
        # Test with 1M tokens
        cost = calculate_cost(1_000_000, model="sonnet", token_type="average")
        assert cost == pytest.approx(9.00)
    
    def test_calculate_cost_different_token_types(self):
        """Test cost calculation for different token types"""
        tokens = 10_000
        
        # Haiku input tokens
        cost = calculate_cost(tokens, model="haiku", token_type="input")
        assert cost == pytest.approx((tokens / 1_000_000) * 0.25)
        
        # Haiku output tokens
        cost = calculate_cost(tokens, model="haiku", token_type="output")
        assert cost == pytest.approx((tokens / 1_000_000) * 1.25)
        
        # Sonnet input tokens
        cost = calculate_cost(tokens, model="sonnet", token_type="input")
        assert cost == pytest.approx((tokens / 1_000_000) * 3.00)
        
        # Sonnet output tokens
        cost = calculate_cost(tokens, model="sonnet", token_type="output")
        assert cost == pytest.approx((tokens / 1_000_000) * 15.00)
    
    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens"""
        assert calculate_cost(0, model="haiku") == 0.0
        assert calculate_cost(0, model="sonnet") == 0.0
    
    def test_calculate_cost_invalid_model(self):
        """Test cost calculation with invalid model"""
        with pytest.raises(ValueError, match="Unknown model"):
            calculate_cost(1000, model="invalid_model")
    
    def test_calculate_cost_invalid_token_type(self):
        """Test cost calculation with invalid token type"""
        with pytest.raises(ValueError, match="Unknown token type"):
            calculate_cost(1000, model="haiku", token_type="invalid_type")


class TestEstimateConversationCost:
    """Test conversation cost estimation"""
    
    def test_estimate_conversation_cost_haiku(self):
        """Test estimating conversation cost for Haiku"""
        # Typical conversation might be 1000 tokens
        cost = estimate_conversation_cost(1000, model="haiku")
        assert cost == pytest.approx(0.00075)  # $0.00075
        
        # Larger conversation - 10,000 tokens
        cost = estimate_conversation_cost(10_000, model="haiku")
        assert cost == pytest.approx(0.0075)  # $0.0075
    
    def test_estimate_conversation_cost_sonnet(self):
        """Test estimating conversation cost for Sonnet"""
        # Typical conversation might be 1000 tokens
        cost = estimate_conversation_cost(1000, model="sonnet")
        assert cost == pytest.approx(0.009)  # $0.009
        
        # Larger conversation - 10,000 tokens
        cost = estimate_conversation_cost(10_000, model="sonnet")
        assert cost == pytest.approx(0.09)  # $0.09
    
    def test_estimate_conversation_cost_default_model(self):
        """Test that default model is Haiku"""
        cost_default = estimate_conversation_cost(1000)
        cost_haiku = estimate_conversation_cost(1000, model="haiku")
        assert cost_default == cost_haiku


class TestFormatCost:
    """Test cost formatting for display"""
    
    def test_format_cost_very_small(self):
        """Test formatting very small costs (< $0.01)"""
        assert format_cost(0.0001) == "$0.000"
        assert format_cost(0.0005) == "$0.001"
        assert format_cost(0.0099) == "$0.010"
    
    def test_format_cost_cents(self):
        """Test formatting costs in cents range"""
        assert format_cost(0.01) == "$0.01"
        assert format_cost(0.10) == "$0.10"
        assert format_cost(0.99) == "$0.99"
    
    def test_format_cost_dollars(self):
        """Test formatting costs in dollars"""
        assert format_cost(1.00) == "$1.00"
        assert format_cost(10.50) == "$10.50"
        assert format_cost(99.99) == "$99.99"
    
    def test_format_cost_zero(self):
        """Test formatting zero cost"""
        assert format_cost(0.0) == "$0.000"


class TestPricingConstants:
    """Test that pricing constants are properly defined"""
    
    def test_pricing_structure(self):
        """Test that PRICING has expected structure"""
        assert "haiku" in PRICING
        assert "sonnet" in PRICING
        
        for model in ["haiku", "sonnet"]:
            assert "input" in PRICING[model]
            assert "output" in PRICING[model]
            assert "average" in PRICING[model]
            
            # Verify all prices are positive
            for token_type in ["input", "output", "average"]:
                assert PRICING[model][token_type] > 0
    
    def test_pricing_relationships(self):
        """Test that pricing relationships make sense"""
        # Output tokens should be more expensive than input
        assert PRICING["haiku"]["output"] > PRICING["haiku"]["input"]
        assert PRICING["sonnet"]["output"] > PRICING["sonnet"]["input"]
        
        # Average should be between input and output
        for model in ["haiku", "sonnet"]:
            assert PRICING[model]["input"] < PRICING[model]["average"] < PRICING[model]["output"]
        
        # Sonnet should be more expensive than Haiku
        for token_type in ["input", "output", "average"]:
            assert PRICING["sonnet"][token_type] > PRICING["haiku"][token_type]
