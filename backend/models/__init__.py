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
    SessionBase,
    SessionCreate,
    SessionUpdate,
    Session,
    SessionSummary,
    SendMessageRequest,
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

from .assignment import (
    AssignmentDB,
    AssignmentClientDB,
    AssignmentType,
    AssignmentCreate,
    AssignmentUpdate,
    Assignment,
    AssignmentClientCreate,
    AssignmentClient,
    ASSIGNMENT_SETTINGS_SUGGESTIONS
)

from .message import (
    MessageDB,
    MessageBase,
    MessageCreate,
    Message
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
    'SessionBase',
    'SessionCreate',
    'SessionUpdate',
    'Session',
    'SessionSummary',
    'SendMessageRequest',
    'EndSessionRequest',
    
    # Course Section
    'CourseSectionDB',
    'SectionEnrollmentDB',
    'CourseSectionCreate',
    'CourseSectionUpdate',
    'CourseSection',
    'SectionEnrollmentCreate',
    'SectionEnrollment',
    
    # Assignment
    'AssignmentDB',
    'AssignmentClientDB',
    'AssignmentType',
    'AssignmentCreate',
    'AssignmentUpdate',
    'Assignment',
    'AssignmentClientCreate',
    'AssignmentClient',
    'ASSIGNMENT_SETTINGS_SUGGESTIONS',
    
    # Message
    'MessageDB',
    'MessageBase',
    'MessageCreate',
    'Message',
]
