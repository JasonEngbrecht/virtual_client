"""
Evaluation Rubric Model
Represents evaluation criteria and scoring for student performance assessment
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
import uuid

Base = declarative_base()


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
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    weight: float = Field(..., ge=0, le=1)
    evaluation_points: List[str] = Field(..., min_items=1)
    scoring_levels: ScoringLevel = Field(default_factory=ScoringLevel)
    
    @validator('weight')
    def validate_weight(cls, v):
        """Ensure weight is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError('Weight must be between 0 and 1')
        return v


class EvaluationRubricBase(BaseModel):
    """Base evaluation rubric schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    criteria: List[RubricCriterion] = Field(..., min_items=1)
    
    @validator('criteria')
    def validate_total_weight(cls, v):
        """Ensure all criteria weights sum to 1.0"""
        total_weight = sum(criterion.weight for criterion in v)
        if abs(total_weight - 1.0) > 0.001:  # Allow small floating point differences
            raise ValueError(f'Criteria weights must sum to 1.0, got {total_weight}')
        return v


class EvaluationRubricCreate(EvaluationRubricBase):
    """Schema for creating a new evaluation rubric"""
    pass


class EvaluationRubricUpdate(BaseModel):
    """Schema for updating an evaluation rubric"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    criteria: Optional[List[RubricCriterion]] = None
    
    @validator('criteria')
    def validate_total_weight_if_provided(cls, v):
        """Ensure criteria weights sum to 1.0 if criteria are provided"""
        if v is not None:
            total_weight = sum(criterion.weight for criterion in v)
            if abs(total_weight - 1.0) > 0.001:
                raise ValueError(f'Criteria weights must sum to 1.0, got {total_weight}')
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
