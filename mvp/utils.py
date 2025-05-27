"""
Shared utilities for MVP Streamlit interfaces

Provides common functionality for all MVP pages:
- Database connection
- Mock authentication
- Streamlit page configuration
- Shared UI helpers
"""

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


def create_sidebar_navigation() -> str:
    """
    Create standard sidebar navigation for MVP pages.
    
    Returns:
        Selected page name
    """
    with st.sidebar:
        st.title("Virtual Client MVP")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Teacher Test", "Student Practice", "Admin Monitor"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Mock user info
        st.caption("Mock Authentication")
        if "Teacher" in page:
            user = get_mock_teacher()
            st.write(f"👩‍🏫 Teacher ID: {user.teacher_id}")
        elif "Student" in page:
            user = get_mock_student()
            st.write(f"🎓 Student ID: {user.student_id}")
        else:
            st.write(f"👤 Admin User")
        
        st.divider()
        
        # Quick stats placeholder
        st.caption("Session Info")
        st.write("Sessions Today: --")
        st.write("Total Cost: --")
        
        return page


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
        st.error(f"Database connection failed: {str(e)}")
        return False


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


# Reusable UI components
def render_chat_message(role: str, content: str, tokens: Optional[int] = None) -> None:
    """
    Render a chat message in the UI.
    
    Args:
        role: Message role ("user" or "assistant")
        content: Message content
        tokens: Optional token count to display
    """
    if role == "user":
        with st.chat_message("user", avatar="🧑"):
            st.write(content)
            if tokens:
                st.caption(f"Tokens: {format_tokens(tokens)}")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(content)
            if tokens:
                st.caption(f"Tokens: {format_tokens(tokens)}")


def render_metric_card(label: str, value: Any, delta: Optional[Any] = None) -> None:
    """
    Render a metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator
    """
    st.metric(label=label, value=value, delta=delta)


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
    # Quick test of utilities
    print("Testing MVP utilities...")
    
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
    
    print("\nAll utilities tested!")
