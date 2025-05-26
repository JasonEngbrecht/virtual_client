"""
Token counting utility for tracking API usage and costs

This module provides functions for estimating token counts from text
and calculating costs based on different model pricing.
"""

from typing import Dict


# Pricing per 1M tokens (in dollars)
PRICING: Dict[str, Dict[str, float]] = {
    "haiku": {
        "input": 0.25,    # $0.25 per 1M input tokens
        "output": 1.25,   # $1.25 per 1M output tokens
        "average": 0.75   # $0.75 per 1M tokens (average)
    },
    "sonnet": {
        "input": 3.00,    # $3.00 per 1M input tokens
        "output": 15.00,  # $15.00 per 1M output tokens
        "average": 9.00   # $9.00 per 1M tokens (average)
    }
}

# Default model for cost calculations
DEFAULT_MODEL = "haiku"


def count_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    This uses a simple character-based estimation where approximately
    4 characters equal 1 token. This is a rough estimate that works
    reasonably well for English text.
    
    For production use, consider using tiktoken or the Anthropic
    token counting API for more accurate counts.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0
    
    # Simple estimation: ~4 characters per token
    # This is a reasonable approximation for English text
    return max(1, len(text) // 4)


def calculate_cost(
    tokens: int, 
    model: str = DEFAULT_MODEL,
    token_type: str = "average"
) -> float:
    """
    Calculate the cost for a given number of tokens.
    
    Args:
        tokens: Number of tokens
        model: Model name ("haiku" or "sonnet")
        token_type: Type of tokens ("input", "output", or "average")
        
    Returns:
        Cost in dollars
        
    Raises:
        ValueError: If model or token_type is not recognized
    """
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}. Available models: {list(PRICING.keys())}")
    
    if token_type not in PRICING[model]:
        raise ValueError(f"Unknown token type: {token_type}. Available types: {list(PRICING[model].keys())}")
    
    # Get price per 1M tokens
    price_per_million = PRICING[model][token_type]
    
    # Calculate cost
    cost = (tokens / 1_000_000) * price_per_million
    
    return cost


def estimate_conversation_cost(
    total_tokens: int,
    model: str = DEFAULT_MODEL
) -> float:
    """
    Estimate the cost of a conversation based on total tokens.
    
    This uses the average pricing between input and output tokens
    since we don't track them separately in the MVP.
    
    Args:
        total_tokens: Total number of tokens in the conversation
        model: Model name ("haiku" or "sonnet")
        
    Returns:
        Estimated cost in dollars
    """
    return calculate_cost(total_tokens, model, "average")


def format_cost(cost: float) -> str:
    """
    Format a cost value for display.
    
    Args:
        cost: Cost in dollars
        
    Returns:
        Formatted cost string (e.g., "$0.003")
    """
    if cost < 0.01:
        # Show 3 decimal places for small amounts
        return f"${cost:.3f}"
    elif cost < 1.00:
        # Show 2 decimal places for cents
        return f"${cost:.2f}"
    else:
        # Show 2 decimal places for dollars
        return f"${cost:.2f}"
