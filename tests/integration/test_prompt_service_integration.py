"""
Integration tests for Prompt Service with other services
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from backend.services.prompt_service import prompt_service
from backend.services.client_service import client_service
from backend.models.client_profile import ClientProfileDB, ClientProfile, ClientProfileCreate
from backend.models.message import MessageDB, Message


class TestPromptServiceIntegration:
    """Test prompt service integration with other services"""
    
    @pytest.fixture
    def sample_client_data(self):
        """Sample client data for testing"""
        return ClientProfileCreate(
            name="Sarah Johnson",
            age=28,
            race="African American",
            gender="female",
            socioeconomic_status="working class",
            issues=["domestic_violence", "trauma_history", "mental_health"],
            background_story="Sarah is a nurse who recently left an abusive relationship. She's staying with friends while looking for her own place. The trauma from her relationship has been affecting her work performance and sleep.",
            personality_traits=["defensive", "anxious", "cooperative"],
            communication_style="indirect"
        )
    
    def test_prompt_generation_with_database_client(self, db_session: Session, sample_client_data):
        """Test generating prompt from a client retrieved from database"""
        # Create client in database
        created_client = client_service.create_client_for_teacher(
            db_session,
            sample_client_data,
            "teacher-123"
        )
        
        # Retrieve client as Pydantic model
        client_model = ClientProfile.model_validate(created_client)
        
        # Generate prompt
        prompt = prompt_service.generate_system_prompt(client_model)
        
        # Verify prompt contains client information
        assert "Sarah Johnson" in prompt
        assert "28-year-old female" in prompt
        assert "African American" in prompt
        assert "working class" in prompt
        
        # Check issues are properly formatted
        assert "domestic violence in your home" in prompt
        assert "past traumatic experiences" in prompt
        assert "mental health challenges" in prompt
        
        # Check personality traits
        assert "defensive when feeling threatened" in prompt
        assert "anxious and worried" in prompt
        assert "cooperative and willing" in prompt
        
        # Check communication style
        assert "communicate indirectly" in prompt
        
    def test_prompt_variations_for_different_clients(self, db_session: Session):
        """Test that different clients produce appropriately different prompts"""
        # Create first client - young, talkative
        client1_data = ClientProfileCreate(
            name="Tommy Lee",
            age=16,
            race="Asian",
            gender="male",
            socioeconomic_status="middle class",
            issues=["family_conflict", "substance_abuse"],
            background_story="Tommy is a high school student whose parents are going through a divorce. He's been experimenting with marijuana to cope.",
            personality_traits=["talkative", "emotional", "confused"],
            communication_style="casual"
        )
        
        # Create second client - elderly, reserved
        client2_data = ClientProfileCreate(
            name="Margaret O'Brien",
            age=75,
            race="Irish American",
            gender="female",
            socioeconomic_status="fixed income",
            issues=["grief_loss", "chronic_illness", "housing_insecurity"],
            background_story="Margaret recently lost her husband of 50 years. She's struggling to maintain their home on her social security income while managing her arthritis.",
            personality_traits=["reserved", "stoic", "pessimistic"],
            communication_style="formal"
        )
        
        # Create both clients
        client1_db = client_service.create_client_for_teacher(db_session, client1_data, "teacher-123")
        client2_db = client_service.create_client_for_teacher(db_session, client2_data, "teacher-123")
        
        # Convert to Pydantic models
        client1 = ClientProfile.model_validate(client1_db)
        client2 = ClientProfile.model_validate(client2_db)
        
        # Generate prompts
        prompt1 = prompt_service.generate_system_prompt(client1)
        prompt2 = prompt_service.generate_system_prompt(client2)
        
        # Verify prompts are different and appropriate
        # Client 1 should be young and talkative
        assert "16-year-old" in prompt1
        assert "talkative and eager to share" in prompt1
        assert "speak casually" in prompt1
        assert "family conflicts" in prompt1
        
        # Client 2 should be elderly and reserved
        assert "75-year-old" in prompt2
        assert "reserved and speak only when necessary" in prompt2
        assert "maintain formal, polite communication" in prompt2
        assert "grief from a recent loss" in prompt2
        
        # Ensure they're distinctly different
        assert prompt1 != prompt2
        assert len(prompt1) > 100  # Substantial prompts
        assert len(prompt2) > 100
    
    def test_reminder_prompt_with_real_client(self, db_session: Session):
        """Test reminder prompt generation with database client"""
        # Create a client with specific traits
        client_data = ClientProfileCreate(
            name="Roberto Martinez",
            age=42,
            race="Latino",
            gender="male",
            socioeconomic_status="unemployed",
            issues=["unemployment", "financial_crisis", "mental_health"],
            background_story="Roberto was laid off from his construction job 6 months ago. Bills are piling up and he's feeling hopeless.",
            personality_traits=["pessimistic", "honest", "emotional"],
            communication_style="direct"
        )
        
        client_db = client_service.create_client_for_teacher(db_session, client_data, "teacher-123")
        client_model = ClientProfile.model_validate(client_db)
        
        # Generate reminder
        reminder = prompt_service.create_reminder_prompt(client_model)
        
        # Check reminder content
        assert "Roberto Martinez" in reminder
        assert "unemployment" in reminder  # First issue
        assert "pessimistic" in reminder  # First trait
        assert "Stay in character" in reminder
        
        # Reminder should be brief
        assert len(reminder) < 200
    
    def test_conversation_context_with_message_models(self, db_session: Session):
        """Test formatting messages from database models"""
        # Create some test messages (normally these would come from the message service)
        messages = [
            Message(
                id="msg-1",
                session_id="session-1",
                role="user",
                content="Hi, I'm your social worker. How can I help you today?",
                timestamp=datetime.utcnow(),
                token_count=12,
                sequence_number=1
            ),
            Message(
                id="msg-2",
                session_id="session-1",
                role="assistant",
                content="I don't know if you can help. Nothing seems to work out for me.",
                timestamp=datetime.utcnow(),
                token_count=14,
                sequence_number=2
            ),
            Message(
                id="msg-3",
                session_id="session-1",
                role="user",
                content="I hear that you're feeling discouraged. Can you tell me more about what's been happening?",
                timestamp=datetime.utcnow(),
                token_count=18,
                sequence_number=3
            )
        ]
        
        # Format for API
        formatted = prompt_service.generate_conversation_context(messages)
        
        # Verify formatting
        assert len(formatted) == 3
        
        # Check structure matches API requirements
        for i, msg in enumerate(formatted):
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ["user", "assistant"]
            assert isinstance(msg["content"], str)
            
        # Verify order is preserved
        assert formatted[0]["content"] == "Hi, I'm your social worker. How can I help you today?"
        assert formatted[1]["content"] == "I don't know if you can help. Nothing seems to work out for me."
        assert formatted[2]["content"] == "I hear that you're feeling discouraged. Can you tell me more about what's been happening?"
    
    def test_prompt_consistency_across_retrievals(self, db_session: Session):
        """Test that the same client produces consistent prompts"""
        # Create a client
        client_data = ClientProfileCreate(
            name="Test Client",
            age=30,
            race="Caucasian",
            gender="non-binary",
            socioeconomic_status="middle class",
            issues=["anxiety", "family_conflict"],
            background_story="Test background story.",
            personality_traits=["anxious", "honest"],
            communication_style="direct"
        )
        
        client_db = client_service.create_client_for_teacher(db_session, client_data, "teacher-123")
        
        # Retrieve and generate prompt multiple times
        prompts = []
        for _ in range(3):
            retrieved = client_service.get(db_session, client_db.id)
            client_model = ClientProfile.model_validate(retrieved)
            prompt = prompt_service.generate_system_prompt(client_model)
            prompts.append(prompt)
        
        # All prompts should be identical
        assert prompts[0] == prompts[1]
        assert prompts[1] == prompts[2]
    
    def test_edge_cases_from_database(self, db_session: Session):
        """Test edge cases with database clients"""
        # Client with no optional fields
        minimal_client_data = ClientProfileCreate(
            name="Minimal Client",
            age=25
        )
        
        minimal_db = client_service.create_client_for_teacher(db_session, minimal_client_data, "teacher-123")
        minimal_model = ClientProfile.model_validate(minimal_db)
        
        # Should generate prompt without errors
        minimal_prompt = prompt_service.generate_system_prompt(minimal_model)
        assert "Minimal Client" in minimal_prompt
        assert "25-year-old" in minimal_prompt
        assert "IMPORTANT GUIDELINES" in minimal_prompt
        
        # Client with all fields filled
        maximal_client_data = ClientProfileCreate(
            name="Maximal Client",
            age=50,
            race="Mixed race",
            gender="male",
            socioeconomic_status="upper middle class",
            issues=["chronic_illness", "elder_care", "financial_crisis", "mental_health", "grief_loss"],
            background_story="A very long and detailed background story " * 10,  # Long story
            personality_traits=["anxious", "defensive", "withdrawn", "pessimistic", "confused"],
            communication_style="verbose"
        )
        
        maximal_db = client_service.create_client_for_teacher(db_session, maximal_client_data, "teacher-123")
        maximal_model = ClientProfile.model_validate(maximal_db)
        
        # Should handle long content gracefully
        maximal_prompt = prompt_service.generate_system_prompt(maximal_model)
        assert "Maximal Client" in maximal_prompt
        assert len(maximal_prompt) > 1000  # Should be substantial
        assert "A very long and detailed background story" in maximal_prompt
