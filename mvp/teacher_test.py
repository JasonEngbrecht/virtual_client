"""
Teacher Test Interface - MVP

Allows teachers to:
1. Create/edit client profiles
2. Test conversations with clients
3. View conversation history and metrics
4. Export conversations for feedback

Part of the MVP to validate conversation quality.
"""

import streamlit as st
from typing import Optional
from utils import (
    setup_page_config,
    show_info_message,
    show_error_message,
    show_success_message,
    initialize_session_state,
    get_database_connection,
    get_mock_teacher,
    get_mock_student,
    render_chat_message,
    format_tokens,
    format_cost
)

# Import backend models and services
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.models.client_profile import (
    ClientProfileCreate,
    ClientProfile,
    PREDEFINED_ISSUES,
    PERSONALITY_TRAITS,
    COMMUNICATION_STYLES
)
from backend.services.client_service import client_service
from backend.services.conversation_service import conversation_service
from backend.models.auth import StudentAuth


def create_client_form():
    """Create the client profile form"""
    st.subheader("📝 Create New Client")
    
    with st.form("client_form", clear_on_submit=True):
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name*", placeholder="e.g., Maria Rodriguez")
            age = st.number_input("Age*", min_value=1, max_value=120, value=35)
            gender = st.selectbox(
                "Gender", 
                ["", "Female", "Male", "Non-binary", "Other", "Prefer not to say"],
                index=0
            )
        
        with col2:
            race = st.selectbox(
                "Race/Ethnicity",
                ["", "White", "Black/African American", "Hispanic/Latino", 
                 "Asian", "Native American", "Pacific Islander", "Mixed", "Other"],
                index=0
            )
            socioeconomic_status = st.selectbox(
                "Socioeconomic Status",
                ["", "Low income", "Working class", "Middle class", "Upper middle class", "Wealthy"],
                index=0
            )
            communication_style = st.selectbox(
                "Communication Style",
                [""] + COMMUNICATION_STYLES,
                index=0
            )
        
        # Issues (Multi-select)
        st.write("**Issues/Challenges** (Select all that apply)")
        issues = st.multiselect(
            "Issues",
            PREDEFINED_ISSUES,
            format_func=lambda x: x.replace("_", " ").title(),
            label_visibility="collapsed"
        )
        
        # Personality Traits (Multi-select)
        st.write("**Personality Traits** (Select 2-5 traits)")
        personality_traits = st.multiselect(
            "Personality Traits",
            PERSONALITY_TRAITS,
            format_func=lambda x: x.replace("_", " ").title(),
            label_visibility="collapsed"
        )
        
        # Background Story
        background_story = st.text_area(
            "Background Story",
            placeholder="Describe the client's background, history, and current situation...",
            height=150
        )
        
        # Submit button
        submitted = st.form_submit_button("Create Client", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not name:
                show_error_message("Name is required")
                return None
            
            if len(personality_traits) < 2:
                show_error_message("Please select at least 2 personality traits")
                return None
            
            if len(personality_traits) > 5:
                show_error_message("Please select no more than 5 personality traits")
                return None
            
            # Create client data
            client_data = ClientProfileCreate(
                name=name,
                age=age,
                race=race if race else None,
                gender=gender if gender else None,
                socioeconomic_status=socioeconomic_status if socioeconomic_status else None,
                issues=issues,
                background_story=background_story if background_story else None,
                personality_traits=personality_traits,
                communication_style=communication_style if communication_style else None
            )
            
            return client_data
    
    return None


def display_client_list(teacher_id: str):
    """Display list of clients created by this teacher"""
    st.subheader("👥 Your Clients")
    
    try:
        db = get_database_connection()
        clients = client_service.get_teacher_clients(db, teacher_id)
        
        if not clients:
            show_info_message("No clients created yet. Create your first client above!")
            return
        
        # Display clients in a grid
        for i in range(0, len(clients), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(clients):
                    client = clients[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"### {client.name}")
                            st.write(f"**Age:** {client.age} | **Gender:** {client.gender or 'Not specified'}")
                            
                            if client.issues:
                                issues_display = ", ".join([issue.replace("_", " ").title() for issue in client.issues[:3]])
                                if len(client.issues) > 3:
                                    issues_display += f" (+{len(client.issues) - 3} more)"
                                st.write(f"**Issues:** {issues_display}")
                            
                            if client.personality_traits:
                                traits_display = ", ".join([trait.replace("_", " ").title() for trait in client.personality_traits[:3]])
                                if len(client.personality_traits) > 3:
                                    traits_display += f" (+{len(client.personality_traits) - 3} more)"
                                st.write(f"**Traits:** {traits_display}")
                            
                            # View details expander
                            with st.expander("View Full Details"):
                                st.write(f"**Race/Ethnicity:** {client.race or 'Not specified'}")
                                st.write(f"**Socioeconomic Status:** {client.socioeconomic_status or 'Not specified'}")
                                st.write(f"**Communication Style:** {client.communication_style or 'Not specified'}")
                                
                                if client.background_story:
                                    st.write("**Background Story:**")
                                    st.write(client.background_story)
                                
                                if client.issues:
                                    st.write("**All Issues:**")
                                    for issue in client.issues:
                                        st.write(f"- {issue.replace('_', ' ').title()}")
                                
                                if client.personality_traits:
                                    st.write("**All Personality Traits:**")
                                    for trait in client.personality_traits:
                                        st.write(f"- {trait.replace('_', ' ').title()}")
                            
                            # Action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"Test Conversation", key=f"test_{client.id}"):
                                    st.session_state.selected_client_id = client.id
                                    st.session_state.selected_client_name = client.name
                                    show_info_message(f"Selected {client.name} for testing. Feature coming in Part 3!")
                            
                            st.divider()
        
    except Exception as e:
        show_error_message(f"Error loading clients: {str(e)}")
    finally:
        db.close()


def main():
    # Configure page
    setup_page_config(
        page_title="Teacher Test - Virtual Client",
        page_icon="👩‍🏫"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get mock teacher
    teacher = get_mock_teacher()
    
    st.title("👩‍🏫 Teacher Test Interface")
    
    # Add tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Create Client", "Test Conversations", "View History"])
    
    with tab1:
        # Client creation form
        client_data = create_client_form()
        
        if client_data:
            try:
                db = get_database_connection()
                new_client = client_service.create_client_for_teacher(
                    db, client_data, teacher.teacher_id
                )
                show_success_message(f"Successfully created client: {new_client.name}")
                st.rerun()  # Refresh to show new client in list
            except Exception as e:
                show_error_message(f"Error creating client: {str(e)}")
            finally:
                db.close()
        
        st.divider()
        
        # Display existing clients
        display_client_list(teacher.teacher_id)
    
    with tab2:
        # Conversation testing interface
        if not hasattr(st.session_state, 'selected_client_id'):
            show_info_message("Please select a client from the 'Create Client' tab first.")
        else:
            # Display selected client info
            st.subheader(f"💬 Test Conversation with {st.session_state.selected_client_name}")
            
            # Initialize conversation-specific session state
            if 'conversation_active' not in st.session_state:
                st.session_state.conversation_active = False
            if 'current_session_id' not in st.session_state:
                st.session_state.current_session_id = None
            if 'conversation_messages' not in st.session_state:
                st.session_state.conversation_messages = []
            if 'conversation_cost' not in st.session_state:
                st.session_state.conversation_cost = 0.0
            if 'conversation_tokens' not in st.session_state:
                st.session_state.conversation_tokens = 0
            
            # Conversation controls
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if not st.session_state.conversation_active:
                    if st.button("🚀 Start Test Conversation", type="primary", use_container_width=True):
                        try:
                            # Use mock student for teacher testing
                            mock_student = get_mock_student()
                            
                            # Start the conversation
                            db = get_database_connection()
                            session = conversation_service.start_conversation(
                                db=db,
                                student=mock_student,
                                client_id=st.session_state.selected_client_id
                            )
                            
                            # Update session state
                            st.session_state.conversation_active = True
                            st.session_state.current_session_id = session.id
                            st.session_state.conversation_messages = []
                            st.session_state.conversation_cost = session.estimated_cost or 0.0
                            st.session_state.conversation_tokens = session.total_tokens or 0
                            
                            # Get initial greeting from messages
                            from backend.services.session_service import session_service
                            messages = session_service.get_messages(
                                db=db,
                                session_id=session.id
                            )
                            
                            if messages:
                                for msg in messages:
                                    st.session_state.conversation_messages.append({
                                        'role': msg.role,
                                        'content': msg.content,
                                        'tokens': msg.token_count
                                    })
                            
                            show_success_message("Conversation started! The client has greeted you.")
                            st.rerun()
                            
                        except Exception as e:
                            error_msg = str(e)
                            if "ANTHROPIC_API_KEY" in error_msg:
                                show_error_message(
                                    "Anthropic API key not configured. Please set the ANTHROPIC_API_KEY "
                                    "environment variable to enable conversations."
                                )
                            else:
                                show_error_message(f"Failed to start conversation: {error_msg}")
                        finally:
                            db.close()
                else:
                    if st.button("🛑 End Conversation", type="secondary", use_container_width=True):
                        try:
                            # End the conversation
                            db = get_database_connection()
                            mock_student = get_mock_student()
                            
                            ended_session = conversation_service.end_conversation(
                                db=db,
                                session_id=st.session_state.current_session_id,
                                user=mock_student,
                                session_notes="Teacher test conversation"
                            )
                            
                            # Reset session state
                            st.session_state.conversation_active = False
                            st.session_state.current_session_id = None
                            
                            show_success_message(f"Conversation ended. Total cost: {format_cost(ended_session.estimated_cost or 0)}")
                            st.rerun()
                            
                        except Exception as e:
                            show_error_message(f"Failed to end conversation: {str(e)}")
                        finally:
                            db.close()
            
            with col2:
                if st.session_state.conversation_active:
                    st.write(f"**Session ID:** {st.session_state.current_session_id[:8]}...")
                else:
                    st.write("**Status:** No active conversation")
            
            with col3:
                # Display metrics
                if st.session_state.conversation_active:
                    st.metric("Total Tokens", format_tokens(st.session_state.conversation_tokens))
                    st.metric("Est. Cost", format_cost(st.session_state.conversation_cost))
            
            st.divider()
            
            # Conversation interface
            if st.session_state.conversation_active:
                # Display conversation history
                st.write("### Conversation History")
                
                # Create a container for messages
                message_container = st.container()
                
                with message_container:
                    for msg in st.session_state.conversation_messages:
                        render_chat_message(
                            role=msg['role'],
                            content=msg['content'],
                            tokens=msg.get('tokens')
                        )
                
                # Message input
                with st.form("message_form", clear_on_submit=True):
                    user_input = st.text_area(
                        "Your message:",
                        placeholder="Type your message here...",
                        height=100,
                        key="message_input"
                    )
                    
                    col1, col2 = st.columns([6, 1])
                    with col2:
                        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
                    
                    if send_button and user_input:
                        try:
                            # Send the message
                            db = get_database_connection()
                            mock_student = get_mock_student()
                            
                            # Add user message to UI immediately
                            st.session_state.conversation_messages.append({
                                'role': 'user',
                                'content': user_input,
                                'tokens': None  # Will be calculated by service
                            })
                            
                            # Get AI response
                            with st.spinner("Client is thinking..."):
                                ai_message = conversation_service.send_message(
                                    db=db,
                                    session_id=st.session_state.current_session_id,
                                    content=user_input,
                                    user=mock_student
                                )
                            
                            # Add AI response to conversation
                            st.session_state.conversation_messages.append({
                                'role': ai_message.role,
                                'content': ai_message.content,
                                'tokens': ai_message.token_count
                            })
                            
                            # Update metrics
                            from backend.services.session_service import session_service
                            session_db = session_service.get_session(
                                db=db,
                                session_id=st.session_state.current_session_id
                            )
                            st.session_state.conversation_cost = session_db.estimated_cost or 0.0
                            st.session_state.conversation_tokens = session_db.total_tokens or 0
                            
                            st.rerun()
                            
                        except Exception as e:
                            error_msg = str(e)
                            if "ANTHROPIC_API_KEY" in error_msg:
                                show_error_message(
                                    "Anthropic API key not configured. Cannot send messages without API access."
                                )
                            else:
                                show_error_message(f"Failed to send message: {error_msg}")
                        finally:
                            db.close()
            
            else:
                # Show instructions when no conversation is active
                st.info(
                    "Start a test conversation to interact with the virtual client. "
                    "The client will respond based on their profile and personality traits."
                )
    
    with tab3:
        show_info_message("Conversation history and metrics will be implemented in Part 4!")


if __name__ == "__main__":
    main()
