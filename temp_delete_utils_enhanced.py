"""
Enhanced utilities for MVP Streamlit interfaces

Provides common functionality for all MVP pages with improved error handling and UI polish:
- Database connection with error handling
- Mock authentication
- Streamlit page configuration  
- Enhanced UI helpers with loading states
- Error handling utilities
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add backend to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.services.database import db_service
from backend.models.auth import TeacherAuth, StudentAuth


def get_database_connection() -> Session:
    """
    Get a database connection for use in Streamlit apps.
    
    Returns:
        Session: SQLAlchemy database session
        
    Note:
        In Streamlit, we need to be careful about session lifecycle.
        This returns a new session that should be used immediately.
    """
    return db_service.SessionLocal()


def get_mock_teacher() -> TeacherAuth:
    """
    Get mock teacher authentication for MVP testing.
    
    Returns:
        TeacherAuth: Mock teacher with ID teacher-1
    """
    return TeacherAuth(
        id="teacher-1",
        teacher_id="teacher-1"
    )


def get_mock_student() -> StudentAuth:
    """
    Get mock student authentication for MVP testing.
    
    Returns:
        StudentAuth: Mock student with ID student-1
    """
    return StudentAuth(
        id="student-1",
        student_id="student-1"
    )


def setup_page_config(
    page_title: str = "Virtual Client MVP",
    page_icon: str = "🎓",
    layout: str = "wide"
) -> None:
    """
    Configure Streamlit page settings.
    
    Args:
        page_title: Browser tab title
        page_icon: Emoji or image for browser tab
        layout: Page layout ("wide" or "centered")
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )


def show_error_message(message: str) -> None:
    """
    Display an error message to the user.
    
    Args:
        message: Error message to display
    """
    st.error(f"❌ {message}")


def show_success_message(message: str) -> None:
    """
    Display a success message to the user.
    
    Args:
        message: Success message to display
    """
    st.success(f"✅ {message}")


def show_info_message(message: str) -> None:
    """
    Display an informational message to the user.
    
    Args:
        message: Info message to display
    """
    st.info(f"ℹ️ {message}")


def show_warning_message(message: str) -> None:
    """
    Display a warning message to the user.
    
    Args:
        message: Warning message to display  
    """
    st.warning(f"⚠️ {message}")


def show_loading_message(message: str = "Loading...") -> None:
    """
    Display a loading message to the user.
    
    Args:
        message: Loading message to display
    """
    st.info(f"⏳ {message}")


def handle_api_error(error: Exception) -> str:
    """
    Convert API errors to user-friendly messages.
    
    Args:
        error: The exception that occurred
        
    Returns:
        User-friendly error message
    """
    error_msg = str(error)
    
    if "ANTHROPIC_API_KEY" in error_msg:
        return "Anthropic API key not configured. Please check your environment settings."
    elif "invalid x-api-key" in error_msg or "invalid api key" in error_msg.lower():
        return "Invalid API key. Please check your ANTHROPIC_API_KEY configuration."
    elif "rate limit" in error_msg.lower():
        return "Rate limit exceeded. Please wait a moment and try again."
    elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
        return "Unable to connect to the AI service. Please check your internet connection."
    elif "not found" in error_msg.lower():
        return "Requested resource not found. Please try again."
    else:
        return f"An unexpected error occurred: {error_msg}"


def safe_database_operation(operation_func, error_prefix: str = "Database operation failed"):
    """
    Safely execute a database operation with error handling.
    
    Args:
        operation_func: Function to execute that uses database
        error_prefix: Prefix for error messages
        
    Returns:
        Result of operation or None if failed
    """
    try:
        result = operation_func()
        return result
    except Exception as e:
        show_error_message(f"{error_prefix}: {handle_api_error(e)}")
        return None


def format_cost(cost: float) -> str:
    """
    Format cost for display.
    
    Args:
        cost: Cost in dollars
        
    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.00:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


def format_tokens(tokens: int) -> str:
    """
    Format token count for display.
    
    Args:
        tokens: Number of tokens
        
    Returns:
        Formatted token string
    """
    if tokens < 1000:
        return str(tokens)
    else:
        return f"{tokens:,}"


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        db = get_database_connection()
        # Try a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        show_error_message(f"Database connection failed: {handle_api_error(e)}")
        return False


def check_api_configuration() -> Dict[str, bool]:
    """
    Check if required API configurations are present.
    
    Returns:
        Dictionary with configuration status
    """
    config_status = {
        'anthropic_api_key': bool(os.getenv("ANTHROPIC_API_KEY")),
        'database_url': bool(os.getenv("DATABASE_URL")) or True,  # SQLite is default
    }
    return config_status


def display_configuration_warnings():
    """
    Display warnings for missing configuration.
    """
    config = check_api_configuration()
    
    if not config['anthropic_api_key']:
        show_warning_message(
            "Anthropic API key not configured. Conversations will not work without setting ANTHROPIC_API_KEY."
        )
        with st.expander("📋 Setup Instructions"):
            st.code("""
# Create a .env file in the project root with:
ANTHROPIC_API_KEY=your_api_key_here

# Or set environment variable:
export ANTHROPIC_API_KEY=your_api_key_here
            """)


def initialize_session_state() -> None:
    """
    Initialize common session state variables.
    """
    # Initialize if not already present
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.total_cost = 0.0
        st.session_state.total_tokens = 0
        st.session_state.last_error = None
        st.session_state.loading = False


def clear_error_state():
    """
    Clear any error state from session.
    """
    if 'last_error' in st.session_state:
        st.session_state.last_error = None


def set_loading_state(loading: bool, message: str = ""):
    """
    Set loading state for UI feedback.
    
    Args:
        loading: Whether currently loading
        message: Optional loading message
    """
    st.session_state.loading = loading
    if loading and message:
        st.session_state.loading_message = message


# Enhanced UI components
def render_chat_message(role: str, content: str, tokens: Optional[int] = None, timestamp: Optional[str] = None) -> None:
    """
    Render a chat message in the UI with enhanced formatting.
    
    Args:
        role: Message role ("user" or "assistant")
        content: Message content
        tokens: Optional token count to display
        timestamp: Optional timestamp to display
    """
    if role == "user":
        with st.chat_message("user", avatar="🧑"):
            st.write(content)
            if tokens or timestamp:
                caption_parts = []
                if tokens:
                    caption_parts.append(f"Tokens: {format_tokens(tokens)}")
                if timestamp:
                    caption_parts.append(f"Time: {timestamp}")
                st.caption(" | ".join(caption_parts))
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(content)
            if tokens or timestamp:
                caption_parts = []
                if tokens:
                    caption_parts.append(f"Tokens: {format_tokens(tokens)}")
                if timestamp:
                    caption_parts.append(f"Time: {timestamp}")
                st.caption(" | ".join(caption_parts))


def render_loading_placeholder(message: str = "Loading data..."):
    """
    Render a loading placeholder with spinner.
    
    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        st.empty()  # Placeholder that will be replaced


def render_metric_card(label: str, value: Any, delta: Optional[Any] = None) -> None:
    """
    Render a metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator
    """
    st.metric(label=label, value=value, delta=delta)


def render_status_indicator(status: str, label: str = "") -> None:
    """
    Render a status indicator with color coding.
    
    Args:
        status: Status value ('active', 'completed', 'error', etc.)
        label: Optional label to display
    """
    status_config = {
        'active': ('🟢', 'Active'),
        'completed': ('✅', 'Completed'),
        'error': ('🔴', 'Error'),
        'inactive': ('⚪', 'Inactive'),
        'loading': ('🟡', 'Loading'),
        'healthy': ('🟢', 'Healthy'),
        'degraded': ('🟡', 'Degraded'),
        'unavailable': ('🔴', 'Unavailable')
    }
    
    emoji, default_label = status_config.get(status.lower(), ('⚪', status.title()))
    display_label = label or default_label
    st.write(f"{emoji} {display_label}")


# Constants for MVP
DEFAULT_MODEL = "claude-3-haiku-20240307"  # Cheap model for testing
DEFAULT_MAX_TOKENS = 150  # Keep responses short for MVP
DEFAULT_TEMPERATURE = 0.7  # Balanced creativity

# Cost constants (per 1000 tokens)
MODEL_COSTS = {
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}
}


def estimate_conversation_cost(
    messages_count: int, 
    avg_tokens_per_message: int = 50,
    model: str = DEFAULT_MODEL
) -> float:
    """
    Estimate the cost of a conversation.
    
    Args:
        messages_count: Number of messages
        avg_tokens_per_message: Average tokens per message
        model: Model being used
        
    Returns:
        Estimated cost in dollars
    """
    total_tokens = messages_count * avg_tokens_per_message
    costs = MODEL_COSTS.get(model, MODEL_COSTS[DEFAULT_MODEL])
    
    # Assume 50/50 input/output split
    input_tokens = total_tokens // 2
    output_tokens = total_tokens // 2
    
    cost = (input_tokens * costs["input"] / 1000) + (output_tokens * costs["output"] / 1000)
    return cost


if __name__ == "__main__":
    # Quick test of enhanced utilities
    print("Testing Enhanced MVP utilities...")
    
    # Test database connection
    try:
        db = get_database_connection()
        print("✅ Database connection successful")
        db.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test mock auth
    teacher = get_mock_teacher()
    student = get_mock_student()
    print(f"✅ Mock teacher: ID={teacher.teacher_id}")
    print(f"✅ Mock student: ID={student.student_id}")
    
    # Test cost formatting
    print(f"✅ Cost formatting: {format_cost(0.0045)} (should be $0.0045)")
    print(f"✅ Token formatting: {format_tokens(1234)} (should be 1,234)")
    
    # Test configuration check
    config = check_api_configuration()
    print(f"✅ Configuration check: {config}")
    
    print("\nAll enhanced utilities tested!")
