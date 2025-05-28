"""
Integration test for Part 10: Enhanced Teacher Features

Tests the system prompt editing and model selection functionality.
"""

import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from backend.services.conversation_service import conversation_service
from backend.services.client_service import client_service
from backend.services.prompt_service import prompt_service
from backend.models.client_profile import ClientProfileCreate
from backend.models.auth import StudentAuth


class TestPart10EnhancedTeacherFeatures:
    """Test prompt editing and model selection functionality"""
    
    def test_custom_system_prompt_and_model_selection_workflow(self, db_session: Session):
        """Test complete workflow with custom prompt and model selection"""
        
        # Step 1: Create a test client
        client_data = ClientProfileCreate(
            name="Test Client",
            age=30,
            personality_traits=["anxious", "cooperative"],
            issues=["housing_insecurity", "mental_health"],
            background_story="Test background for prompt generation"
        )
        
        # Create client (using mock teacher ID)
        created_client = client_service.create_client_for_teacher(
            db=db_session, 
            client_data=client_data, 
            teacher_id="teacher-1"
        )
        
        # Step 2: Generate default system prompt
        default_prompt = prompt_service.generate_system_prompt(created_client)
        
        # Verify default prompt contains expected elements
        assert "Test Client" in default_prompt
        assert "30-year-old" in default_prompt
        assert "anxious" in default_prompt or "cooperative" in default_prompt
        assert "housing insecurity" in default_prompt or "housing" in default_prompt
        
        # Step 3: Create custom system prompt
        custom_prompt = """You are playing the role of Maria, a 30-year-old who is experiencing housing insecurity.

CUSTOM BEHAVIOR:
- You are more direct than usual
- You focus primarily on housing concerns
- You are hopeful about finding solutions

IMPORTANT GUIDELINES:
1. Stay in character at all times
2. Keep responses concise (1-2 sentences)
3. This is an educational simulation
"""
        
        # Step 4: Test conversation with custom prompt and model
        mock_student = StudentAuth(id="student-1", student_id="student-1")
        custom_model = "claude-3-5-sonnet-20241022"
        
        # Mock the Anthropic service to avoid actual API calls
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic_service:
            mock_anthropic_instance = Mock()
            mock_anthropic_instance.generate_response.side_effect = [
                "Hello, I'm Maria. I'm dealing with some housing issues right now.",  # Initial greeting
                "Thank you for asking. The uncertainty is really stressing me out."    # Response to user
            ]
            mock_anthropic_service.return_value = mock_anthropic_instance
            
            # Start conversation with custom prompt and model
            session = conversation_service.start_conversation(
                db=db_session,
                student=mock_student,
                client_id=created_client.id,
                custom_system_prompt=custom_prompt,
                model=custom_model
            )
            
            # Verify session was created
            assert session.id is not None
            assert session.student_id == mock_student.student_id
            assert session.client_profile_id == created_client.id
            assert session.status == "active"
            
            # Verify the anthropic service was called with custom prompt and model
            calls = mock_anthropic_instance.generate_response.call_args_list
            assert len(calls) == 1  # Initial greeting call
            
            # Check that custom prompt was used (passed as system_prompt parameter)
            first_call_kwargs = calls[0][1]  # Get keyword arguments
            assert first_call_kwargs['system_prompt'] == custom_prompt
            assert first_call_kwargs['model'] == custom_model
            
            # Step 5: Test sending message with same model and custom prompt
            user_message = "How are you feeling today?"
            
            ai_response = conversation_service.send_message(
                db=db_session,
                session_id=session.id,
                content=user_message,
                user=mock_student,
                model=custom_model,
                system_prompt=custom_prompt  # Pass the custom prompt
            )
            
            # Verify response was generated
            assert ai_response.role == "assistant"
            assert ai_response.content == "Thank you for asking. The uncertainty is really stressing me out."
            assert ai_response.token_count > 0
            
            # Verify the model was passed to the second call
            assert len(mock_anthropic_instance.generate_response.call_args_list) == 2
            second_call_kwargs = mock_anthropic_instance.generate_response.call_args_list[1][1]
            assert second_call_kwargs['model'] == custom_model
            
            # Step 6: Verify conversation context and custom prompt persistence
            # The system prompt should be the custom one that we passed
            assert second_call_kwargs['system_prompt'] == custom_prompt
            
        print("✅ Part 10 integration test passed!")
        print(f"   - Created client: {created_client.name}")
        print(f"   - Generated default prompt: {len(default_prompt)} characters")
        print(f"   - Used custom prompt: {len(custom_prompt)} characters")
        print(f"   - Selected model: {custom_model}")
        print(f"   - Started conversation session: {session.id}")
        print(f"   - Exchanged messages with custom settings")
        
    def test_default_vs_custom_prompt_behavior(self, db_session: Session):
        """Test that custom prompts override default prompts properly"""
        
        # Create test client
        client_data = ClientProfileCreate(
            name="Sarah Johnson",
            age=25,
            personality_traits=["defensive", "suspicious"],
            issues=["substance_abuse"],
            communication_style="confrontational"
        )
        
        client = client_service.create_client_for_teacher(
            db=db_session, 
            client_data=client_data, 
            teacher_id="teacher-1"
        )
        
        # Test with default prompt
        default_prompt = prompt_service.generate_system_prompt(client)
        
        # Test with custom prompt that overrides personality
        custom_prompt = "You are Sarah, but today you are feeling more cooperative and open than usual."
        
        mock_student = StudentAuth(id="student-1", student_id="student-1")
        
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic:
            mock_instance = Mock()
            mock_instance.generate_response.return_value = "Test response"
            mock_anthropic.return_value = mock_instance
            
            # Start conversation with custom prompt
            session = conversation_service.start_conversation(
                db=db_session,
                student=mock_student,
                client_id=client.id,
                custom_system_prompt=custom_prompt,
                model="claude-3-haiku-20240307"
            )
            
            # Verify custom prompt was used instead of default
            call_kwargs = mock_instance.generate_response.call_args[1]
            assert call_kwargs['system_prompt'] == custom_prompt
            assert call_kwargs['system_prompt'] != default_prompt
            
        print("✅ Custom prompt override test passed!")
        
    def test_model_selection_pricing_logic(self, db_session: Session):
        """Test that different models can be selected and used"""
        
        # Create test client
        client_data = ClientProfileCreate(
            name="Test Client Model Selection",
            age=35,
            personality_traits=["cooperative"]
        )
        
        client = client_service.create_client_for_teacher(
            db=db_session, 
            client_data=client_data, 
            teacher_id="teacher-1"
        )
        
        mock_student = StudentAuth(id="student-1", student_id="student-1")
        
        # Test different models
        test_models = [
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022", 
            "claude-3-sonnet-20240229"
        ]
        
        with patch('backend.services.conversation_service.anthropic_service') as mock_anthropic:
            mock_instance = Mock()
            mock_instance.generate_response.return_value = "Model test response"
            mock_anthropic.return_value = mock_instance
            
            for model in test_models:
                # Start conversation with specific model
                session = conversation_service.start_conversation(
                    db=db_session,
                    student=mock_student,
                    client_id=client.id,
                    model=model
                )
                
                # Verify correct model was used
                call_kwargs = mock_instance.generate_response.call_args[1]
                assert call_kwargs['model'] == model
                
                # End the session for next test
                conversation_service.end_conversation(
                    db=db_session,
                    session_id=session.id,
                    user=mock_student
                )
                
        print("✅ Model selection test passed for all models!")
        print(f"   - Tested models: {', '.join(test_models)}")


if __name__ == "__main__":
    # This allows running the test directly for quick verification
    print("Run this test with: python run_tests.py tests/integration/test_part10_enhanced_teacher_features.py -v")
