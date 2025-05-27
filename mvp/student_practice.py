"""
Student Practice Interface - MVP

Allows students to:
1. View available clients
2. Start practice conversations
3. Chat with virtual clients
4. End sessions when complete

Part of the MVP to validate the student experience.
"""

import streamlit as st
from utils import (
    setup_page_config,
    show_info_message,
    initialize_session_state
)


def main():
    # Configure page
    setup_page_config(
        page_title="Student Practice - Virtual Client",
        page_icon="🎓"
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.title("🎓 Student Practice Interface")
    
    show_info_message("Student interface coming in Part 5 of implementation!")
    
    st.write("""
    This interface will allow students to:
    - Browse available virtual clients
    - Start practice conversations
    - Chat with AI-powered clients
    - Track session duration
    - End sessions when ready
    """)


if __name__ == "__main__":
    main()
