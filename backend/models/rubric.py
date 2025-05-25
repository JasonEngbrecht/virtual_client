"""
Evaluation Rubric Model
Represents evaluation criteria and scoring for student performance assessment
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Float
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from ..services.database import Base


# SQLAlchemy ORM Model
class EvaluationRubricDB(Base):
    """Database model for evaluation rubrics"""
    __tablename__ = "evaluation_rubrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    criteria = Column(JSON, nullable=False)  # List of criteria with details
    total_weight = Column(Float, default=1.0)  # Should sum to 1.0
    created_by = Column(String, nullable=False)  # Teacher ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Models for API
class ScoringLevel(BaseModel):
    """Scoring level definition"""
    excellent: int = 4
    good: int = 3
    satisfactory: int = 2
    needs_improvement: int = 1


class RubricCriterion(BaseModel):
    """Individual evaluation criterion"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Name of the evaluation criterion (e.g., 'Communication Skills')"
    )
    description: str = Field(
        ...,
        description="Detailed description of what this criterion evaluates"
    )
    weight: float = Field(
        ..., 
        ge=0, 
        le=1,
        description="Weight of this criterion (0.0 to 1.0). All criteria weights must sum to 1.0"
    )
    evaluation_points: List[str] = Field(
        ..., 
        min_items=1,
        description="List of specific behaviors or skills to evaluate (at least one required)"
    )
    scoring_levels: ScoringLevel = Field(
        default_factory=ScoringLevel,
        description="Scoring levels for this criterion (defaults to 4-point scale)"
    )
    
    @validator('weight')
    def validate_weight(cls, v):
        """Ensure weight is between 0 and 1"""
        if v < 0:
            raise ValueError(f'Criterion weight cannot be negative. You provided {v}, but weights must be between 0.0 and 1.0')
        if v > 1:
            raise ValueError(f'Criterion weight cannot exceed 1.0. You provided {v}, but the maximum allowed weight is 1.0')
        return v


class EvaluationRubricBase(BaseModel):
    """Base evaluation rubric schema"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Name of the evaluation rubric"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the rubric's purpose and use"
    )
    criteria: List[RubricCriterion] = Field(
        ..., 
        min_items=1,
        description="List of evaluation criteria. At least one criterion is required"
    )
    
    @validator('criteria')
    def validate_total_weight(cls, v):
        """Ensure all criteria weights sum to 1.0"""
        if not v:
            raise ValueError('At least one evaluation criterion is required')
        
        total_weight = sum(criterion.weight for criterion in v)
        
        # Allow small floating point differences (0.001 tolerance)
        if abs(total_weight - 1.0) > 0.001:
            # Provide helpful error message with current sum and guidance
            criteria_info = [f"{c.name}: {c.weight}" for c in v]
            raise ValueError(
                f'Criteria weights must sum to exactly 1.0, but your weights sum to {total_weight:.3f}. '
                f'Current weights: {{", ".join(criteria_info)}}. '
                f'Please adjust the weights so they total 1.0 (100% of the evaluation).'
            )
        return v


class EvaluationRubricCreate(EvaluationRubricBase):
    """Schema for creating a new evaluation rubric"""
    pass


class EvaluationRubricUpdate(BaseModel):
    """Schema for updating an evaluation rubric"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Updated name for the evaluation rubric"
    )
    description: Optional[str] = Field(
        None,
        description="Updated description of the rubric's purpose and use"
    )
    criteria: Optional[List[RubricCriterion]] = Field(
        None,
        description="Updated list of evaluation criteria (if provided, must have valid weights summing to 1.0)"
    )
    
    @validator('criteria')
    def validate_total_weight_if_provided(cls, v):
        """Ensure criteria weights sum to 1.0 if criteria are provided"""
        if v is not None:
            if len(v) == 0:
                raise ValueError('If updating criteria, at least one criterion must be provided')
                
            total_weight = sum(criterion.weight for criterion in v)
            
            # Allow small floating point differences (0.001 tolerance)
            if abs(total_weight - 1.0) > 0.001:
                # Provide helpful error message with current sum and guidance
                criteria_info = [f"{c.name}: {c.weight}" for c in v]
                raise ValueError(
                    f'When updating criteria, weights must sum to exactly 1.0, but your weights sum to {total_weight:.3f}. '
                    f'Current weights: {{", ".join(criteria_info)}}. '
                    f'Please adjust the weights so they total 1.0 (100% of the evaluation).'
                )
        return v


class EvaluationRubric(EvaluationRubricBase):
    """Complete evaluation rubric schema with metadata"""
    id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Sample rubric template
SAMPLE_RUBRIC_CRITERIA = [
    {
        "name": "Empathy & Understanding",
        "description": "Demonstrates understanding and empathy for client's situation",
        "weight": 0.25,
        "evaluation_points": [
            "Validates client's feelings",
            "Shows active listening",
            "Reflects understanding",
            "Avoids judgment"
        ]
    },
    {
        "name": "Communication Skills",
        "description": "Uses appropriate communication techniques",
        "weight": 0.25,
        "evaluation_points": [
            "Clear and concise language",
            "Appropriate tone",
            "Open-ended questions",
            "Clarification when needed"
        ]
    },
    {
        "name": "Professional Boundaries",
        "description": "Maintains appropriate professional boundaries",
        "weight": 0.20,
        "evaluation_points": [
            "Maintains professional role",
            "Avoids personal disclosure",
            "Respects client autonomy",
            "Appropriate self-disclosure"
        ]
    },
    {
        "name": "Assessment Skills",
        "description": "Gathers relevant information effectively",
        "weight": 0.15,
        "evaluation_points": [
            "Asks relevant questions",
            "Explores important areas",
            "Identifies key issues",
            "Prioritizes concerns"
        ]
    },
    {
        "name": "Intervention Planning",
        "description": "Develops appropriate intervention strategies",
        "weight": 0.15,
        "evaluation_points": [
            "Identifies resources",
            "Collaborative planning",
            "Realistic goals",
            "Client-centered approach"
        ]
    }
]
