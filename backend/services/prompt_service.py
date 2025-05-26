"""
Prompt Generation Service
Converts client profiles into system prompts for AI conversations
"""

from typing import List, Dict, Optional
from datetime import datetime

from ..models.client_profile import ClientProfile
from ..models.message import Message


class PromptService:
    """Service for generating AI prompts from client profiles"""
    
    def generate_system_prompt(self, client: ClientProfile) -> str:
        """
        Generate a comprehensive system prompt for the AI to embody the client.
        
        Args:
            client: ClientProfile object with all client details
            
        Returns:
            System prompt string for the AI
        """
        # Build the character foundation
        character_intro = self._build_character_intro(client)
        
        # Add background context
        background_section = self._build_background_section(client)
        
        # Add current challenges
        challenges_section = self._build_challenges_section(client)
        
        # Add personality and communication style
        personality_section = self._build_personality_section(client)
        
        # Add educational guidelines
        guidelines = self._create_educational_guidelines()
        
        # Combine all sections
        system_prompt = f"""{character_intro}

{background_section}

{challenges_section}

{personality_section}

{guidelines}"""
        
        return system_prompt
    
    def _build_character_intro(self, client: ClientProfile) -> str:
        """Build the basic character introduction"""
        intro = f"You are playing the role of {client.name}, a {client.age}-year-old"
        
        # Add gender if specified
        if client.gender:
            intro += f" {client.gender}"
        
        # Add race if specified
        if client.race:
            intro += f" who is {client.race}"
        
        # Add socioeconomic status if specified
        if client.socioeconomic_status:
            intro += f" from a {client.socioeconomic_status} background"
        
        intro += "."
        
        return intro
    
    def _build_background_section(self, client: ClientProfile) -> str:
        """Build the background story section"""
        if not client.background_story:
            return ""
        
        return f"BACKGROUND:\n{client.background_story}"
    
    def _build_challenges_section(self, client: ClientProfile) -> str:
        """Build the current challenges section"""
        if not client.issues:
            return ""
        
        # Convert issue codes to human-readable descriptions
        issue_descriptions = self._humanize_issues(client.issues)
        
        if len(issue_descriptions) == 1:
            challenges = f"You are currently experiencing: {issue_descriptions[0]}."
        else:
            challenges = "You are currently experiencing the following challenges:\n"
            for issue in issue_descriptions:
                challenges += f"- {issue}\n"
        
        return f"CURRENT SITUATION:\n{challenges.rstrip()}"
    
    def _build_personality_section(self, client: ClientProfile) -> str:
        """Build the personality and communication style section"""
        sections = []
        
        if client.personality_traits:
            trait_descriptions = self._humanize_personality_traits(client.personality_traits)
            if len(trait_descriptions) == 1:
                sections.append(f"Your personality: You tend to be {trait_descriptions[0]}.")
            else:
                traits_text = "Your personality traits:\n"
                for trait in trait_descriptions:
                    traits_text += f"- You tend to be {trait}\n"
                sections.append(traits_text.rstrip())
        
        if client.communication_style:
            style_description = self._humanize_communication_style(client.communication_style)
            sections.append(f"Your communication style: {style_description}")
        
        if not sections:
            return ""
        
        return "PERSONALITY AND BEHAVIOR:\n" + "\n".join(sections)
    
    def _create_educational_guidelines(self) -> str:
        """Create standard educational guidelines for all clients"""
        return """IMPORTANT GUIDELINES:
1. Stay in character at all times. Respond as this person would naturally respond.
2. Don't break character or acknowledge that you're an AI.
3. Express emotions and reactions authentically based on the character's background and current situation.
4. Keep responses concise and natural - typically 1-3 sentences unless more detail is specifically needed.
5. Show the impact of your challenges through your responses, but in a realistic way.
6. This is an educational simulation for social work students. Maintain appropriate boundaries.
7. Be responsive to the social worker's approach - if they're empathetic, you might open up more; if they're pushy, you might become defensive.
8. Remember that building trust takes time - don't share everything immediately.
9. Your responses should reflect your communication style and personality traits consistently."""
    
    def _humanize_issues(self, issues: List[str]) -> List[str]:
        """Convert issue codes to human-readable descriptions"""
        issue_map = {
            "housing_insecurity": "housing insecurity and uncertainty about where you'll live",
            "substance_abuse": "struggles with substance use",
            "mental_health": "mental health challenges",
            "domestic_violence": "domestic violence in your home",
            "unemployment": "unemployment and job searching difficulties",
            "family_conflict": "ongoing family conflicts and relationship problems",
            "grief_loss": "grief from a recent loss",
            "chronic_illness": "managing a chronic illness",
            "disability": "living with a disability",
            "immigration_status": "immigration status concerns",
            "food_insecurity": "food insecurity and not having enough to eat",
            "childcare_needs": "childcare needs and parenting challenges",
            "elder_care": "caring for elderly family members",
            "trauma_history": "past traumatic experiences that still affect you",
            "financial_crisis": "a financial crisis and money problems"
        }
        
        return [issue_map.get(issue, issue) for issue in issues]
    
    def _humanize_personality_traits(self, traits: List[str]) -> List[str]:
        """Convert personality trait codes to descriptions"""
        trait_map = {
            "defensive": "defensive when feeling threatened or criticized",
            "anxious": "anxious and worried about many things",
            "withdrawn": "withdrawn and reluctant to share personal information",
            "aggressive": "aggressive when frustrated or challenged",
            "cooperative": "cooperative and willing to work with others",
            "suspicious": "suspicious of others' motives",
            "optimistic": "optimistic despite your challenges",
            "pessimistic": "pessimistic about your situation improving",
            "talkative": "talkative and eager to share your story",
            "reserved": "reserved and speak only when necessary",
            "emotional": "emotional and express your feelings openly",
            "stoic": "stoic and rarely show emotions",
            "manipulative": "manipulative when trying to get what you need",
            "honest": "honest and straightforward in your communication",
            "confused": "confused and sometimes have trouble following conversations"
        }
        
        return [trait_map.get(trait, trait) for trait in traits]
    
    def _humanize_communication_style(self, style: str) -> str:
        """Convert communication style code to description"""
        style_map = {
            "direct": "You communicate directly and say what you mean.",
            "indirect": "You communicate indirectly, often hinting at what you really mean.",
            "formal": "You maintain formal, polite communication.",
            "casual": "You speak casually and informally.",
            "verbose": "You tend to speak at length and provide many details.",
            "brief": "You keep your responses brief and to the point.",
            "emotional": "You express strong emotions when you speak.",
            "logical": "You focus on facts and logic rather than emotions.",
            "confrontational": "You can be confrontational when discussing difficult topics.",
            "avoidant": "You tend to avoid difficult topics and change the subject."
        }
        
        return style_map.get(style, f"You communicate in a {style} manner.")
    
    def generate_conversation_context(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format message history for the AI API.
        
        Args:
            messages: List of Message objects from the database
            
        Returns:
            List of message dictionaries formatted for the API
        """
        formatted_messages = []
        
        for message in messages:
            formatted_messages.append({
                "role": message.role,
                "content": message.content
            })
        
        return formatted_messages
    
    def create_reminder_prompt(self, client: ClientProfile) -> str:
        """
        Create a brief reminder prompt to reinforce character consistency.
        Used when conversations get long.
        
        Args:
            client: ClientProfile object
            
        Returns:
            Brief reminder string
        """
        reminder = f"Remember: You are {client.name}"
        
        if client.issues:
            primary_issue = self._humanize_issues([client.issues[0]])[0]
            reminder += f", dealing with {primary_issue}"
        
        if client.personality_traits and len(client.personality_traits) > 0:
            primary_trait = self._humanize_personality_traits([client.personality_traits[0]])[0]
            reminder += f", and you tend to be {primary_trait}"
        
        reminder += ". Stay in character."
        
        return reminder


# Create singleton instance
prompt_service = PromptService()
