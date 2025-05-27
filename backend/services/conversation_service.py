"""
Conversation Handler Service

This service orchestrates the conversation flow between students and AI clients.
It integrates the session service, message handling, prompt generation, and
Anthropic API to create realistic educational conversations.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session as DBSession

# Import models
from backend.models.session import Session, SessionCreate, SessionDB
from backend.models.message import Message, MessageCreate, MessageDB
from backend.models.client_profile import ClientProfile
from backend.models.auth import StudentAuth, TeacherAuth

# Import services
from backend.services.session_service import session_service
from backend.services.anthropic_service import anthropic_service
from backend.services.prompt_service import prompt_service
from backend.services.client_service import client_service

# Import utilities
from backend.utils.token_counter import count_tokens


class ConversationService:
    """
    Service for managing AI-powered conversations between students and virtual clients.
    
    This service handles:
    - Starting new conversations with appropriate greetings
    - Processing user messages and generating AI responses
    - Maintaining conversation context and history
    - Tracking token usage and costs
    - Ending conversations gracefully
    """
    
    def __init__(self):
        """Initialize the conversation service."""
        pass
    
    def start_conversation(
        self,
        db: DBSession,
        student: StudentAuth,
        client_id: str,
        assignment_id: Optional[str] = None
    ) -> Session:
        """
        Start a new conversation session.
        
        Creates a new session, generates the system prompt for the AI,
        and creates an initial greeting from the virtual client.
        
        Args:
            db: Database session
            student: Authenticated student starting the conversation
            client_id: ID of the virtual client to converse with
            assignment_id: Optional assignment ID if this is for an assignment
            
        Returns:
            Session: The newly created session with initial AI greeting
            
        Raises:
            ValueError: If client doesn't exist or student doesn't have access
        """
        # Step 1: Validate client exists
        client = client_service.get(db, client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Step 2: TODO - If assignment_id provided, verify student has access
        # This will be implemented when assignment validation is added
        
        # Step 3: Create the session
        session_data = SessionCreate(
            student_id=student.student_id,
            client_profile_id=client_id
        )
        
        session_db = session_service.create_session(
            db=db,
            session_data=session_data,
            student_id=student.student_id
        )
        
        # Step 4: Generate system prompt for the AI
        system_prompt = prompt_service.generate_system_prompt(client)
        
        # Step 5: Generate initial greeting from the AI
        greeting_prompt = (
            f"You are meeting a social work student for the first time. "
            f"Introduce yourself naturally as {client.name}, staying in character. "
            f"Keep your greeting brief (1-2 sentences) and authentic to your personality and current situation. "
            f"Don't immediately share all your problems - just a natural first interaction."
        )
        
        try:
            # Get the Anthropic service instance
            anthropic = anthropic_service()
            
            # Generate the greeting
            greeting_content = anthropic.generate_response(
                messages=[{"role": "user", "content": greeting_prompt}],
                system_prompt=system_prompt,
                max_tokens=150,  # Keep greetings concise
                temperature=0.7
            )
            
            # Count tokens for the greeting
            greeting_tokens = count_tokens(greeting_content)
            
        except Exception as e:
            # Handle any Anthropic API errors gracefully
            raise RuntimeError(f"Failed to generate AI greeting: {str(e)}")
        
        # Step 6: Store the AI greeting as the first message
        message_data = MessageCreate(
            role="assistant",
            content=greeting_content,
            token_count=greeting_tokens
        )
        
        # Add message to session (this also updates session tokens and cost)
        session_service.add_message(
            db=db,
            session_id=session_db.id,
            message_data=message_data
        )
        
        # Step 7: Refresh session from DB to get updated token counts
        db.refresh(session_db)
        
        # Convert to Pydantic model and return
        return Session.model_validate(session_db)
    
    def send_message(
        self,
        db: DBSession,
        session_id: str,
        content: str,
        user: StudentAuth
    ) -> Message:
        """
        Send a message in a conversation and get AI response.
        
        This method:
        1. Validates the session and user access
        2. Stores the user's message
        3. Generates an AI response
        4. Stores the AI response
        5. Updates token counts and costs
        
        Args:
            db: Database session
            session_id: ID of the conversation session
            content: Message content from the user
            user: Authenticated user sending the message
            
        Returns:
            Message: The AI's response message
            
        Raises:
            ValueError: If session doesn't exist or user doesn't have access
            RuntimeError: If AI response generation fails
        """
        # Step 1: Get and validate the session
        session_db = session_service.get_session(db, session_id)
        if not session_db:
            raise ValueError(f"Session with ID {session_id} not found")
        
        # Verify student has access to this session
        if session_db.student_id != user.student_id:
            raise ValueError(f"Student {user.student_id} does not have access to session {session_id}")
        
        # Check if session is still active
        if session_db.status != "active":
            raise ValueError(f"Session {session_id} is not active")
        
        # Step 2: Store the user's message
        user_message_data = MessageCreate(
            role="user",
            content=content,
            token_count=count_tokens(content)
        )
        
        user_message = session_service.add_message(
            db=db,
            session_id=session_id,
            message_data=user_message_data
        )
        
        # Step 3: Get conversation history for context
        # Get all messages including the one we just added
        messages = session_service.get_messages(
            db=db,
            session_id=session_id,
            limit=50  # Reasonable limit to control context size
        )
        
        # Step 4: Generate AI response
        try:
            response_content, response_tokens = self.get_ai_response(
                db=db,
                session=session_db,
                user_message=content,
                conversation_history=messages[:-1]  # Exclude the message we just added
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate AI response: {str(e)}")
        
        # Step 5: Store the AI response
        ai_message_data = MessageCreate(
            role="assistant",
            content=response_content,
            token_count=response_tokens
        )
        
        ai_message = session_service.add_message(
            db=db,
            session_id=session_id,
            message_data=ai_message_data
        )
        
        # Convert to Pydantic model and return
        return Message.model_validate(ai_message)
    
    def get_ai_response(
        self,
        db: DBSession,
        session: SessionDB,
        user_message: str,
        conversation_history: list[MessageDB]
    ) -> tuple[str, int]:
        """
        Generate an AI response for the conversation.
        
        This method:
        1. Gets the client profile
        2. Generates the system prompt
        3. Formats the conversation history
        4. Calls the Anthropic API
        5. Returns the response and token count
        
        Args:
            db: Database session
            session: The current session
            user_message: The latest message from the user
            conversation_history: Previous messages in the conversation
            
        Returns:
            tuple: (response_content, token_count)
            
        Raises:
            RuntimeError: If AI response generation fails
        """
        # Step 1: Get the client profile
        client = client_service.get(db, session.client_profile_id)
        if not client:
            raise RuntimeError(f"Client profile {session.client_profile_id} not found")
        
        # Step 2: Generate system prompt
        system_prompt = prompt_service.generate_system_prompt(client)
        
        # Step 3: Format conversation history for API
        formatted_messages = self._format_conversation_for_ai(
            messages=conversation_history,
            latest_user_message=user_message
        )
        
        # Step 4: Call Anthropic API
        try:
            anthropic = anthropic_service()
            
            response_content = anthropic.generate_response(
                messages=formatted_messages,
                system_prompt=system_prompt,
                max_tokens=500,  # Reasonable limit for conversational responses
                temperature=0.7  # Balanced between creativity and consistency
            )
            
            # Step 5: Count tokens and return
            response_tokens = count_tokens(response_content)
            
            return response_content, response_tokens
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def end_conversation(
        self,
        db: DBSession,
        session_id: str,
        user: StudentAuth,
        session_notes: Optional[str] = None
    ) -> Session:
        """
        End a conversation session.
        
        Args:
            db: Database session
            session_id: ID of the session to end
            user: Authenticated user ending the session
            session_notes: Optional notes about the session
            
        Returns:
            Session: The ended session with final status
            
        Raises:
            ValueError: If session doesn't exist or user doesn't have access
        """
        # Get and validate the session
        session_db = session_service.get_session(db, session_id)
        if not session_db:
            raise ValueError(f"Session with ID {session_id} not found")
        
        # Verify student has access to this session
        if session_db.student_id != user.student_id:
            raise ValueError(f"Student {user.student_id} does not have access to session {session_id}")
        
        # Check if session is already ended
        if session_db.status == "completed":
            raise ValueError(f"Session {session_id} is already completed")
        
        # End the session using session service
        ended_session = session_service.end_session(
            db=db,
            session_id=session_id,
            student_id=user.student_id,
            session_notes=session_notes
        )
        
        # Check if end_session returned None (shouldn't happen due to our checks above)
        if not ended_session:
            raise RuntimeError(f"Failed to end session {session_id}")
        
        # Convert to Pydantic model and return
        return Session.model_validate(ended_session)
    
    def _format_conversation_for_ai(
        self,
        messages: list[MessageDB],
        latest_user_message: str
    ) -> list[Dict[str, str]]:
        """
        Format conversation history for the Anthropic API.
        
        Converts our message format to the format expected by the API,
        ensuring proper role assignments and message ordering.
        
        Args:
            messages: Historical messages from the database
            latest_user_message: The most recent user message
            
        Returns:
            list: Formatted messages for the API
        """
        formatted = []
        
        # Add all historical messages
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add the latest user message
        formatted.append({
            "role": "user",
            "content": latest_user_message
        })
        
        return formatted
    
    def _calculate_cost(self, token_count: int, model: str) -> float:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            token_count: Number of tokens used
            model: Model name (e.g., "claude-3-haiku-20240307")
            
        Returns:
            float: Estimated cost in dollars
        """
        # This method is kept for potential future use, but cost calculation
        # is actually handled by the session service using the token_counter utility
        # which has the pricing models configured.
        
        # For now, we'll use the same pricing as configured in token_counter
        if "haiku" in model.lower():
            # Haiku: $0.25 per 1M input, $1.25 per 1M output
            # Average to $0.75 per 1M tokens
            return (token_count / 1_000_000) * 0.75
        elif "sonnet" in model.lower():
            # Sonnet: $3 per 1M input, $15 per 1M output  
            # Average to $9 per 1M tokens
            return (token_count / 1_000_000) * 9.0
        else:
            # Default to Haiku pricing
            return (token_count / 1_000_000) * 0.75


# Create a singleton instance
conversation_service = ConversationService()
