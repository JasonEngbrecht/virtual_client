# Virtual Client - Data Models

Complete reference for all data models in the Virtual Client system.

## 📊 Model Overview

### Data Hierarchy
```
Teacher
├── Course Sections
│   ├── Enrolled Students
│   └── Assignments
│       └── Assignment Clients (Client + Rubric pairs)
├── Client Profiles (reusable across assignments)
└── Evaluation Rubrics (reusable across assignments)

Student
├── Course Enrollments
└── Sessions
    ├── Assignment Sessions (linked to specific assignment)
    └── Practice Sessions (free practice)
```

## ✅ Implemented Models

### ClientProfile
Virtual clients created by teachers for practice scenarios.

```json
{
    "id": "uuid",
    "name": "string",
    "age": "integer",
    "race": "string",
    "gender": "string",
    "socioeconomic_status": "string",
    "issues": ["housing_insecurity", "substance_abuse", ...],
    "background_story": "text",
    "personality_traits": ["defensive", "anxious", ...],
    "communication_style": "string",
    "created_by": "teacher_id",
    "created_at": "timestamp"
}
```

**Key Features:**
- Teacher-owned resources
- Rich demographic information
- Multiple issues/challenges
- Personality configuration for AI responses
- Reusable across multiple assignments

### EvaluationRubric
Structured evaluation criteria for assessing student performance.

```json
{
    "id": "uuid",
    "name": "string",
    "description": "text",
    "criteria": [
        {
            "name": "Empathy",
            "description": "Shows understanding...",
            "weight": 0.25,
            "evaluation_points": ["Active listening", "Validation", ...],
            "scoring_levels": {
                "excellent": 4,
                "good": 3,
                "satisfactory": 2,
                "needs_improvement": 1
            }
        }
    ],
    "created_by": "teacher_id",
    "created_at": "timestamp"
}
```

**Validation Rules:**
- Criteria weights must sum to 1.0
- Each criterion must have unique name
- Weights must be between 0.0 and 1.0
- At least one criterion required

### CourseSection
Organizational unit for teacher-student relationships.

```json
{
    "id": "uuid",
    "teacher_id": "string",
    "name": "string",  // e.g., "SW 101 - Fall 2025"
    "description": "text",
    "course_code": "string",  // e.g., "SW101"
    "term": "string",  // e.g., "Fall 2025"
    "is_active": "boolean",
    "created_at": "timestamp",
    "settings": {}  // section-specific settings
}
```

**Key Features:**
- Teacher isolation via teacher_id
- Flexible settings JSON field
- Active/inactive status
- Optional course code and term

### SectionEnrollment
Links students to course sections with soft delete support.

```json
{
    "id": "uuid",
    "section_id": "uuid",
    "student_id": "string",
    "enrolled_at": "timestamp",
    "is_active": "boolean",
    "role": "student|ta"  // future: teaching assistants
}
```

**Business Rules:**
- No duplicate active enrollments
- Soft delete preserves history
- Re-enrollment reactivates existing record
- Role field for future TA support

### Assignment
Teacher-created practice assignments within sections.

```json
{
    "id": "uuid",
    "section_id": "uuid",  // belongs to a course section
    "title": "string",
    "description": "text",
    "type": "practice|graded",
    "settings": {  // flexible JSON field
        "time_limit": 30,
        "allow_notes": true,
        "show_rubric": true
    },
    "available_from": "timestamp",
    "due_date": "timestamp",
    "is_published": "boolean",
    "max_attempts": "integer|null",  // null = unlimited
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

**Key Features:**
- Practice vs Graded assignment types
- Flexible settings via JSON field
- Date-based availability control
- Publishing workflow (draft → published)
- Optional attempt limiting

**Validation Rules:**
- Title required (1-200 chars)
- Due date must be after available_from
- Max attempts must be positive or null

### AssignmentClient
Links clients and rubrics to assignments with soft delete support.

```json
{
    "id": "uuid",
    "assignment_id": "uuid",
    "client_id": "uuid",
    "rubric_id": "uuid",
    "is_active": "boolean",  // soft delete
    "display_order": "integer"  // order clients appear to students
}
```

**Key Features:**
- Many-to-many relationship with rubric per pair
- Soft delete for preserving history
- Display ordering for student experience
- Each client can have different rubric

## ⏳ Planned Models (Not Yet Implemented)

### Session (Phase 1.6 - Enhanced)
Student practice sessions with virtual clients.

```json
{
    "id": "uuid",
    "student_id": "string",
    "section_id": "uuid",  // which course section (null for practice)
    "assignment_id": "uuid",  // null for practice sessions
    "assignment_client_id": "uuid",  // specific client within assignment
    "client_profile_id": "uuid",
    "rubric_id": "uuid",
    "session_type": "assignment|practice",
    "attempt_number": "integer",
    "messages": [
        {
            "role": "student|client|system",
            "content": "text",
            "timestamp": "datetime",
            "metadata": {}  // emotion state, topics, etc.
        }
    ],
    "started_at": "timestamp",
    "ended_at": "timestamp",
    "is_active": "boolean",
    "evaluation_result_id": "uuid",
    "evaluation_visible_to_student": "boolean",
    "session_notes": "text"
}
```

**Session Types:**
- **Practice**: Student-initiated, any client/rubric
- **Assignment**: Following assignment rules, tracked attempts

### Evaluation (Phase 1.7)
Automated evaluation results based on rubrics.

```json
{
    "id": "uuid",
    "session_id": "uuid",
    "rubric_id": "uuid",
    "overall_score": "float",
    "criteria_scores": [
        {
            "criterion_name": "string",
            "score": "integer",
            "feedback": "text",
            "examples": ["specific quotes or behaviors"]
        }
    ],
    "strengths": ["text"],
    "areas_for_improvement": ["text"],
    "generated_at": "timestamp",
    "reviewed_by_teacher": "boolean",
    "teacher_notes": "text"
}
```

**Features:**
- Detailed per-criterion feedback
- Specific examples from conversation
- Teacher review capability
- Visibility controlled by assignment settings

## 🔗 Model Relationships

### Core Relationships
```
Teacher ──owns──> ClientProfile
Teacher ──owns──> EvaluationRubric
Teacher ──owns──> CourseSection

CourseSection ──contains──> SectionEnrollment
SectionEnrollment ──references──> Student

CourseSection ──contains──> Assignment
Assignment ──contains──> AssignmentClient
AssignmentClient ──links──> ClientProfile + EvaluationRubric

Student ──creates──> Session
Session ──references──> ClientProfile + EvaluationRubric
Session ──produces──> Evaluation
```

### Key Constraints
1. **Teacher Isolation**: Teachers can only see/modify their own resources
2. **Enrollment Required**: Students must be enrolled to see section content
3. **Soft Delete**: Enrollments use soft delete to preserve history
4. **Cascade Protection**: Can't delete rubrics/clients if in use
5. **Assignment Rules**: Sessions must follow assignment constraints

## 📝 Implementation Notes

### Database Considerations
- All models use UUID primary keys
- Timestamps use UTC
- JSON fields for flexible settings/metadata
- Proper indexes on foreign keys
- Soft delete pattern for historical data

### API Design
- Nested routes for hierarchical data (e.g., `/sections/{id}/assignments`)
- Teacher endpoints require teacher authentication
- Student endpoints check enrollment
- 404 instead of 403 for security (don't reveal existence)

### Future Considerations
- Archive/restore functionality
- Bulk operations (import/export)
- Template system for common scenarios
- Analytics and reporting models
- Integration with external LMS

## 🚀 MVP Models (Temporary Simplified Versions)

### Session (Simplified for MVP)
Minimal session tracking focused on core conversation functionality.

```json
{
    "id": "uuid",
    "student_id": "string",
    "client_profile_id": "uuid",
    "started_at": "timestamp",
    "ended_at": "timestamp",
    "status": "active|completed|abandoned",
    "total_tokens": "integer",
    "estimated_cost": "decimal"
}
```

**MVP Features:**
- Simple status tracking
- Cost monitoring from day 1
- No complex relationships yet
- Will be enhanced based on learnings

### Message (✅ Implemented)
Proper message storage designed for 6M+ messages per semester.

```json
{
    "id": "uuid",
    "session_id": "uuid",
    "role": "user|assistant",  // simplified for MVP
    "content": "text",
    "timestamp": "datetime",
    "token_count": "integer",
    "sequence_number": "integer"
}
```

**Design Decisions:**
- Separate table, NOT stored as JSON in session
- Indexed for efficient queries (session_id + timestamp, session_id + sequence)
- Token counting built-in
- Sequence number for ordering
- Ready for pagination
- Content validation ensures non-empty messages
- Role limited to user/assistant for MVP (can expand later)

### MVP Implementation Notes

**What's Different:**
- No assignment linking yet
- No rubric association
- No attempt tracking
- Focused purely on conversation quality

**Migration Path:**
After MVP validation, these models will be enhanced with:
- Assignment relationships
- Rubric associations
- Attempt tracking
- Session metadata
- Evaluation readiness

**Database Schema (MVP):**
```sql
-- Simplified sessions table
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    student_id VARCHAR NOT NULL,
    client_profile_id VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0,
    FOREIGN KEY (client_profile_id) REFERENCES client_profiles(id)
);

-- Messages table built for scale
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    token_count INTEGER NOT NULL,
    sequence_number INTEGER NOT NULL,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_session_sequence (session_id, sequence_number),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

*This document serves as the authoritative reference for all data models in the Virtual Client system.*