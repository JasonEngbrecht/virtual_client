"""
Models module
Contains all SQLAlchemy ORM models and Pydantic schemas
"""

from .client_profile import (
    ClientProfileDB,
    ClientProfileBase,
    ClientProfileCreate,
    ClientProfileUpdate,
    ClientProfile,
    PREDEFINED_ISSUES,
    PERSONALITY_TRAITS,
    COMMUNICATION_STYLES
)

from .evaluation import (
    EvaluationDB,
    CriterionScore,
    EvaluationBase,
    EvaluationCreate,
    Evaluation,
    EvaluationSummary,
    ProgressReport,
    EvaluationRequest
)

from .rubric import (
    EvaluationRubricDB,
    ScoringLevel,
    RubricCriterion,
    EvaluationRubricBase,
    EvaluationRubricCreate,
    EvaluationRubricUpdate,
    EvaluationRubric,
    SAMPLE_RUBRIC_CRITERIA
)

from .session import (
    SessionDB,
    Message,
    SessionBase,
    SessionCreate,
    SessionUpdate,
    Session,
    SessionSummary,
    SendMessageRequest,
    SendMessageResponse,
    EndSessionRequest
)

from .course_section import (
    CourseSectionDB,
    SectionEnrollmentDB,
    CourseSectionCreate,
    CourseSectionUpdate,
    CourseSection,
    SectionEnrollmentCreate,
    SectionEnrollment
)

# Export all models for easy access
__all__ = [
    # Client Profile
    'ClientProfileDB',
    'ClientProfileBase',
    'ClientProfileCreate',
    'ClientProfileUpdate',
    'ClientProfile',
    'PREDEFINED_ISSUES',
    'PERSONALITY_TRAITS',
    'COMMUNICATION_STYLES',
    
    # Evaluation
    'EvaluationDB',
    'CriterionScore',
    'EvaluationBase',
    'EvaluationCreate',
    'Evaluation',
    'EvaluationSummary',
    'ProgressReport',
    'EvaluationRequest',
    
    # Rubric
    'EvaluationRubricDB',
    'ScoringLevel',
    'RubricCriterion',
    'EvaluationRubricBase',
    'EvaluationRubricCreate',
    'EvaluationRubricUpdate',
    'EvaluationRubric',
    'SAMPLE_RUBRIC_CRITERIA',
    
    # Session
    'SessionDB',
    'Message',
    'SessionBase',
    'SessionCreate',
    'SessionUpdate',
    'Session',
    'SessionSummary',
    'SendMessageRequest',
    'SendMessageResponse',
    'EndSessionRequest',
    
    # Course Section
    'CourseSectionDB',
    'SectionEnrollmentDB',
    'CourseSectionCreate',
    'CourseSectionUpdate',
    'CourseSection',
    'SectionEnrollmentCreate',
    'SectionEnrollment',
]
