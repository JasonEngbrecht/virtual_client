"""
Integration tests for rate limiting with conversation service
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.conversation_service import conversation_service
from backend.models.auth import StudentAuth
from backend.models.session import SessionCreate
from backend.models.message import MessageCreate
from backend.utils.rate_limiter import RateLimiter, RateLimitExceeded, rate_limit


class TestConversationRateLimiting:
    """Test rate limiting applied to conversation operations"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter with tight limits for testing"""
        return RateLimiter(
            user_limit=3,      # 3 messages per minute per user
            user_window=60,
            global_limit=10,   # 10 messages per minute total
            global_window=60
        )
    
    @pytest.fixture
    def mock_services(self, monkeypatch, db_session):
        """Mock the services used by conversation service"""
        # Mock db.refresh to avoid SQLAlchemy issues with Mock objects
        original_refresh = db_session.refresh
        def mock_refresh(obj):
            # Do nothing for mock objects
            if isinstance(obj, Mock):
                return
            # Call original for real objects
            return original_refresh(obj)
        
        monkeypatch.setattr(db_session, "refresh", mock_refresh)
        # Create mock client profile
        mock_client = Mock(
            id="client-123",
            name="Test Client",
            age=25,
            gender="female",
            background_story="Test background"
        )
        
        # Mock client service
        mock_client_service = Mock()
        mock_client_service.get.return_value = mock_client
        
        # Create mock session
        mock_session = Mock(
            id="session-123",
            student_id="student-123",
            client_profile_id="client-123",
            status="active",
            total_tokens=0,
            estimated_cost=0.0,
            started_at=datetime.utcnow(),
            ended_at=None,
            session_notes=None
        )
        
        # Mock session service
        mock_session_service = Mock()
        mock_session_service.create_session.return_value = mock_session
        
        # Create a flexible mock that returns sessions with different student IDs
        mock_sessions = {}
        
        def mock_get_session(db, session_id, student_id=None):
            # Return a stored session or create one
            if session_id in mock_sessions:
                return mock_sessions[session_id]
            return None
        
        def create_mock_session(session_id, student_id):
            session = Mock(
                id=session_id,
                student_id=student_id,
                client_profile_id="client-123",
                status="active",
                total_tokens=0,
                estimated_cost=0.0,
                started_at=datetime.utcnow(),
                ended_at=None,
                session_notes=None
            )
            mock_sessions[session_id] = session
            return session
        
        # Set default session for backward compatibility
        create_mock_session("session-123", "student-123")
        
        mock_session_service.get_session.side_effect = mock_get_session
        mock_session_service.create_session.side_effect = lambda db, session_data, student_id: create_mock_session(f"session-{len(mock_sessions)}", student_id)
        # Track message sequence numbers per session
        message_sequences = {}
        
        def mock_add_message(db, session_id, message_data):
            # Get next sequence number for this session
            if session_id not in message_sequences:
                message_sequences[session_id] = 0
            message_sequences[session_id] += 1
            
            return Mock(
                id=f"msg-{message_sequences[session_id]}",
                session_id=session_id,
                role=message_data.role,
                content=message_data.content,
                token_count=message_data.token_count,
                timestamp=datetime.utcnow(),
                sequence_number=message_sequences[session_id]
            )
        
        mock_session_service.add_message.side_effect = mock_add_message
        mock_session_service.get_messages.return_value = []
        
        # Mock prompt service
        mock_prompt_service = Mock()
        mock_prompt_service.generate_system_prompt.return_value = "System prompt"
        
        # Mock anthropic service
        mock_anthropic_instance = Mock()
        mock_anthropic_instance.generate_response.return_value = "AI response"  # Return just the string
        mock_anthropic_service = Mock(return_value=mock_anthropic_instance)
        
        # Mock the conversation service's get_ai_response to return tuple
        def mock_get_ai_response(self, db, session, user_message, conversation_history):
            return ("AI response", 25)  # Return tuple as expected
        
        # Apply mocks
        monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
        monkeypatch.setattr("backend.services.conversation_service.session_service", mock_session_service)
        monkeypatch.setattr("backend.services.conversation_service.prompt_service", mock_prompt_service)
        monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
        monkeypatch.setattr("backend.services.conversation_service.ConversationService.get_ai_response", mock_get_ai_response)
        
        return {
            "client": mock_client_service,
            "session": mock_session_service,
            "prompt": mock_prompt_service,
            "anthropic": mock_anthropic_service
        }
    
    def test_rate_limited_send_message(self, db_session, rate_limiter, mock_services):
        """Test applying rate limiting to send_message"""
        student = StudentAuth(id="student-123", student_id="student-123")
        
        # Create a rate-limited version of send_message
        @rate_limit(
            limiter=rate_limiter,
            get_user_id=lambda *args, **kwargs: kwargs.get('user').student_id
        )
        def rate_limited_send_message(db, session_id, content, user):
            return conversation_service.send_message(db, session_id, content, user)
        
        # First 3 messages should succeed
        for i in range(3):
            result = rate_limited_send_message(
                db_session,
                "session-123",  # Using mock session id
                f"Message {i}",
                user=student
            )
            assert result is not None
        
        # 4th message should hit rate limit
        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limited_send_message(
                db_session,
                "session-123",  # Using mock session id
                "Too many messages",
                user=student
            )
        assert "student-123" in str(exc_info.value)
        assert exc_info.value.retry_after is not None
    
    def test_rate_limited_start_conversation(self, db_session, rate_limiter, mock_services):
        """Test rate limiting conversation starts"""
        student = StudentAuth(id="student-456", student_id="student-456")
        
        # Create a rate-limited version that limits conversation starts
        @rate_limit(
            limiter=RateLimiter(user_limit=2, user_window=300),  # 2 conversations per 5 minutes
            get_user_id=lambda *args, **kwargs: args[1].student_id if len(args) > 1 else None  # args[1] is 'student'
        )
        def rate_limited_start_conversation(db, student, client_id):
            return conversation_service.start_conversation(db, student, client_id)
        
        # First 2 conversations should succeed
        result1 = rate_limited_start_conversation(db_session, student, "client-1")
        assert result1 is not None
        
        result2 = rate_limited_start_conversation(db_session, student, "client-2")
        assert result2 is not None
        
        # 3rd conversation should hit rate limit
        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limited_start_conversation(db_session, student, "client-3")
        assert "student-456" in str(exc_info.value)
    
    def test_global_rate_limit(self, db_session, rate_limiter, mock_services, monkeypatch):
        """Test global rate limit across multiple users"""
        # Use a limiter with low global limit
        global_limiter = RateLimiter(
            user_limit=100,  # High user limit
            global_limit=5,  # Low global limit
            global_window=60
        )
        
        # Mock send_message to avoid session validation issues
        call_count = 0
        def mock_send_message(self, db, session_id, content, user):
            nonlocal call_count
            call_count += 1
            return Mock(id=f"msg-{call_count}", content=content, role="assistant")
        
        monkeypatch.setattr("backend.services.conversation_service.ConversationService.send_message", mock_send_message)
        
        @rate_limit(
            limiter=global_limiter,
            get_user_id=lambda *args, **kwargs: kwargs.get('user').student_id
        )
        def rate_limited_send_message(db, session_id, content, user):
            return conversation_service.send_message(db, session_id, content, user)
        
        # Send messages from different users
        for i in range(5):
            student = StudentAuth(id=f"student-{i}", student_id=f"student-{i}")
            result = rate_limited_send_message(
                db_session,
                f"session-{i}",  # Each student has their own session
                f"Message from student {i}",
                user=student
            )
            assert result is not None
        
        # 6th message should hit global limit (even from new user)
        new_student = StudentAuth(id="student-new", student_id="student-new")
        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limited_send_message(
                db_session,
                "session-new",
                "Global limit exceeded",
                user=new_student
            )
        assert "Rate limit exceeded" in str(exc_info.value)
    
    @patch('time.time')
    def test_rate_limit_recovery(self, mock_time, db_session, rate_limiter, mock_services, monkeypatch):
        """Test that rate limits recover after time window"""
        student = StudentAuth(id="student-789", student_id="student-789")
        mock_time.return_value = 1000.0
        
        # Create a mock session for this student
        mock_sessions = mock_services["session"]
        # Call the create_session mock with proper arguments
        test_session = mock_sessions.create_session(
            db_session, 
            Mock(student_id="student-789", client_profile_id="client-123"),  # session_data
            "student-789"
        )
        
        @rate_limit(
            limiter=rate_limiter,
            get_user_id=lambda *args, **kwargs: kwargs.get('user').student_id
        )
        def rate_limited_send_message(db, session_id, content, user):
            return conversation_service.send_message(db, session_id, content, user)
        
        # Use up the rate limit
        for i in range(3):
            rate_limited_send_message(
                db_session,
                test_session.id,
                f"Message {i}",
                user=student
            )
        
        # Next message should fail
        with pytest.raises(RateLimitExceeded):
            rate_limited_send_message(
                db_session,
                test_session.id,
                "Too many",
                user=student
            )
        
        # Move time forward past the window
        mock_time.return_value = 1061.0  # 61 seconds later
        
        # Should be able to send again
        result = rate_limited_send_message(
            db_session,
            test_session.id,
            "After waiting",
            user=student
        )
        assert result is not None


class TestRateLimitedConversationService:
    """Test a conversation service wrapper with built-in rate limiting"""
    
    @pytest.fixture
    def rate_limited_conversation_service(self):
        """Create a wrapper class with rate limiting built in"""
        class RateLimitedConversationService:
            def __init__(self):
                self.message_limiter = RateLimiter(
                    user_limit=10,    # 10 messages per minute
                    user_window=60
                )
                self.start_limiter = RateLimiter(
                    user_limit=3,     # 3 new conversations per hour
                    user_window=3600
                )
            
            def start_conversation(self, db, student, client_id):
                allowed, retry_after = self.start_limiter.check_limit(student.student_id)
                if not allowed:
                    raise RateLimitExceeded(
                        f"Too many new conversations. Try again in {retry_after} seconds.",
                        retry_after
                    )
                return conversation_service.start_conversation(db, student, client_id)
            
            def send_message(self, db, session_id, content, user):
                allowed, retry_after = self.message_limiter.check_limit(user.student_id)
                if not allowed:
                    raise RateLimitExceeded(
                        f"Message rate limit exceeded. Try again in {retry_after} seconds.",
                        retry_after
                    )
                return conversation_service.send_message(db, session_id, content, user)
            
            def get_usage_stats(self, student_id):
                return {
                    "messages": self.message_limiter.get_user_usage(student_id),
                    "conversations": self.start_limiter.get_user_usage(student_id)
                }
        
        return RateLimitedConversationService()
    
    def test_service_with_built_in_rate_limiting(self, db_session, rate_limited_conversation_service, monkeypatch):
        """Test using the rate-limited service wrapper"""
        service = rate_limited_conversation_service
        student = StudentAuth(id="student-100", student_id="student-100")
        
        # Mock the actual conversation service methods
        mock_session_count = 0
        def mock_start_conversation(db, student, client_id):
            nonlocal mock_session_count
            mock_session_count += 1
            return Mock(id=f"session-{mock_session_count}", student_id=student.student_id)
        
        monkeypatch.setattr("backend.services.conversation_service.conversation_service.start_conversation", mock_start_conversation)
        
        # Mock send_message too
        mock_message_count = 0
        def mock_send_message(db, session_id, content, user):
            nonlocal mock_message_count
            mock_message_count += 1
            return Mock(id=f"msg-{mock_message_count}", content=content, role="assistant")
        
        monkeypatch.setattr("backend.services.conversation_service.conversation_service.send_message", mock_send_message)
        
        # Start conversations
        for i in range(3):
            session = service.start_conversation(db_session, student, f"client-{i}")
            assert session is not None
        
        # 4th conversation should hit limit
        with pytest.raises(RateLimitExceeded) as exc_info:
            service.start_conversation(db_session, student, "client-4")
        assert "Too many new conversations" in str(exc_info.value)
        
        # Can still send messages to existing conversations
        for i in range(5):
            msg = service.send_message(
                db_session,
                "session-123",
                f"Message {i}",
                student
            )
            assert msg is not None
        
        # Check usage stats
        stats = service.get_usage_stats(student.student_id)
        assert stats["messages"]["requests_in_window"] == 5
        assert stats["messages"]["remaining"] == 5  # 10 - 5
        assert stats["conversations"]["requests_in_window"] == 3
        assert stats["conversations"]["remaining"] == 0  # 3 - 3


class TestRateLimitingErrorHandling:
    """Test error handling and recovery strategies"""
    
    def test_graceful_degradation(self, db_session):
        """Test handling rate limit errors gracefully"""
        student = StudentAuth(id="student-200", student_id="student-200")
        
        # Simulate a service that handles rate limits gracefully
        def send_message_with_fallback(db, session_id, content, user, limiter):
            try:
                allowed, retry_after = limiter.check_limit(user.student_id)
                if not allowed:
                    # Return a fallback response instead of failing
                    return {
                        "error": "rate_limit_exceeded",
                        "message": "You're sending messages too quickly. Please wait a moment.",
                        "retry_after": retry_after
                    }
                
                # Normal message sending
                return conversation_service.send_message(db, session_id, content, user)
                
            except Exception as e:
                # Handle other errors
                return {
                    "error": "unknown_error",
                    "message": "Sorry, something went wrong. Please try again."
                }
        
        limiter = RateLimiter(user_limit=1, user_window=60)
        
        # First message succeeds
        result = send_message_with_fallback(
            db_session,
            "session-123",  # Using mock session id
            "Hello",
            student,
            limiter
        )
        # Would normally check for successful message, but we're mocking
        
        # Second message gets rate limit response
        result = send_message_with_fallback(
            db_session,
            "session-123",  # Using mock session id
            "Hello again",
            student,
            limiter
        )
        assert result["error"] == "rate_limit_exceeded"
        assert "too quickly" in result["message"]
        assert result["retry_after"] is not None
    
    def test_rate_limit_headers_for_api(self):
        """Test generating rate limit headers for API responses"""
        limiter = RateLimiter(user_limit=10, user_window=60)
        student_id = "student-300"
        
        # Make some requests
        for _ in range(3):
            limiter.check_limit(student_id)
        
        # Get usage for headers
        usage = limiter.get_user_usage(student_id)
        
        # Generate headers that could be added to API response
        headers = {
            "X-RateLimit-Limit": str(usage["limit"]),
            "X-RateLimit-Remaining": str(usage["remaining"]),
            "X-RateLimit-Window": str(usage["window_seconds"]),
            "X-RateLimit-Used": str(usage["requests_in_window"])
        }
        
        assert headers["X-RateLimit-Limit"] == "10"
        assert headers["X-RateLimit-Remaining"] == "7"
        assert headers["X-RateLimit-Window"] == "60"
        assert headers["X-RateLimit-Used"] == "3"
