"""
Student Practice Interface - Streamlit app for students to practice conversations
"""
import streamlit as st
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from mvp.utils import (
    get_database_connection,
    get_mock_student,
    setup_page_config,
    show_error_message,
    show_success_message,
    show_info_message,
    render_chat_message,
    format_tokens,
    format_cost
)
from backend.services.client_service import client_service
from backend.services.session_service import session_service
from backend.services.conversation_service import conversation_service
from backend.models.client_profile import ClientProfile
from backend.models.session import Session


def display_client_card(client: ClientProfile, active_session: Optional[Session] = None):
    """Display a client card with information and action button"""
    with st.container():
        # Card styling
        st.markdown(
            """
            <style>
            .client-card {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                background-color: #f9f9f9;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Card content
        st.markdown('<div class="client-card">', unsafe_allow_html=True)
        
        # Client name and basic info
        st.markdown(f"### {client.name}")
        st.markdown(f"**Age:** {client.age} | **Gender:** {client.gender or 'Not specified'}")
        
        # Issues or background story preview (truncated)
        if client.issues:
            issues_display = ", ".join([issue.replace("_", " ").title() for issue in client.issues[:2]])
            if len(client.issues) > 2:
                issues_display += f" (+{len(client.issues) - 2} more)"
            st.markdown(f"**Issues:** {issues_display}")
        elif client.background_story:
            story_preview = client.background_story[:150] + "..." if len(client.background_story) > 150 else client.background_story
            st.markdown(f"**Background:** {story_preview}")
        
        # Personality traits
        if client.personality_traits:
            traits_str = ", ".join([trait.replace("_", " ").title() for trait in client.personality_traits[:3]])
            if len(client.personality_traits) > 3:
                traits_str += f" (+{len(client.personality_traits) - 3} more)"
            st.markdown(f"**Personality:** {traits_str}")
        
        # Action button
        if active_session:
            if st.button(f"Continue Conversation", key=f"continue_{client.id}"):
                # Store session info and switch to conversation view
                st.session_state.active_session_id = active_session.id
                st.session_state.selected_client_id = client.id
                st.session_state.view = "conversation"
                st.rerun()
        else:
            if st.button(f"Start Conversation", key=f"start_{client.id}"):
                # Start a new conversation
                db = None
                try:
                    db = get_database_connection()
                    student = get_mock_student()
                    
                    # Use conversation service to start the conversation
                    session = conversation_service.start_conversation(
                        db=db,
                        student=student,
                        client_id=client.id
                    )
                    
                    # Store session info and switch to conversation view
                    st.session_state.active_session_id = session.id
                    st.session_state.selected_client_id = client.id
                    st.session_state.view = "conversation"
                    show_success_message(f"Started conversation with {client.name}")
                    st.rerun()
                    
                except Exception as e:
                    show_error_message(f"Error starting conversation: {str(e)}")
                finally:
                    if db:
                        db.close()
        
        st.markdown('</div>', unsafe_allow_html=True)


def display_conversation_interface():
    """Display the conversation interface for students"""
    # Get student auth
    student = get_mock_student()
    
    # Initialize conversation-specific session state
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = []
    if 'conversation_cost' not in st.session_state:
        st.session_state.conversation_cost = 0.0
    if 'conversation_tokens' not in st.session_state:
        st.session_state.conversation_tokens = 0
    if 'conversation_start_time' not in st.session_state:
        st.session_state.conversation_start_time = datetime.now()
    
    # Get client information
    db = None
    try:
        db = get_database_connection()
        client = client_service.get(db, st.session_state.selected_client_id)
        if not client:
            show_error_message("Client not found")
            st.button("← Back to Client Selection", on_click=lambda: setattr(st.session_state, 'view', 'client_selection'))
            return
        
        # Header with client info
        st.header(f"💬 Conversation with {client.name}")
        
        # Get session info and messages if not already loaded
        if not st.session_state.conversation_messages and st.session_state.active_session_id:
            session = session_service.get_session(db, st.session_state.active_session_id)
            if session:
                st.session_state.conversation_cost = session.estimated_cost or 0.0
                st.session_state.conversation_tokens = session.total_tokens or 0
                st.session_state.conversation_start_time = session.started_at
                
                # Load existing messages
                messages = session_service.get_messages(db, st.session_state.active_session_id)
                for msg in messages:
                    st.session_state.conversation_messages.append({
                        'role': msg.role,
                        'content': msg.content,
                        'tokens': msg.token_count
                    })
        
        # Conversation controls and metrics
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            if st.button("🛑 End Session", type="secondary", use_container_width=True):
                try:
                    # End the conversation
                    ended_session = conversation_service.end_conversation(
                        db=db,
                        session_id=st.session_state.active_session_id,
                        user=student,
                        session_notes="Student practice session"
                    )
                    
                    # Clear session state
                    st.session_state.active_session_id = None
                    st.session_state.conversation_messages = []
                    st.session_state.view = "client_selection"
                    
                    show_success_message(f"Session ended. Total cost: {format_cost(ended_session.estimated_cost or 0)}")
                    st.rerun()
                    
                except Exception as e:
                    show_error_message(f"Failed to end session: {str(e)}")
        
        with col2:
            # Calculate session duration
            duration = datetime.now() - st.session_state.conversation_start_time
            duration_minutes = int(duration.total_seconds() // 60)
            st.metric("Session Duration", f"{duration_minutes} min")
        
        with col3:
            st.metric("Total Tokens", format_tokens(st.session_state.conversation_tokens))
        
        with col4:
            st.metric("Cost", format_cost(st.session_state.conversation_cost))
        
        st.divider()
        
        # Display conversation history
        st.subheader("Conversation")
        
        # Create a container for messages
        message_container = st.container()
        
        with message_container:
            for msg in st.session_state.conversation_messages:
                render_chat_message(
                    role=msg['role'],
                    content=msg['content'],
                    tokens=msg.get('tokens')
                )
        
        # Message input form
        with st.form("message_form", clear_on_submit=True):
            user_input = st.text_area(
                "Your message:",
                placeholder="Type your message here...",
                height=100,
                key="student_message_input"
            )
            
            col1, col2 = st.columns([6, 1])
            with col2:
                send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
            
            if send_button and user_input:
                try:
                    # Add user message to UI immediately
                    st.session_state.conversation_messages.append({
                        'role': 'user',
                        'content': user_input,
                        'tokens': None
                    })
                    
                    # Get AI response
                    with st.spinner(f"{client.name} is typing..."):
                        ai_message = conversation_service.send_message(
                            db=db,
                            session_id=st.session_state.active_session_id,
                            content=user_input,
                            user=student
                        )
                    
                    # Add AI response to conversation
                    st.session_state.conversation_messages.append({
                        'role': ai_message.role,
                        'content': ai_message.content,
                        'tokens': ai_message.token_count
                    })
                    
                    # Update metrics
                    session = session_service.get_session(db, st.session_state.active_session_id)
                    st.session_state.conversation_cost = session.estimated_cost or 0.0
                    st.session_state.conversation_tokens = session.total_tokens or 0
                    
                    st.rerun()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "ANTHROPIC_API_KEY" in error_msg:
                        show_error_message(
                            "Anthropic API key not configured. Please contact your instructor."
                        )
                    else:
                        show_error_message(f"Failed to send message: {error_msg}")
        
        # Back button at the bottom
        st.markdown("---")
        if st.button("← Back to Client Selection"):
            st.session_state.view = "client_selection"
            st.rerun()
            
    except Exception as e:
        show_error_message(f"Error in conversation interface: {str(e)}")
        if st.button("← Back to Client Selection"):
            st.session_state.view = "client_selection"
            st.rerun()
    finally:
        if db:
            db.close()


def main():
    # Page setup
    setup_page_config("Student Practice", "🎭")
    
    # Get mock student auth
    student = get_mock_student()
    
    # Header
    st.title("🎭 Practice Conversations")
    st.markdown(f"**Student ID:** {student.student_id}")
    st.markdown("---")
    
    # Initialize session state
    if "view" not in st.session_state:
        st.session_state.view = "client_selection"
    
    # Navigation based on view
    if st.session_state.view == "conversation":
        display_conversation_interface()
        return
    
    # Client Selection View
    st.header("Select a Client to Practice With")
    
    try:
        # Get database connection
        db = get_database_connection()
        
        # Get all available clients (from all teachers for MVP)
        # In production, this would be filtered by assignment/section
        all_clients = []
        
        # For MVP, we'll get clients from teacher-1 (our mock teacher)
        # In production, this would come from assignments
        teacher_clients = client_service.get_teacher_clients(db, "teacher-1")
        all_clients.extend(teacher_clients)
        
        if not all_clients:
            st.info("No clients available for practice yet. Please ask your teacher to create some clients.")
            return
        
        # Get active sessions for this student
        active_sessions = session_service.get_student_sessions(
            db, 
            student.student_id, 
            status="active"
        )
        
        # Create a map of client_id to active session
        active_session_map = {
            session.client_profile_id: session 
            for session in active_sessions
        }
        
        # Display clients in a grid
        st.markdown(f"**Available Clients:** {len(all_clients)}")
        
        # Create columns for grid layout
        cols = st.columns(2)
        
        for idx, client in enumerate(all_clients):
            with cols[idx % 2]:
                active_session = active_session_map.get(client.id)
                display_client_card(client, active_session)
        
        # Show summary of active conversations
        if active_sessions:
            st.markdown("---")
            st.subheader(f"Active Conversations ({len(active_sessions)})")
            for session in active_sessions:
                # Find the client for this session
                client = next((c for c in all_clients if c.id == session.client_profile_id), None)
                if client:
                    st.markdown(f"- **{client.name}** - Started {session.started_at.strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        show_error_message(f"Error loading clients: {str(e)}")
        st.error("Please make sure the database is properly initialized.")
    
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()
