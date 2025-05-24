"""
Evaluation Model
Represents the evaluation results of a student's session performance
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Float, Integer
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from ..services.database import Base


# SQLAlchemy ORM Model
class EvaluationDB(Base):
    """Database model for evaluation results"""
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    rubric_id = Column(String, nullable=False)
    overall_score = Column(Float, nullable=False)  # Weighted average score
    total_possible = Column(Float, nullable=False)  # Maximum possible score
    percentage_score = Column(Float, nullable=False)  # Percentage (0-100)
    criteria_scores = Column(JSON, nullable=False)  # Detailed scores per criterion
    feedback = Column(Text)  # Generated feedback text
    strengths = Column(JSON)  # List of identified strengths
    improvements = Column(JSON)  # List of areas for improvement
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic Models for API
class CriterionScore(BaseModel):
    """Score for an individual rubric criterion"""
    criterion_name: str
    score: int = Field(..., ge=1, le=4)  # 1-4 scale
    max_score: int = 4
    weight: float
    weighted_score: float
    feedback: str
    evidence: List[str] = Field(default_factory=list)  # Specific examples from conversation


class EvaluationBase(BaseModel):
    """Base evaluation schema"""
    session_id: str
    student_id: str
    rubric_id: str
    overall_score: float = Field(..., ge=0)
    total_possible: float = Field(..., gt=0)
    percentage_score: float = Field(..., ge=0, le=100)
    criteria_scores: List[CriterionScore]
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation"""
    pass


class Evaluation(EvaluationBase):
    """Complete evaluation schema with metadata"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class EvaluationSummary(BaseModel):
    """Summary view of evaluation for quick reference"""
    id: str
    session_id: str
    student_id: str
    percentage_score: float
    created_at: datetime
    strengths_count: int = 0
    improvements_count: int = 0


class ProgressReport(BaseModel):
    """Student progress report across multiple sessions"""
    student_id: str
    total_sessions: int
    evaluated_sessions: int
    average_score: float
    score_trend: List[float]  # Scores over time
    common_strengths: List[str]
    common_improvements: List[str]
    sessions_by_client_type: Dict[str, int]  # Count by client issue type
    improvement_areas: Dict[str, float]  # Average score by criterion


class EvaluationRequest(BaseModel):
    """Request schema for triggering an evaluation"""
    session_id: str
    auto_feedback: bool = True  # Whether to generate automated feedback
