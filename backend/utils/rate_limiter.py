"""
Rate limiting utility for controlling API usage

This module provides rate limiting functionality to prevent abuse and control
costs. It supports both per-user and global rate limits with configurable
time windows.

For MVP, this uses in-memory storage. The design allows easy migration to
Redis or other distributed storage for production use.
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional, Tuple, Callable, Any
import os


# Default rate limits - can be overridden by environment variables
DEFAULT_USER_LIMIT = int(os.getenv("RATE_LIMIT_USER_PER_MINUTE", "10"))  # 10 messages per minute per user
DEFAULT_GLOBAL_LIMIT = int(os.getenv("RATE_LIMIT_GLOBAL_PER_HOUR", "1000"))  # 1000 messages per hour total

# Time windows in seconds
MINUTE = 60
HOUR = 3600


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after  # Seconds until the limit resets


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    
    This implementation uses in-memory storage for MVP. The interface is
    designed to allow easy migration to Redis or other distributed storage.
    """
    
    def __init__(
        self,
        user_limit: int = DEFAULT_USER_LIMIT,
        user_window: int = MINUTE,
        global_limit: int = DEFAULT_GLOBAL_LIMIT,
        global_window: int = HOUR
    ):
        """
        Initialize rate limiter with configurable limits.
        
        Args:
            user_limit: Maximum requests per user in the time window
            user_window: Time window for user limits in seconds
            global_limit: Maximum total requests in the time window
            global_window: Time window for global limits in seconds
        """
        self.user_limit = user_limit
        self.user_window = user_window
        self.global_limit = global_limit
        self.global_window = global_window
        
        # In-memory storage
        # For Redis migration: Replace these with Redis sorted sets
        self._user_requests: Dict[str, deque] = defaultdict(deque)
        self._global_requests: deque = deque()
        
        # Track last cleanup time to avoid excessive cleanup operations
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every minute
    
    def check_limit(self, user_id: Optional[str] = None) -> Tuple[bool, Optional[int]]:
        """
        Check if a request is within rate limits.
        
        Args:
            user_id: Optional user identifier for per-user limits
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is within limits
            - retry_after_seconds: Seconds until limit resets (if exceeded)
        """
        current_time = time.time()
        
        # Periodic cleanup to prevent memory growth
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_requests(current_time)
            self._last_cleanup = current_time
        
        # Check global limit
        global_allowed, global_retry = self._check_global_limit(current_time)
        if not global_allowed:
            return False, global_retry
        
        # Check user limit if user_id provided
        if user_id:
            user_allowed, user_retry = self._check_user_limit(user_id, current_time)
            if not user_allowed:
                return False, user_retry
        
        # Record the request
        self._record_request(user_id, current_time)
        
        return True, None
    
    def _check_global_limit(self, current_time: float) -> Tuple[bool, Optional[int]]:
        """Check global rate limit"""
        window_start = current_time - self.global_window
        
        # Remove old requests outside the window
        while self._global_requests and self._global_requests[0] < window_start:
            self._global_requests.popleft()
        
        # Check if we're at the limit
        if len(self._global_requests) >= self.global_limit:
            # Calculate when the oldest request will fall out of the window
            oldest_request = self._global_requests[0]
            retry_after = int(oldest_request + self.global_window - current_time) + 1
            return False, retry_after
        
        return True, None
    
    def _check_user_limit(self, user_id: str, current_time: float) -> Tuple[bool, Optional[int]]:
        """Check per-user rate limit"""
        window_start = current_time - self.user_window
        user_requests = self._user_requests[user_id]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Check if we're at the limit
        if len(user_requests) >= self.user_limit:
            # Calculate when the oldest request will fall out of the window
            oldest_request = user_requests[0]
            retry_after = int(oldest_request + self.user_window - current_time) + 1
            return False, retry_after
        
        return True, None
    
    def _record_request(self, user_id: Optional[str], current_time: float):
        """Record a request for rate limiting"""
        self._global_requests.append(current_time)
        
        if user_id:
            self._user_requests[user_id].append(current_time)
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove old requests to prevent memory growth"""
        # Clean global requests
        window_start = current_time - self.global_window
        while self._global_requests and self._global_requests[0] < window_start:
            self._global_requests.popleft()
        
        # Clean user requests
        user_window_start = current_time - self.user_window
        empty_users = []
        
        for user_id, requests in self._user_requests.items():
            while requests and requests[0] < user_window_start:
                requests.popleft()
            
            # Mark empty queues for removal
            if not requests:
                empty_users.append(user_id)
        
        # Remove empty user entries
        for user_id in empty_users:
            del self._user_requests[user_id]
    
    def reset_user_limit(self, user_id: str):
        """
        Reset rate limit for a specific user.
        Useful for testing or administrative overrides.
        """
        if user_id in self._user_requests:
            del self._user_requests[user_id]
    
    def reset_all_limits(self):
        """
        Reset all rate limits.
        Useful for testing or system recovery.
        """
        self._user_requests.clear()
        self._global_requests.clear()
    
    def get_user_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get current usage statistics for a user.
        
        Returns:
            Dictionary with usage information
        """
        current_time = time.time()
        window_start = current_time - self.user_window
        user_requests = self._user_requests.get(user_id, deque())
        
        # Count requests in current window
        recent_requests = [r for r in user_requests if r >= window_start]
        
        return {
            "user_id": user_id,
            "requests_in_window": len(recent_requests),
            "limit": self.user_limit,
            "window_seconds": self.user_window,
            "remaining": max(0, self.user_limit - len(recent_requests))
        }
    
    def get_global_usage(self) -> Dict[str, Any]:
        """
        Get current global usage statistics.
        
        Returns:
            Dictionary with usage information
        """
        current_time = time.time()
        window_start = current_time - self.global_window
        
        # Count requests in current window
        recent_requests = [r for r in self._global_requests if r >= window_start]
        
        return {
            "requests_in_window": len(recent_requests),
            "limit": self.global_limit,
            "window_seconds": self.global_window,
            "remaining": max(0, self.global_limit - len(recent_requests))
        }


# Global rate limiter instance with default settings
default_rate_limiter = RateLimiter()


def rate_limit(
    limiter: Optional[RateLimiter] = None,
    get_user_id: Optional[Callable] = None,
    raise_on_limit: bool = True
):
    """
    Decorator for rate limiting functions or API endpoints.
    
    Args:
        limiter: RateLimiter instance to use (defaults to global instance)
        get_user_id: Function to extract user_id from function arguments
        raise_on_limit: If True, raise RateLimitExceeded. If False, return None.
        
    Example:
        @rate_limit(get_user_id=lambda *args, **kwargs: kwargs.get('user_id'))
        def send_message(user_id: str, content: str):
            # Function implementation
            
        # For FastAPI endpoints:
        @rate_limit(get_user_id=lambda *args, **kwargs: kwargs.get('current_user'))
        def api_endpoint(current_user: str = Depends(get_current_user)):
            # Endpoint implementation
    """
    if limiter is None:
        limiter = default_rate_limiter
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id if getter provided
            user_id = None
            if get_user_id:
                try:
                    user_id = get_user_id(*args, **kwargs)
                except:
                    # If we can't get user_id, continue without user-specific limit
                    pass
            
            # Check rate limit
            allowed, retry_after = limiter.check_limit(user_id)
            
            if not allowed:
                if raise_on_limit:
                    message = f"Rate limit exceeded. Try again in {retry_after} seconds."
                    if user_id:
                        message = f"Rate limit exceeded for user {user_id}. Try again in {retry_after} seconds."
                    raise RateLimitExceeded(message, retry_after)
                else:
                    return None
            
            # Call the original function
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user_id if getter provided
            user_id = None
            if get_user_id:
                try:
                    user_id = get_user_id(*args, **kwargs)
                except:
                    # If we can't get user_id, continue without user-specific limit
                    pass
            
            # Check rate limit
            allowed, retry_after = limiter.check_limit(user_id)
            
            if not allowed:
                if raise_on_limit:
                    message = f"Rate limit exceeded. Try again in {retry_after} seconds."
                    if user_id:
                        message = f"Rate limit exceeded for user {user_id}. Try again in {retry_after} seconds."
                    raise RateLimitExceeded(message, retry_after)
                else:
                    return None
            
            # Call the original function
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


# Convenience decorators with common configurations
def rate_limit_user(func: Callable) -> Callable:
    """
    Rate limit decorator that extracts user_id from keyword arguments.
    Expects functions to have a 'user_id' parameter.
    """
    return rate_limit(get_user_id=lambda *args, **kwargs: kwargs.get('user_id'))(func)


def rate_limit_student(func: Callable) -> Callable:
    """
    Rate limit decorator for student endpoints.
    Expects functions to have a 'student_id' parameter.
    """
    return rate_limit(get_user_id=lambda *args, **kwargs: kwargs.get('student_id'))(func)
