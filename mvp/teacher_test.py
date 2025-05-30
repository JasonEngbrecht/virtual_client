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
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import io
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from mvp.utils import (
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
    format_cost,
    handle_api_error,
    display_configuration_warnings
)

from backend.models.client_profile import (
    ClientProfileCreate,
    ClientProfile,
    PREDEFINED_ISSUES,
    PERSONALITY_TRAITS,
    COMMUNICATION_STYLES
)
from backend.services.client_service import client_service
from backend.services.conversation_service import conversation_service
from backend.services.session_service import session_service
from backend.models.auth import StudentAuth
from backend.models.session import SessionDB
from backend.models.message import MessageDB
from backend.services.prompt_service import prompt_service


# Available models and their pricing (input/output per 1M tokens)
AVAILABLE_MODELS = {
    "claude-3-haiku-20240307": {
        "name": "Claude 3 Haiku",
        "description": "Fast and efficient for testing",
        "input_cost": 0.25,
        "output_cost": 1.25,
        "recommended_for": "Development & Testing"
    },
    "claude-3-5-sonnet-20241022": {
        "name": "Claude 3.5 Sonnet", 
        "description": "Balanced performance and cost",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "recommended_for": "General Use"
    },
    "claude-3-sonnet-20240229": {
        "name": "Claude 3 Sonnet",
        "description": "Higher quality responses", 
        "input_cost": 3.00,
        "output_cost": 15.00,
        "recommended_for": "Production"
    },
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "description": "Highest quality, most expensive",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "recommended_for": "Premium Use"
    }
}

DEFAULT_MODEL = "claude-3-haiku-20240307"


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


def fetch_conversation_history(teacher_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all conversation sessions for a teacher's test conversations.
    
    Args:
        teacher_id: The teacher's ID
        
    Returns:
        List of conversation sessions with client info
    """
    conversations = []
    
    try:
        db = get_database_connection()
        
        # Get mock student ID (teacher test conversations use this)
        mock_student = get_mock_student()
        
        # Get all sessions for the mock student (these are teacher test sessions)
        sessions = session_service.get_student_sessions(
            db=db,
            student_id=mock_student.student_id,
            limit=100  # Get up to 100 conversations
        )
        
        # Enrich with client information
        for session in sessions:
            client = client_service.get(db, session.client_profile_id)
            if client:
                conversations.append({
                    'session': session,
                    'client': client,
                    'messages': session_service.get_messages(db, session.id)
                })
        
        return conversations
        
    except Exception as e:
        show_error_message(f"Error fetching conversation history: {str(e)}")
        return []
    finally:
        if 'db' in locals():
            db.close()


def calculate_conversation_metrics(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregate metrics from conversation history.
    
    Args:
        conversations: List of conversation data
        
    Returns:
        Dictionary with calculated metrics
    """
    if not conversations:
        return {
            'total_conversations': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'avg_cost_per_conversation': 0.0,
            'avg_tokens_per_conversation': 0,
            'avg_messages_per_conversation': 0,
            'avg_response_time': None
        }
    
    total_conversations = len(conversations)
    total_cost = sum(conv['session'].estimated_cost or 0.0 for conv in conversations)
    total_tokens = sum(conv['session'].total_tokens or 0 for conv in conversations)
    
    # Calculate average response times
    response_times = []
    for conv in conversations:
        messages = conv.get('messages', [])
        if messages and len(messages) >= 2:
            # Look for user messages followed by assistant responses
            for i in range(len(messages) - 1):
                if messages[i].role == 'user' and messages[i + 1].role == 'assistant':
                    time_diff = (messages[i + 1].timestamp - messages[i].timestamp).total_seconds()
                    response_times.append(time_diff)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    
    total_messages = sum(len(conv.get('messages', [])) for conv in conversations)
    
    return {
        'total_conversations': total_conversations,
        'total_cost': total_cost,
        'total_tokens': total_tokens,
        'avg_cost_per_conversation': total_cost / total_conversations if total_conversations > 0 else 0.0,
        'avg_tokens_per_conversation': total_tokens // total_conversations if total_conversations > 0 else 0,
        'avg_messages_per_conversation': total_messages // total_conversations if total_conversations > 0 else 0,
        'avg_response_time': avg_response_time
    }


def format_conversation_export(conversation: Dict[str, Any]) -> str:
    """
    Format a conversation for export as markdown.
    
    Args:
        conversation: Conversation data with session, client, and messages
        
    Returns:
        Markdown formatted string
    """
    session = conversation['session']
    client = conversation['client']
    messages = conversation.get('messages', [])
    
    # Start building the export
    export_lines = [
        f"# Conversation Export",
        f"\n## Session Information",
        f"- **Session ID**: {session.id}",
        f"- **Client**: {client.name}",
        f"- **Started**: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Ended**: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S') if session.ended_at else 'Active'}",
        f"- **Status**: {session.status}",
        f"- **Total Tokens**: {format_tokens(session.total_tokens or 0)}",
        f"- **Estimated Cost**: {format_cost(session.estimated_cost or 0.0)}",
        f"\n## Client Profile",
        f"- **Name**: {client.name}",
        f"- **Age**: {client.age}",
        f"- **Gender**: {client.gender or 'Not specified'}",
        f"- **Issues**: {', '.join(client.issues) if client.issues else 'None specified'}",
        f"- **Personality Traits**: {', '.join(client.personality_traits) if client.personality_traits else 'None specified'}",
        f"\n## Conversation Transcript\n"
    ]
    
    # Add messages
    for msg in messages:
        timestamp = msg.timestamp.strftime('%H:%M:%S')
        role = "Student" if msg.role == "user" else "Client"
        tokens_info = f" ({msg.token_count} tokens)" if msg.token_count else ""
        
        export_lines.append(f"**[{timestamp}] {role}**{tokens_info}:")
        export_lines.append(f"{msg.content}")
        export_lines.append("")  # Empty line for readability
    
    # Add session notes if any
    if session.session_notes:
        export_lines.extend([
            f"\n## Session Notes",
            f"{session.session_notes}"
        ])
    
    return "\n".join(export_lines)


def show_conversation_setup():
    """
    Show conversation setup interface with prompt preview/editing and model selection.
    
    Returns:
        Tuple of (ready_to_start: bool, system_prompt: str, selected_model: str)
    """
    st.subheader(f"🔧 Conversation Setup for {st.session_state.selected_client_name}")
    
    # Get the client for prompt generation
    try:
        db = get_database_connection()
        client = client_service.get(db, st.session_state.selected_client_id)
        if not client:
            show_error_message("Client not found")
            return False, "", DEFAULT_MODEL
    except Exception as e:
        show_error_message(f"Error loading client: {str(e)}")
        return False, "", DEFAULT_MODEL
    finally:
        db.close()
    
    # Generate default system prompt
    default_prompt = prompt_service.generate_system_prompt(client)
    
    # Initialize session state for conversation setup
    if 'setup_system_prompt' not in st.session_state:
        st.session_state.setup_system_prompt = default_prompt
    if 'setup_selected_model' not in st.session_state:
        st.session_state.setup_selected_model = DEFAULT_MODEL
    
    # Model selection
    st.write("### 🤖 Model Selection")
    
    # Create model options
    model_options = []
    model_labels = []
    for model_id, model_info in AVAILABLE_MODELS.items():
        model_options.append(model_id)
        cost_range = f"${model_info['input_cost']:.2f}-${model_info['output_cost']:.2f}/1M tokens"
        model_labels.append(f"{model_info['name']} - {model_info['description']} ({cost_range})")
    
    # Model selectbox
    current_model_index = 0
    if st.session_state.setup_selected_model in model_options:
        current_model_index = model_options.index(st.session_state.setup_selected_model)
    
    selected_model_index = st.selectbox(
        "Choose AI Model:",
        range(len(model_options)),
        index=current_model_index,
        format_func=lambda i: model_labels[i],
        help="Different models have different capabilities and costs"
    )
    
    selected_model = model_options[selected_model_index]
    st.session_state.setup_selected_model = selected_model
    
    # Show model details
    model_info = AVAILABLE_MODELS[selected_model]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Input Cost", f"${model_info['input_cost']:.2f}/1M tokens")
    with col2:
        st.metric("Output Cost", f"${model_info['output_cost']:.2f}/1M tokens")
    with col3:
        st.info(f"**Best for:** {model_info['recommended_for']}")
    
    st.divider()
    
    # System prompt preview and editing
    st.write("### 📝 System Prompt")
    
    # Tabs for default vs custom prompt
    prompt_tab1, prompt_tab2 = st.tabs(["Default Prompt", "Edit Prompt"])
    
    with prompt_tab1:
        st.write("**Generated system prompt based on client profile:**")
        st.code(default_prompt, language="text")
        
        if st.button("Use Default Prompt", key="use_default"):
            st.session_state.setup_system_prompt = default_prompt
            show_success_message("Using default system prompt")
    
    with prompt_tab2:
        st.write("**Edit the system prompt to customize the AI's behavior:**")
        
        edited_prompt = st.text_area(
            "System Prompt:",
            value=st.session_state.setup_system_prompt,
            height=300,
            help="This prompt defines how the AI will behave as the virtual client"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Changes", key="save_prompt"):
                st.session_state.setup_system_prompt = edited_prompt
                show_success_message("System prompt updated")
        
        with col2:
            if st.button("Reset to Default", key="reset_prompt"):
                st.session_state.setup_system_prompt = default_prompt
                show_success_message("Reset to default prompt")
    
    st.divider()
    
    # Cost estimation
    st.write("### 💰 Cost Estimation")
    estimated_tokens = len(st.session_state.setup_system_prompt) // 4 + 100  # Rough estimate
    model_info = AVAILABLE_MODELS[selected_model]
    estimated_cost = (estimated_tokens / 1_000_000) * ((model_info['input_cost'] + model_info['output_cost']) / 2)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated Tokens", format_tokens(estimated_tokens))
    with col2:
        st.metric("Estimated Cost per Exchange", format_cost(estimated_cost))
    
    # Ready to start button
    st.write("### 🚀 Ready to Start")
    
    if st.button("Start Conversation with These Settings", type="primary", use_container_width=True):
        return True, st.session_state.setup_system_prompt, st.session_state.setup_selected_model
    
    return False, st.session_state.setup_system_prompt, st.session_state.setup_selected_model


def display_conversation_history(teacher_id: str):
    """
    Display conversation history and metrics for a teacher.
    
    Args:
        teacher_id: The teacher's ID
    """
    st.subheader("📊 Conversation History & Metrics")
    
    # Fetch conversation history
    conversations = fetch_conversation_history(teacher_id)
    
    if not conversations:
        show_info_message(
            "No conversation history yet. Start testing conversations with your clients "
            "in the 'Test Conversations' tab to see metrics here!"
        )
        return
    
    # Calculate and display metrics
    metrics = calculate_conversation_metrics(conversations)
    
    # Display summary metrics
    st.write("### 📈 Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Conversations",
            metrics['total_conversations']
        )
    
    with col2:
        st.metric(
            "Total Cost",
            format_cost(metrics['total_cost'])
        )
    
    with col3:
        st.metric(
            "Avg Cost/Conversation",
            format_cost(metrics['avg_cost_per_conversation'])
        )
    
    with col4:
        if metrics['avg_response_time'] is not None:
            st.metric(
                "Avg Response Time",
                f"{metrics['avg_response_time']:.1f}s"
            )
        else:
            st.metric(
                "Avg Response Time",
                "N/A"
            )
    
    # Additional metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tokens",
            format_tokens(metrics['total_tokens'])
        )
    
    with col2:
        st.metric(
            "Avg Tokens/Conv",
            format_tokens(metrics['avg_tokens_per_conversation'])
        )
    
    with col3:
        st.metric(
            "Avg Messages/Conv",
            metrics['avg_messages_per_conversation']
        )
    
    st.divider()
    
    # Display conversation history
    st.write("### 💬 Conversation History")
    
    # Sort conversations by start time (most recent first)
    conversations.sort(key=lambda x: x['session'].started_at, reverse=True)
    
    for i, conv in enumerate(conversations):
        session = conv['session']
        client = conv['client']
        messages = conv.get('messages', [])
        
        # Create a container for each conversation
        with st.container():
            # Header with key info
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.write(f"**{client.name}**")
                st.caption(f"Session: {session.id[:8]}...")
            
            with col2:
                start_time = session.started_at.strftime('%Y-%m-%d %H:%M')
                st.write(f"📅 {start_time}")
                if session.ended_at:
                    duration = session.ended_at - session.started_at
                    duration_minutes = int(duration.total_seconds() // 60)
                    st.caption(f"Duration: {duration_minutes} min")
            
            with col3:
                st.write(f"💬 {len(messages)} msgs")
                st.caption(f"{format_tokens(session.total_tokens or 0)} tokens")
            
            with col4:
                st.write(format_cost(session.estimated_cost or 0.0))
                status_emoji = "✅" if session.status == "completed" else "🔴"
                st.caption(f"{status_emoji} {session.status}")
            
            # Expandable conversation view
            with st.expander("View Conversation"):
                for msg in messages:
                    render_chat_message(
                        role=msg.role,
                        content=msg.content,
                        tokens=msg.token_count
                    )
                
                if session.session_notes:
                    st.info(f"**Session Notes**: {session.session_notes}")
            
            # Export button
            export_text = format_conversation_export(conv)
            st.download_button(
                label="📥 Export Conversation",
                data=export_text,
                file_name=f"conversation_{client.name.replace(' ', '_')}_{session.started_at.strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key=f"export_{session.id}"
            )
            
            st.divider()


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
    
    # Display configuration warnings
    display_configuration_warnings()
    
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
            # Initialize conversation setup state
            if 'conversation_setup_complete' not in st.session_state:
                st.session_state.conversation_setup_complete = False
            
            # Show setup interface if setup is not complete AND no active conversation
            if not st.session_state.conversation_setup_complete and not st.session_state.get('conversation_active', False):
                ready_to_start, system_prompt, selected_model = show_conversation_setup()
                
                if ready_to_start:
                    st.session_state.conversation_setup_complete = True
                    st.session_state.setup_system_prompt = system_prompt
                    st.session_state.setup_selected_model = selected_model
                    st.rerun()
                
                return  # Don't show conversation interface until setup is complete
            
            # Display conversation interface
            st.subheader(f"💬 Test Conversation with {st.session_state.selected_client_name}")
            
            # Show selected settings
            with st.expander("🔧 Current Settings", expanded=False):
                model_info = AVAILABLE_MODELS.get(st.session_state.setup_selected_model, {})
                st.write(f"**Model:** {model_info.get('name', st.session_state.setup_selected_model)}")
                st.write(f"**Prompt Preview:** {st.session_state.setup_system_prompt[:100]}...")
                if st.button("Change Settings", key="change_settings"):
                    st.session_state.conversation_setup_complete = False
                    st.rerun()
            
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
                            
                            # Start the conversation with custom settings
                            db = get_database_connection()
                            session = conversation_service.start_conversation(
                                db=db,
                                student=mock_student,
                                client_id=st.session_state.selected_client_id,
                                custom_system_prompt=st.session_state.setup_system_prompt,
                                model=st.session_state.setup_selected_model
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
                            show_error_message(f"Failed to start conversation: {handle_api_error(e)}")
                            # Store error for debugging
                            st.session_state.last_error = str(e)
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
                            st.session_state.conversation_setup_complete = False  # Allow settings change for next conversation
                            
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
                # Display metrics with better formatting
                if st.session_state.conversation_active:
                    st.metric(
                        "Total Tokens", 
                        format_tokens(st.session_state.conversation_tokens),
                        help="Tokens used in this conversation"
                    )
                    st.metric(
                        "Est. Cost", 
                        format_cost(st.session_state.conversation_cost),
                        help="Estimated cost for this conversation"
                    )
                else:
                    st.metric("Status", "Ready")
                    st.caption("Start a conversation to see metrics")
            
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
                            
                            # Get AI response with enhanced loading state
                            with st.spinner(f"💭 {st.session_state.selected_client_name} is thinking..."):
                                # Set loading state
                                st.session_state.loading = True
                                
                                ai_message = conversation_service.send_message(
                                    db=db,
                                    session_id=st.session_state.current_session_id,
                                    content=user_input,
                                    user=mock_student,
                                    model=st.session_state.setup_selected_model,
                                    system_prompt=st.session_state.setup_system_prompt
                                )
                                
                                # Clear loading state
                                st.session_state.loading = False
                            
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
                            show_error_message(f"Failed to send message: {handle_api_error(e)}")
                            # Store error for debugging
                            st.session_state.last_error = str(e)
                        finally:
                            db.close()
            
            else:
                # Show instructions when no conversation is active
                st.info(
                    "Start a test conversation to interact with the virtual client. "
                    "The client will respond based on their profile and personality traits."
                )
    
    with tab3:
        display_conversation_history(teacher.teacher_id)


if __name__ == "__main__":
    main()
