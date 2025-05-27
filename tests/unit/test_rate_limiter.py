"""
Unit tests for rate limiting utility
"""

import pytest
import time
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from backend.utils.rate_limiter import (
    RateLimiter, RateLimitExceeded, default_rate_limiter,
    rate_limit, rate_limit_user, rate_limit_student
)


class TestRateLimiter:
    """Test the RateLimiter class"""
    
    def test_init_with_defaults(self):
        """Test rate limiter initialization with default values"""
        limiter = RateLimiter()
        assert limiter.user_limit == 10  # Default from environment or constant
        assert limiter.user_window == 60  # 1 minute
        assert limiter.global_limit == 1000
        assert limiter.global_window == 3600  # 1 hour
    
    def test_init_with_custom_values(self):
        """Test rate limiter initialization with custom values"""
        limiter = RateLimiter(
            user_limit=5,
            user_window=30,
            global_limit=100,
            global_window=300
        )
        assert limiter.user_limit == 5
        assert limiter.user_window == 30
        assert limiter.global_limit == 100
        assert limiter.global_window == 300
    
    def test_check_limit_allows_initial_request(self):
        """Test that first request is always allowed"""
        limiter = RateLimiter(user_limit=5, global_limit=10)
        
        allowed, retry_after = limiter.check_limit()
        assert allowed is True
        assert retry_after is None
        
        # With user_id
        allowed, retry_after = limiter.check_limit("user1")
        assert allowed is True
        assert retry_after is None
    
    def test_user_rate_limit_enforcement(self):
        """Test per-user rate limit is enforced"""
        limiter = RateLimiter(user_limit=3, user_window=60)
        
        # First 3 requests should succeed
        for i in range(3):
            allowed, retry_after = limiter.check_limit("user1")
            assert allowed is True
            assert retry_after is None
        
        # 4th request should fail
        allowed, retry_after = limiter.check_limit("user1")
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
        
        # Different user should still be allowed
        allowed, retry_after = limiter.check_limit("user2")
        assert allowed is True
        assert retry_after is None
    
    def test_global_rate_limit_enforcement(self):
        """Test global rate limit is enforced"""
        limiter = RateLimiter(user_limit=10, global_limit=5)
        
        # First 5 requests should succeed (even with different users)
        for i in range(5):
            allowed, retry_after = limiter.check_limit(f"user{i}")
            assert allowed is True
            assert retry_after is None
        
        # 6th request should fail
        allowed, retry_after = limiter.check_limit("user_new")
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
    
    @patch('time.time')
    def test_sliding_window(self, mock_time):
        """Test that old requests expire from the window"""
        # Set initial time before creating limiter
        mock_time.return_value = 1000.0
        limiter = RateLimiter(user_limit=2, user_window=60)
        
        # Make 2 requests
        limiter.check_limit("user1")
        limiter.check_limit("user1")
        
        # 3rd request should fail
        allowed, _ = limiter.check_limit("user1")
        assert allowed is False
        
        # Move time forward by 61 seconds
        mock_time.return_value = 1061.0
        
        # Now request should succeed (old requests expired)
        allowed, _ = limiter.check_limit("user1")
        assert allowed is True
    
    @patch('time.time')
    def test_retry_after_calculation(self, mock_time):
        """Test retry_after is calculated correctly"""
        # Set initial time before creating limiter
        mock_time.return_value = 1000.0
        limiter = RateLimiter(user_limit=1, user_window=60)
        
        # First request
        limiter.check_limit("user1")
        
        # Second request should fail
        allowed, retry_after = limiter.check_limit("user1")
        assert allowed is False
        
        # Retry after should be approximately 60 seconds
        assert 59 <= retry_after <= 61
    
    def test_reset_user_limit(self):
        """Test resetting limits for a specific user"""
        limiter = RateLimiter(user_limit=1)
        
        # Use up the limit
        limiter.check_limit("user1")
        allowed, _ = limiter.check_limit("user1")
        assert allowed is False
        
        # Reset the user's limit
        limiter.reset_user_limit("user1")
        
        # Now should be allowed again
        allowed, _ = limiter.check_limit("user1")
        assert allowed is True
    
    def test_reset_all_limits(self):
        """Test resetting all limits"""
        limiter = RateLimiter(user_limit=1, global_limit=2)
        
        # Use up limits
        limiter.check_limit("user1")
        limiter.check_limit("user2")
        
        # Both should be blocked
        allowed, _ = limiter.check_limit("user1")
        assert allowed is False
        allowed, _ = limiter.check_limit("user3")
        assert allowed is False
        
        # Reset all limits
        limiter.reset_all_limits()
        
        # Now all should be allowed
        allowed, _ = limiter.check_limit("user1")
        assert allowed is True
        allowed, _ = limiter.check_limit("user3")
        assert allowed is True
    
    def test_get_user_usage(self):
        """Test getting usage statistics for a user"""
        limiter = RateLimiter(user_limit=5)
        
        # Make some requests
        limiter.check_limit("user1")
        limiter.check_limit("user1")
        limiter.check_limit("user1")
        
        usage = limiter.get_user_usage("user1")
        assert usage["user_id"] == "user1"
        assert usage["requests_in_window"] == 3
        assert usage["limit"] == 5
        assert usage["remaining"] == 2
        assert usage["window_seconds"] == 60
        
        # Check user with no requests
        usage = limiter.get_user_usage("user2")
        assert usage["requests_in_window"] == 0
        assert usage["remaining"] == 5
    
    def test_get_global_usage(self):
        """Test getting global usage statistics"""
        limiter = RateLimiter(global_limit=100)
        
        # Make some requests
        for i in range(7):
            limiter.check_limit(f"user{i}")
        
        usage = limiter.get_global_usage()
        assert usage["requests_in_window"] == 7
        assert usage["limit"] == 100
        assert usage["remaining"] == 93
        assert usage["window_seconds"] == 3600
    
    @patch('time.time')
    def test_cleanup_old_requests(self, mock_time):
        """Test automatic cleanup of old requests"""
        # Set initial time before creating limiter
        mock_time.return_value = 1000.0
        limiter = RateLimiter(user_limit=100, user_window=60, global_window=60)  # Use same window for test
        
        # Make requests
        for i in range(10):
            limiter.check_limit("user1")
        
        # Verify requests are tracked
        assert len(limiter._user_requests["user1"]) == 10
        assert len(limiter._global_requests) == 10
        
        # Move time forward past both windows
        mock_time.return_value = 1120.0  # 2 minutes later (past 60 second window)
        
        # Make another request to trigger cleanup
        limiter.check_limit("user2")
        
        # Old requests should be cleaned up
        assert "user1" not in limiter._user_requests  # Empty queue removed
        assert len(limiter._global_requests) == 1  # Only the new request


class TestRateLimitDecorator:
    """Test the rate_limit decorator"""
    
    def test_rate_limit_decorator_basic(self):
        """Test basic rate limit decorator functionality"""
        limiter = RateLimiter(user_limit=2)
        call_count = 0
        
        @rate_limit(limiter=limiter)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        # First 2 global calls should succeed
        assert test_function() == "success"
        assert test_function() == "success"
        assert call_count == 2
        
        # Reset for next test
        limiter.reset_all_limits()
    
    def test_rate_limit_decorator_with_user_id(self):
        """Test rate limit decorator with user_id extraction"""
        limiter = RateLimiter(user_limit=2)
        
        @rate_limit(
            limiter=limiter,
            get_user_id=lambda *args, **kwargs: kwargs.get('user_id')
        )
        def test_function(user_id: str):
            return f"success for {user_id}"
        
        # User 1: 2 calls should succeed
        assert test_function(user_id="user1") == "success for user1"
        assert test_function(user_id="user1") == "success for user1"
        
        # User 1: 3rd call should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            test_function(user_id="user1")
        assert "user1" in str(exc_info.value)
        
        # User 2: Should still work
        assert test_function(user_id="user2") == "success for user2"
    
    def test_rate_limit_decorator_no_raise(self):
        """Test rate limit decorator that returns None instead of raising"""
        limiter = RateLimiter(global_limit=1)
        
        @rate_limit(limiter=limiter, raise_on_limit=False)
        def test_function():
            return "success"
        
        # First call succeeds
        assert test_function() == "success"
        
        # Second call returns None
        assert test_function() is None
    
    def test_rate_limit_user_decorator(self):
        """Test the convenience rate_limit_user decorator"""
        limiter = RateLimiter(user_limit=1)
        
        # Replace default limiter temporarily
        original_default = default_rate_limiter
        import backend.utils.rate_limiter
        backend.utils.rate_limiter.default_rate_limiter = limiter
        
        try:
            @rate_limit_user
            def test_function(user_id: str, message: str):
                return f"{user_id}: {message}"
            
            # First call succeeds
            result = test_function(user_id="user1", message="hello")
            assert result == "user1: hello"
            
            # Second call for same user fails
            with pytest.raises(RateLimitExceeded):
                test_function(user_id="user1", message="hello again")
            
            # Different user succeeds
            result = test_function(user_id="user2", message="hi")
            assert result == "user2: hi"
        finally:
            # Restore original default limiter
            backend.utils.rate_limiter.default_rate_limiter = original_default
    
    def test_rate_limit_student_decorator(self):
        """Test the convenience rate_limit_student decorator"""
        limiter = RateLimiter(user_limit=1)
        
        # Replace default limiter temporarily
        original_default = default_rate_limiter
        import backend.utils.rate_limiter
        backend.utils.rate_limiter.default_rate_limiter = limiter
        
        try:
            @rate_limit_student
            def test_function(student_id: str, action: str):
                return f"Student {student_id}: {action}"
            
            # First call succeeds
            result = test_function(student_id="s1", action="login")
            assert result == "Student s1: login"
            
            # Second call for same student fails
            with pytest.raises(RateLimitExceeded):
                test_function(student_id="s1", action="another action")
            
            # Different student succeeds
            result = test_function(student_id="s2", action="login")
            assert result == "Student s2: login"
        finally:
            # Restore original default limiter
            backend.utils.rate_limiter.default_rate_limiter = original_default
    
    @pytest.mark.asyncio
    async def test_rate_limit_async_function(self):
        """Test rate limit decorator with async functions"""
        limiter = RateLimiter(global_limit=2)
        call_count = 0
        
        @rate_limit(limiter=limiter)
        async def async_test_function():
            nonlocal call_count
            call_count += 1
            return "async success"
        
        # First 2 calls should succeed
        assert await async_test_function() == "async success"
        assert await async_test_function() == "async success"
        assert call_count == 2
        
        # 3rd call should fail
        with pytest.raises(RateLimitExceeded):
            await async_test_function()


class TestRateLimitExceeded:
    """Test the RateLimitExceeded exception"""
    
    def test_exception_with_retry_after(self):
        """Test exception includes retry_after information"""
        exc = RateLimitExceeded("Rate limit hit", retry_after=30)
        assert str(exc) == "Rate limit hit"
        assert exc.retry_after == 30
    
    def test_exception_without_retry_after(self):
        """Test exception without retry_after"""
        exc = RateLimitExceeded("Rate limit hit")
        assert str(exc) == "Rate limit hit"
        assert exc.retry_after is None


class TestIntegrationScenarios:
    """Test realistic usage scenarios"""
    
    @patch('time.time')
    def test_conversation_rate_limiting_scenario(self, mock_time):
        """Test a realistic conversation rate limiting scenario"""
        # Set initial time before creating limiter
        mock_time.return_value = 1000.0
        
        # Configure: 5 messages per minute per user, 20 global per minute
        limiter = RateLimiter(
            user_limit=5,
            user_window=60,
            global_limit=20,
            global_window=60
        )
        
        # Simulate conversation service
        @rate_limit(
            limiter=limiter,
            get_user_id=lambda *args, **kwargs: kwargs.get('student_id')
        )
        def send_message(student_id: str, content: str):
            return {"status": "sent", "content": content}
        
        # Student 1 sends 5 messages - all should succeed
        for i in range(5):
            result = send_message(student_id="student1", content=f"Message {i}")
            assert result["status"] == "sent"
        
        # 6th message should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            send_message(student_id="student1", content="Too many messages")
        assert "student1" in str(exc_info.value)
        
        # Student 2 can still send messages
        result = send_message(student_id="student2", content="Hello")
        assert result["status"] == "sent"
        
        # Move time forward 1 minute
        mock_time.return_value = 1061.0
        
        # Student 1 can send again
        result = send_message(student_id="student1", content="After waiting")
        assert result["status"] == "sent"
    
    def test_multiple_decorators_scenario(self):
        """Test using multiple rate limiters for different purposes"""
        # Strict limiter for expensive operations
        expensive_limiter = RateLimiter(user_limit=1, user_window=300, global_limit=1, global_window=300)  # 1 per 5 minutes
        
        # Lenient limiter for regular operations
        regular_limiter = RateLimiter(user_limit=10, user_window=60)  # 10 per minute
        
        @rate_limit(limiter=expensive_limiter)
        def expensive_operation():
            return "expensive done"
        
        @rate_limit(limiter=regular_limiter)
        def regular_operation():
            return "regular done"
        
        # Can do many regular operations
        for _ in range(5):
            assert regular_operation() == "regular done"
        
        # But only one expensive operation
        assert expensive_operation() == "expensive done"
        with pytest.raises(RateLimitExceeded):
            expensive_operation()
        
        # Regular operations still work
        assert regular_operation() == "regular done"
