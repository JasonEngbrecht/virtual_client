"""
Unit tests for Prompt Service
"""

import pytest
from datetime import datetime
from backend.services.prompt_service import prompt_service, PromptService
from backend.models.client_profile import ClientProfile
from backend.models.message import Message


class TestPromptService:
    """Test prompt generation functionality"""
    
    @pytest.fixture
    def sample_client(self):
        """Create a sample client profile for testing"""
        return ClientProfile(
            id="test-client-1",
            name="Maria Rodriguez",
            age=35,
            race="Latina",
            gender="female",
            socioeconomic_status="low income",
            issues=["housing_insecurity", "unemployment", "childcare_needs"],
            background_story="Maria is a single mother of two young children who recently lost her job as a restaurant server. She's facing eviction and struggling to find affordable childcare while job searching.",
            personality_traits=["anxious", "defensive", "honest"],
            communication_style="emotional",
            created_by="teacher-123",
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def minimal_client(self):
        """Create a minimal client profile with only required fields"""
        return ClientProfile(
            id="test-client-2",
            name="John Doe",
            age=45,
            race=None,
            gender=None,
            socioeconomic_status=None,
            issues=[],
            background_story=None,
            personality_traits=[],
            communication_style=None,
            created_by="teacher-123",
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def complex_client(self):
        """Create a complex client with many attributes"""
        return ClientProfile(
            id="test-client-3",
            name="David Chen",
            age=68,
            race="Asian",
            gender="male",
            socioeconomic_status="middle class",
            issues=["chronic_illness", "grief_loss", "elder_care", "mental_health"],
            background_story="David is a retired engineer caring for his wife with dementia. He recently lost his adult son in an accident and is struggling with grief while managing his own diabetes and his wife's increasing care needs.",
            personality_traits=["withdrawn", "stoic", "pessimistic", "reserved"],
            communication_style="formal",
            created_by="teacher-123",
            created_at=datetime.utcnow()
        )
    
    def test_generate_system_prompt_complete_profile(self, sample_client):
        """Test prompt generation with a complete client profile"""
        prompt = prompt_service.generate_system_prompt(sample_client)
        
        # Check that all key information is included
        assert "Maria Rodriguez" in prompt
        assert "35-year-old" in prompt
        assert "female" in prompt
        assert "Latina" in prompt
        assert "low income" in prompt
        
        # Check issues are humanized
        assert "housing insecurity" in prompt
        assert "unemployment" in prompt
        assert "childcare needs" in prompt
        
        # Check background story is included
        assert "single mother" in prompt
        assert "lost her job" in prompt
        
        # Check personality traits are humanized
        assert "anxious" in prompt
        assert "defensive" in prompt
        assert "honest" in prompt
        
        # Check communication style is humanized
        assert "express strong emotions" in prompt
        
        # Check guidelines are included
        assert "IMPORTANT GUIDELINES" in prompt
        assert "Stay in character" in prompt
        assert "educational simulation" in prompt
    
    def test_generate_system_prompt_minimal_profile(self, minimal_client):
        """Test prompt generation with minimal client profile"""
        prompt = prompt_service.generate_system_prompt(minimal_client)
        
        # Check basic info is included
        assert "John Doe" in prompt
        assert "45-year-old" in prompt
        
        # Check that missing fields don't cause errors
        assert "BACKGROUND:" not in prompt  # No background story
        assert "CURRENT SITUATION:" not in prompt  # No issues
        assert "PERSONALITY AND BEHAVIOR:" not in prompt  # No traits or style
        
        # Guidelines should still be included
        assert "IMPORTANT GUIDELINES" in prompt
    
    def test_humanize_issues(self):
        """Test issue code to human-readable conversion"""
        service = PromptService()
        
        issues = ["housing_insecurity", "mental_health", "unemployment"]
        humanized = service._humanize_issues(issues)
        
        assert len(humanized) == 3
        assert "housing insecurity and uncertainty about where you'll live" in humanized
        assert "mental health challenges" in humanized
        assert "unemployment and job searching difficulties" in humanized
    
    def test_humanize_personality_traits(self):
        """Test personality trait humanization"""
        service = PromptService()
        
        traits = ["anxious", "withdrawn", "honest"]
        humanized = service._humanize_personality_traits(traits)
        
        assert len(humanized) == 3
        assert "anxious and worried about many things" in humanized
        assert "withdrawn and reluctant to share personal information" in humanized
        assert "honest and straightforward in your communication" in humanized
    
    def test_humanize_communication_style(self):
        """Test communication style humanization"""
        service = PromptService()
        
        # Test each style
        styles = {
            "direct": "You communicate directly and say what you mean.",
            "emotional": "You express strong emotions when you speak.",
            "formal": "You maintain formal, polite communication.",
            "avoidant": "You tend to avoid difficult topics and change the subject."
        }
        
        for code, expected in styles.items():
            result = service._humanize_communication_style(code)
            assert result == expected
    
    def test_unknown_codes_handled_gracefully(self):
        """Test that unknown codes are handled without errors"""
        service = PromptService()
        
        # Unknown issue
        issues = ["unknown_issue", "housing_insecurity"]
        humanized = service._humanize_issues(issues)
        assert "unknown_issue" in humanized  # Falls back to original
        assert "housing insecurity" in humanized[1]
        
        # Unknown trait
        traits = ["unknown_trait", "anxious"]
        humanized = service._humanize_personality_traits(traits)
        assert "unknown_trait" in humanized
        assert "anxious and worried" in humanized[1]
        
        # Unknown communication style
        result = service._humanize_communication_style("unknown_style")
        assert "unknown_style manner" in result
    
    def test_character_intro_variations(self):
        """Test different character introduction formats"""
        service = PromptService()
        
        # Test with all demographics
        client1 = ClientProfile(
            id="1", name="Test Person", age=30, race="Asian", gender="male",
            socioeconomic_status="middle class", issues=[], background_story=None,
            personality_traits=[], communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        intro1 = service._build_character_intro(client1)
        assert "30-year-old male who is Asian from a middle class background" in intro1
        
        # Test with partial demographics
        client2 = ClientProfile(
            id="2", name="Test Person", age=25, race=None, gender="female",
            socioeconomic_status=None, issues=[], background_story=None,
            personality_traits=[], communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        intro2 = service._build_character_intro(client2)
        assert "25-year-old female" in intro2
        assert "from a" not in intro2  # No socioeconomic status
    
    def test_generate_conversation_context(self):
        """Test message history formatting"""
        messages = [
            Message(
                id="1", session_id="session-1", role="user",
                content="Hello, how are you?", timestamp=datetime.utcnow(),
                token_count=5, sequence_number=1
            ),
            Message(
                id="2", session_id="session-1", role="assistant",
                content="I'm not doing great, to be honest.", timestamp=datetime.utcnow(),
                token_count=8, sequence_number=2
            ),
            Message(
                id="3", session_id="session-1", role="user",
                content="What's going on?", timestamp=datetime.utcnow(),
                token_count=4, sequence_number=3
            )
        ]
        
        formatted = prompt_service.generate_conversation_context(messages)
        
        assert len(formatted) == 3
        assert formatted[0]["role"] == "user"
        assert formatted[0]["content"] == "Hello, how are you?"
        assert formatted[1]["role"] == "assistant"
        assert formatted[1]["content"] == "I'm not doing great, to be honest."
        assert formatted[2]["role"] == "user"
        assert formatted[2]["content"] == "What's going on?"
    
    def test_create_reminder_prompt(self, sample_client, minimal_client):
        """Test reminder prompt generation"""
        # Test with full client
        reminder1 = prompt_service.create_reminder_prompt(sample_client)
        assert "Maria Rodriguez" in reminder1
        assert "housing insecurity" in reminder1
        assert "anxious" in reminder1
        assert "Stay in character" in reminder1
        
        # Test with minimal client
        reminder2 = prompt_service.create_reminder_prompt(minimal_client)
        assert "John Doe" in reminder2
        assert "Stay in character" in reminder2
        # Should not have issues or traits
        assert "dealing with" not in reminder2
    
    def test_single_issue_formatting(self):
        """Test that single issues are formatted differently than multiple"""
        client = ClientProfile(
            id="test", name="Test", age=30, race=None, gender=None,
            socioeconomic_status=None, issues=["mental_health"],
            background_story=None, personality_traits=[], communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        
        prompt = prompt_service.generate_system_prompt(client)
        
        # Single issue should not have bullet points
        assert "You are currently experiencing: mental health challenges" in prompt
        assert "- mental health" not in prompt
    
    def test_multiple_issues_formatting(self):
        """Test that multiple issues are formatted as a list"""
        client = ClientProfile(
            id="test", name="Test", age=30, race=None, gender=None,
            socioeconomic_status=None, 
            issues=["mental_health", "unemployment", "housing_insecurity"],
            background_story=None, personality_traits=[], communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        
        prompt = prompt_service.generate_system_prompt(client)
        
        # Multiple issues should have bullet points
        assert "You are currently experiencing the following challenges:" in prompt
        assert "- mental health challenges" in prompt
        assert "- unemployment" in prompt
        assert "- housing insecurity" in prompt
    
    def test_single_trait_formatting(self):
        """Test single personality trait formatting"""
        client = ClientProfile(
            id="test", name="Test", age=30, race=None, gender=None,
            socioeconomic_status=None, issues=[],
            background_story=None, personality_traits=["anxious"], 
            communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        
        prompt = prompt_service.generate_system_prompt(client)
        
        # Single trait should not have bullet points
        assert "Your personality: You tend to be anxious" in prompt
        assert "- You tend to be" not in prompt
    
    def test_multiple_traits_formatting(self):
        """Test multiple personality traits formatting"""
        client = ClientProfile(
            id="test", name="Test", age=30, race=None, gender=None,
            socioeconomic_status=None, issues=[],
            background_story=None, 
            personality_traits=["anxious", "defensive", "withdrawn"], 
            communication_style=None,
            created_by="teacher", created_at=datetime.utcnow()
        )
        
        prompt = prompt_service.generate_system_prompt(client)
        
        # Multiple traits should have bullet points
        assert "Your personality traits:" in prompt
        assert "- You tend to be anxious" in prompt
        assert "- You tend to be defensive" in prompt
        assert "- You tend to be withdrawn" in prompt
    
    def test_comprehensive_prompt_structure(self, complex_client):
        """Test the overall structure of a complex prompt"""
        prompt = prompt_service.generate_system_prompt(complex_client)
        
        # Check sections appear in correct order
        sections = prompt.split("\n\n")
        
        # First section should be character intro
        assert "David Chen" in sections[0]
        assert "68-year-old male" in sections[0]
        
        # Should have background section
        background_found = False
        for section in sections:
            if "BACKGROUND:" in section:
                background_found = True
                assert "retired engineer" in section
                break
        assert background_found
        
        # Should have current situation section
        situation_found = False
        for section in sections:
            if "CURRENT SITUATION:" in section:
                situation_found = True
                assert "chronic illness" in section
                break
        assert situation_found
        
        # Should have personality section
        personality_found = False
        for section in sections:
            if "PERSONALITY AND BEHAVIOR:" in section:
                personality_found = True
                assert "withdrawn" in section
                assert "formal" in section
                break
        assert personality_found
        
        # Should end with guidelines
        assert "IMPORTANT GUIDELINES:" in sections[-1]
        assert "educational simulation" in sections[-1]
    
    def test_empty_message_list_handling(self):
        """Test that empty message list is handled correctly"""
        messages = []
        formatted = prompt_service.generate_conversation_context(messages)
        
        assert formatted == []
        assert isinstance(formatted, list)
    
    def test_guideline_content(self):
        """Test that all important guidelines are included"""
        guidelines = prompt_service._create_educational_guidelines()
        
        # Check key guidelines
        assert "Stay in character at all times" in guidelines
        assert "Don't break character" in guidelines
        assert "educational simulation" in guidelines
        assert "appropriate boundaries" in guidelines
        assert "1-3 sentences" in guidelines
        assert "building trust takes time" in guidelines
        assert "communication style and personality traits consistently" in guidelines
