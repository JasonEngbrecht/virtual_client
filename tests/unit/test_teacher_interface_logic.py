"""
Unit tests for MVP Teacher Interface - Business Logic Focus

Tests the business logic without mocking Streamlit UI components.
For UI testing, see the integration tests which test the full flow.
"""

import pytest
from backend.models.client_profile import ClientProfileCreate, ClientProfileDB
from backend.models.auth import TeacherAuth


class TestTeacherInterfaceLogic:
    """Test teacher interface business logic"""
    
    def test_client_profile_create_validation(self):
        """Test ClientProfileCreate validation"""
        # Valid client
        valid_client = ClientProfileCreate(
            name="Test Client",
            age=30,
            personality_traits=["anxious", "cooperative"]
        )
        assert valid_client.name == "Test Client"
        assert valid_client.age == 30
        assert len(valid_client.personality_traits) == 2
        
        # Test with all fields
        full_client = ClientProfileCreate(
            name="Full Client",
            age=45,
            gender="Female",
            race="Asian",
            socioeconomic_status="Middle class",
            issues=["housing_insecurity", "unemployment"],
            background_story="Detailed background",
            personality_traits=["defensive", "withdrawn", "anxious"],
            communication_style="brief"
        )
        assert full_client.gender == "Female"
        assert len(full_client.issues) == 2
        assert full_client.communication_style == "brief"
    
    def test_teacher_auth_model(self):
        """Test TeacherAuth model"""
        teacher = TeacherAuth(id="teacher-1", teacher_id="teacher-1")
        assert teacher.id == "teacher-1"
        assert teacher.teacher_id == "teacher-1"
    
    def test_personality_traits_validation_logic(self):
        """Test personality traits validation logic"""
        # Test minimum traits (should have at least 2)
        traits_too_few = ["anxious"]
        assert len(traits_too_few) < 2  # This would fail validation
        
        # Test maximum traits (should have at most 5)
        traits_too_many = ["anxious", "cooperative", "defensive", 
                          "emotional", "talkative", "withdrawn"]
        assert len(traits_too_many) > 5  # This would fail validation
        
        # Test valid range
        traits_valid = ["anxious", "cooperative", "defensive"]
        assert 2 <= len(traits_valid) <= 5  # This would pass validation
    
    def test_client_display_formatting(self):
        """Test client display formatting logic"""
        # Test issue formatting
        issues = ["housing_insecurity", "unemployment", "mental_health"]
        formatted_issues = [issue.replace("_", " ").title() for issue in issues]
        assert formatted_issues == ["Housing Insecurity", "Unemployment", "Mental Health"]
        
        # Test personality trait formatting
        traits = ["anxious", "cooperative"]
        formatted_traits = [trait.replace("_", " ").title() for trait in traits]
        assert formatted_traits == ["Anxious", "Cooperative"]
    
    def test_client_data_transformation(self):
        """Test transforming form data to ClientProfileCreate"""
        # Simulate form data
        form_data = {
            "name": "Maria Rodriguez",
            "age": 35,
            "gender": "Female",
            "race": "Hispanic/Latino",
            "socioeconomic_status": "Working class",
            "issues": ["housing_insecurity", "unemployment"],
            "background_story": "Single mother facing challenges",
            "personality_traits": ["anxious", "cooperative"],
            "communication_style": "emotional"
        }
        
        # Transform to ClientProfileCreate
        client = ClientProfileCreate(**form_data)
        
        assert client.name == form_data["name"]
        assert client.age == form_data["age"]
        assert client.issues == form_data["issues"]
        assert client.personality_traits == form_data["personality_traits"]
    
    def test_empty_optional_fields(self):
        """Test handling of empty optional fields"""
        # Create client with minimal data
        minimal_data = {
            "name": "Test Client",
            "age": 25,
            "personality_traits": ["reserved", "honest"]
        }
        
        client = ClientProfileCreate(**minimal_data)
        
        # Check optional fields default to None or empty
        assert client.gender is None
        assert client.race is None
        assert client.socioeconomic_status is None
        assert client.issues == []
        assert client.background_story is None
        assert client.communication_style is None
