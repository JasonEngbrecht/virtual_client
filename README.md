# Virtual Client - Social Work Training App

**Status:** In Development | **Phase:** 1.4 Part 5 Complete ✅ | **Next:** Phase 1.4 Part 6 - Student Section Access

This project will create a virtual client that social work (and other areas) can interface with to practice working with clients.

## 🌟 Latest Achievement
**Phase 1.4 Part 5 COMPLETE** ✅ - Enrollment Management Endpoints:
- ✅ **Part 5**: Implemented teacher endpoints for enrollment management
  - GET /api/teacher/sections/{id}/roster - View enrolled students
  - POST /api/teacher/sections/{id}/enroll - Enroll a student
  - DELETE /api/teacher/sections/{id}/enroll/{student_id} - Unenroll (soft delete)
  - Teacher isolation enforced on all operations
  - Comprehensive error handling (404, 403, 400, 422)
  - 15 integration tests all passing
  - Follows established patterns from previous endpoints

**Previous Achievement:** Phase 1.4 Part 4 COMPLETE - Enrollment Service Layer:
- ✅ **Part 4**: Implemented comprehensive enrollment management service
  - `enroll_student()` - Enrolls students with duplicate prevention and reactivation
  - `unenroll_student()` - Soft delete preserving enrollment history
  - `get_section_roster()` - Retrieves active/inactive enrollments
  - `is_student_enrolled()` - Checks active enrollment status
  - `get_student_sections()` - Gets all sections for a student
  - Business rules: No duplicates, soft delete, section validation
  - 20 comprehensive unit tests all passing
  - Fixed SQLAlchemy session management issues in tests
  - Following established service patterns

**Previous Achievement:** Phase 1.4 Part 3 COMPLETE - Section CRUD Endpoints:
- ✅ **Part 3**: Implemented all 5 CRUD endpoints for course sections
  - GET /api/teacher/sections - List teacher's sections
  - POST /api/teacher/sections - Create new section
  - GET /api/teacher/sections/{id} - Get section details
  - PUT /api/teacher/sections/{id} - Update section (partial updates supported)
  - DELETE /api/teacher/sections/{id} - Delete section (cascades to enrollments)
  - Teacher isolation enforced on all operations
  - Comprehensive error handling (404, 403, 400, 422)
  - 18 integration tests all passing
  - Follows established patterns from client and rubric endpoints

**Previous Achievement:** Phase 1.4 Part 2 COMPLETE - Basic Section Service:
- ✅ **Part 2**: Created SectionService with teacher-specific operations
  - Service class inheriting from BaseCRUD
  - Methods: get_teacher_sections, create_section_for_teacher
  - Permission checks: can_update, can_delete
  - Comprehensive unit tests (11 test cases)
  - Follows established patterns from ClientService and RubricService

**Previous Achievement:** Phase 1.3 COMPLETE - EvaluationRubric CRUD implementation (All 7 Parts Complete):
- ✅ **Part 1**: RubricService class inheriting from BaseCRUD
- ✅ **Part 2**: Teacher-filtered methods (get_teacher_rubrics, create_rubric_for_teacher, can_update, can_delete)
- ✅ **Part 3**: GET /api/teacher/rubrics endpoint with integration test
- ✅ **Part 4**: All CRUD endpoints implemented:
  - POST /api/teacher/rubrics (create with criteria validation)
  - GET /api/teacher/rubrics/{id} (retrieve specific rubric)
  - PUT /api/teacher/rubrics/{id} (update with partial support)
  - DELETE /api/teacher/rubrics/{id} (delete with basic functionality)
- ✅ **Part 5**: Cascade protection preventing deletion of rubrics in use (409 Conflict)
- ✅ **Part 6**: Enhanced validation with user-friendly error messages:
  - Weight validation shows actual values provided
  - Weight sum errors include breakdown of all criteria weights
  - Duplicate criterion name prevention
  - Clear guidance on fixing validation errors
- ✅ **Part 7**: Comprehensive test suite (`test_phase_1_3_complete.py`)
  - Tests all endpoints with various scenarios
  - Verifies teacher isolation
  - Tests edge cases and error handling
  - All 29 rubric-related tests passing

**Implementation Time:** ~3 hours (met estimate of 2-3 hours)

**Previous Achievement:** Phase 1.2 COMPLETE - Full ClientProfile CRUD with enhanced error handling (~3.25 hours)

**Current Progress:** Phase 1.4 Parts 1-4 COMPLETE
- ✅ Part 1: Database Models (25 minutes) 
- ✅ Part 2: Section Service (30 minutes)
- ✅ Part 3: Section CRUD Endpoints (45 minutes)
- ✅ Part 4: Enrollment Service Layer (45 minutes)
- Total Phase 1.4 time so far: 235 minutes (~3.9 hours)

**Next:** Phase 1.4 Part 6 - Student Section Access

## Project Overview

An educational application designed to help social work students practice client interactions through AI-powered simulations. The app allows teachers to create virtual clients with specific demographics and issues, upload evaluation rubrics, and enables students to engage in realistic practice sessions with automated feedback.

## Development Environment

This project is being developed using **PyCharm IDE**.

### PyCharm Configuration
1. Open the project in PyCharm
2. Configure the Python interpreter to use the virtual environment
3. Set up run configurations for FastAPI
4. Configure code style and linting preferences

For detailed setup instructions, run: `python setup_instructions.py`

## Core Features

### 1. Teacher Capabilities
- **Virtual Client Creation**
  - Set client demographics (age, race, gender, socioeconomic status)
  - Select from predefined issues/challenges
  - Customize personality traits and communication styles
  - Generate background stories

- **Rubric Management**
  - Upload custom evaluation rubrics
  - Define evaluation criteria with weights
  - Set scoring levels and expectations
  - Save and reuse rubrics across sessions

### 2. Student Capabilities
- **Interactive Sessions**
  - Chat-based interface with virtual client
  - Realistic client responses powered by LLM
  - Session recording and transcript generation
  - Practice mode with different client scenarios

- **Feedback System**
  - Automated evaluation based on teacher's rubric
  - Detailed feedback on performance
  - Areas of improvement identification
  - Progress tracking over multiple sessions

## Technical Architecture

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite (for demo)
- **LLM Integration**: OpenAI API (GPT-4) or Anthropic Claude
- **Frontend Options**: 
  - Streamlit (rapid prototyping)
  - Flask + Bootstrap (traditional web)
  - React/Vue (advanced UI)
- **IDE**: PyCharm

### Project Structure
```
virtual_client/
├── backend/
│   ├── app.py                 # Main application entry
│   ├── models/
│   │   ├── client_profile.py  # Virtual client data model
│   │   ├── rubric.py          # Evaluation rubric model
│   │   ├── session.py         # Interaction session model
│   │   └── evaluation.py      # Evaluation results model
│   ├── services/
│   │   ├── database.py        # Base database service
│   │   ├── client_service.py  # Client profile CRUD operations
│   │   ├── rubric_service.py  # Rubric CRUD operations
│   │   ├── session_service.py # Session management
│   │   ├── evaluation_service.py  # Evaluation generation & retrieval
│   │   ├── llm_service.py     # LLM API integration
│   │   └── storage_service.py # Generic database operations
│   ├── prompts/
│   │   └── client_prompts.py  # LLM prompt templates
│   ├── api/
│   │   ├── teacher_routes.py  # Teacher endpoints
│   │   └── student_routes.py  # Student endpoints
│   └── scripts/
│       └── init_db.py         # Database initialization
├── frontend/
│   ├── teacher_dashboard.py   # Teacher interface
│   └── student_interface.py   # Student chat interface
├── database/
│   ├── schema.sql            # Database schema
│   └── app.db               # SQLite database file
├── tests/
│   ├── conftest.py           # Pytest configuration
│   ├── factories.py          # Test data factories
│   ├── unit/                 # Unit tests
│   │   ├── test_client_service.py
│   │   ├── test_rubric_service.py
│   │   └── test_session_service.py
│   └── integration/          # Integration tests
│       ├── test_teacher_api.py
│       └── test_student_api.py
├── requirements.txt
├── .env                      # Environment variables
└── README.md
```

## Data Models

### ClientProfile
```python
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

### EvaluationRubric
```python
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

### CourseSection (NEW)
```python
{
    "id": "uuid",
    "teacher_id": "string",
    "name": "string",  # e.g., "SW 101 - Fall 2025"
    "description": "text",
    "course_code": "string",  # e.g., "SW101"
    "term": "string",  # e.g., "Fall 2025"
    "is_active": "boolean",
    "created_at": "timestamp",
    "settings": {}  # section-specific settings
}
```

### SectionEnrollment (NEW)
```python
{
    "id": "uuid",
    "section_id": "uuid",
    "student_id": "string",
    "enrolled_at": "timestamp",
    "is_active": "boolean",
    "role": "student|ta"  # future: teaching assistants
}
```

### Assignment (NEW)
```python
{
    "id": "uuid",
    "section_id": "uuid",  # belongs to a course section
    "name": "string",
    "description": "text",
    "instructions": "text",
    "due_date": "timestamp",
    "available_from": "timestamp",
    "available_until": "timestamp",
    "max_attempts_per_client": "integer",
    "show_evaluation_immediately": "boolean",
    "allow_practice_mode": "boolean",
    "is_published": "boolean",
    "created_at": "timestamp",
    "order": "integer"  # display order in section
}
```

### AssignmentClient (NEW)
```python
{
    "id": "uuid",
    "assignment_id": "uuid",
    "client_profile_id": "uuid",
    "rubric_id": "uuid",
    "order": "integer",  # which client to complete first/second/etc
    "is_required": "boolean",  # future: optional clients
    "special_instructions": "text"  # client-specific instructions
}
```

### Session (UPDATED)
```python
{
    "id": "uuid",
    "student_id": "string",
    "section_id": "uuid",  # which course section (null for practice)
    "assignment_id": "uuid",  # null for practice sessions
    "assignment_client_id": "uuid",  # specific client within assignment
    "client_profile_id": "uuid",
    "rubric_id": "uuid",
    "session_type": "assignment|practice",
    "attempt_number": "integer",
    "messages": [
        {
            "role": "student|client|system",
            "content": "text",
            "timestamp": "datetime",
            "metadata": {}  # emotion state, topics, etc.
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

## Implementation Roadmap

### Phase 1: Foundation - CRUD Implementation
- [x] Set up project structure
- [x] Configure FastAPI application
- [x] Design and implement data models
- [x] Set up SQLite database with schema
- [x] **Phase 1.1: Database Foundation & Base Service** ✅ **COMPLETED**
  - [x] Database initialization script (`backend/scripts/init_db.py`)
  - [x] Base database service with session management
  - [x] Testing setup with pytest (15 tests, all passing)
  - [x] Generic BaseCRUD class for reusable operations
  - [x] SQLAlchemy 2.0 compatibility fixes
  - [x] PyCharm run configurations
  - [x] Test fixtures and comprehensive test coverage
- [x] **Phase 1.2: ClientProfile CRUD** ✅ **COMPLETED**
  - [x] Storage service for client operations
  - [x] Teacher API routes (Create, Read, Update, Delete)
  - [x] Unit and integration tests
  
  **Incremental Implementation Plan for Phase 1.2:**
  
  To ensure successful implementation and catch errors early, Phase 1.2 will be completed in small, testable parts:
  
  **Part 1: Basic Client Service (No Authentication)** ✅
  - [x] Create minimal ClientService class inheriting from BaseCRUD
  - [x] Write basic instantiation test
  - [x] Verify BaseCRUD inheritance works correctly
  
  **Part 2: Add Teacher-Filtered Methods** ✅
  - [x] Implement get_teacher_clients() method with unit test
  - [x] Implement create_client_for_teacher() method with unit test
  - [x] Add permission check methods (can_update, can_delete) with tests
  
  **Part 3: Create Minimal API Router** ✅
  - [x] Create teacher_routes.py with empty router
  - [x] Add single GET /test endpoint
  - [x] Update app.py to include router
  - [x] Verify endpoint accessibility
  
  **Part 4: Add One Endpoint at a Time** ✅
  - [x] GET /clients (list) with hardcoded teacher_id
  - [x] POST /clients (create)
  - [x] GET /clients/{id} (retrieve)
  - [x] PUT /clients/{id} (update)
  - [x] DELETE /clients/{id} (delete)
  - [x] Test each endpoint with curl/Postman before moving to next
  
  **Part 5: Add Authentication Placeholder** ✅
  - [x] Create get_current_teacher() dependency
  - [x] Replace hardcoded teacher_id with dependency
  - [x] Verify endpoints work with mock auth
  
  **Part 6: Error Handling** ✅
  - [x] Add 404 (not found) handling with clear messages
  - [x] Add 403 (permission denied) handling for unauthorized access
  - [x] Add 400 (validation error) handling with detailed errors
  - [x] Test each error case thoroughly
  
  **Testing Strategy**: After each part, run unit tests, manual tests, and integration tests before proceeding.
- [x] **Phase 1.3: EvaluationRubric CRUD** ✅ **COMPLETED**
  - [x] Storage service with criteria validation
  - [x] Teacher API routes for rubric management
  - [x] Cascade protection testing
  - [x] Enhanced validation with user-friendly error messages
  - [x] Comprehensive test suite
  
  **Incremental Implementation Plan for Phase 1.3:**
  
  Following the successful approach from Phase 1.2, Phase 1.3 will be implemented in testable increments:
  
  **Part 1: Basic Rubric Service (15-20 minutes)** ✅
  - [x] Create `backend/services/rubric_service.py` with minimal RubricService class inheriting from BaseCRUD
  - [x] Write basic instantiation test in `tests/unit/test_rubric_service.py`
  - [x] Verify BaseCRUD inheritance works correctly
  - [x] **Test**: Unit test for service instantiation
  
  **Part 2: Add Teacher-Filtered Methods (30-45 minutes)** ✅
  - [x] Implement `get_teacher_rubrics()` method with unit test
  - [x] Implement `create_rubric_for_teacher()` method with unit test
  - [x] Add permission check methods (`can_update`, `can_delete`) with tests
  - [x] **Test**: Unit tests for each method with mock data
  
  **Part 3: Add First API Endpoint - List Rubrics (20-30 minutes)** ✅
  - [x] Add GET `/api/teacher/rubrics` endpoint to existing teacher_routes.py
  - [x] Test with curl/Postman
  - [x] Write integration test
  - [x] **Test**: Manual API test + integration test file
  
  **Part 4: Add Remaining CRUD Endpoints (45-60 minutes)** ✅
  - [x] POST `/api/teacher/rubrics` (create) - includes criteria validation
  - [x] GET `/api/teacher/rubrics/{id}` (retrieve)
  - [x] PUT `/api/teacher/rubrics/{id}` (update) - with partial update support
  - [x] DELETE `/api/teacher/rubrics/{id}` (delete) - basic version first
  - [x] **Test**: Manual testing + integration test for each endpoint
  
  **Part 5: Add Cascade Protection (30-45 minutes)** ✅
  - [x] Add `is_rubric_in_use()` method to check if rubric is referenced by sessions
  - [x] Modify delete endpoint to check before deletion
  - [x] Add appropriate error response (409 Conflict)
  - [x] Create tests with mock session data
  - [x] **Test**: Unit test for protection logic + integration test for delete with conflict
  
  **Part 6: Enhanced Validation & Error Handling (20-30 minutes)**
  - [x] Add detailed validation error messages for criteria structure
  - [x] Ensure weight validation errors are user-friendly
  - [x] Add any rubric-specific error cases
  - [x] Create comprehensive error handling test script
  - [x] **Test**: Error handling test script similar to Phase 1.2
  
  **Part 7: Comprehensive Test Suite (15-20 minutes)** ✅
  - [x] Create `test_phase_1_3_complete.py` script
  - [x] Test all endpoints with various scenarios
  - [x] Verify teacher isolation works correctly
  - [x] Test edge cases (empty criteria, invalid weights, etc.)
  - [x] **Test**: Full system test covering all functionality
  
  **Key Differences from Phase 1.2:**
  - No router creation needed (add to existing teacher_routes.py)
  - Additional complexity: criteria validation, nested data, cascade protection
  - Reuse authentication and error patterns from Phase 1.2
  
  **Estimated Timeline:** 2.5-3.5 hours total
- [ ] **Phase 1.4: Course Section Management** (IN PROGRESS - 3.5-4.5 hours)
  - [x] Part 1: Database Models and Schema ✅ (25 min)
  - [x] Part 2: Basic Section Service ✅ (30 min)
  - [x] Part 3: Section CRUD Endpoints ✅ (45 min)
  - [x] Part 4: Enrollment Service Layer ✅ (45 min)
  - ✅ Part 5: Enrollment Management Endpoints ✅ (45 min)
  - [ ] Part 6: Student Section Access (30-45 min)
  - [ ] Part 7: Section Summary and Statistics (30-40 min)
  - [ ] Part 8: Comprehensive Testing & Documentation (45-60 min)
- [ ] **Phase 1.5: Assignment Management** (NEW - 4-5 hours)
  - [ ] Assignment CRUD within sections
  - [ ] Assignment-Client-Rubric linking
  - [ ] Assignment settings and publishing
  - [ ] Student assignment viewing
- [ ] **Phase 1.6: Session Management** (REVISED - 4-5 hours)
  - [ ] Practice sessions (any client/rubric)
  - [ ] Assignment sessions (following rules)
  - [ ] Message handling and transcripts
  - [ ] Student and teacher API routes
- [ ] **Phase 1.7: Evaluation System** (ORIGINAL 1.5 - 3-4 hours)
  - [ ] Automated evaluation based on rubrics
  - [ ] Teacher review capabilities
  - [ ] Student visibility controls
- [x] Implement API documentation

### Phase 2: LLM Integration (Week 2)
- [ ] Set up LLM API connections
- [ ] Develop client personality prompt templates
- [ ] Create conversation management system
- [ ] Test different prompt strategies
- [ ] Implement response filtering/safety measures
- [ ] Build conversation context management

### Phase 3: Teacher Interface (Week 3)
- [ ] Build client profile creation form
- [ ] Implement rubric upload/creation interface
- [ ] Create teacher dashboard
- [ ] Add client profile management
- [ ] Implement rubric library
- [ ] Add preview functionality

### Phase 4: Student Interface (Week 4)
- [ ] Design chat interface
- [ ] Implement real-time messaging
- [ ] Add session management
- [ ] Create client selection screen
- [ ] Build conversation history display
- [ ] Add session controls (start/end/pause)

### Phase 5: Evaluation System (Week 5)
- [ ] Implement evaluation algorithm
- [ ] Create feedback generation system
- [ ] Build results visualization
- [ ] Add progress tracking
- [ ] Generate detailed reports
- [ ] Test evaluation accuracy

### Phase 6: Polish & Testing (Week 6)
- [ ] Comprehensive testing
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Demo preparation
- [ ] Bug fixes and refinements

## CRUD Implementation Strategy

### Overview
CRUD (Create, Read, Update, Delete) operations form the foundation of the application. Implementation follows a layered architecture with proper separation of concerns.

### Implementation Order
1. **Database Foundation** - Connection management and base service class
2. **ClientProfile** - Full CRUD for virtual client management
3. **EvaluationRubric** - CRUD with validation for evaluation criteria
4. **Session** - Create, Read, Update (messages), End operations
5. **Evaluation** - Create (automatic) and Read operations

### Architecture Pattern
```
API Route (FastAPI) → Service Layer → Database Layer (SQLAlchemy) → SQLite
```

### Testing Approach
- **Unit Tests**: Service layer logic in isolation
- **Integration Tests**: Full API endpoint testing
- **Test Database**: In-memory SQLite for speed
- **Fixtures**: Reusable test data for all models
- **Coverage Goal**: >80% code coverage
- **Test Runner**: Custom scripts for easy execution
- **PyCharm Integration**: Pre-configured test runs

### Key Principles
- **Permission-based access**: Teachers see only their data
- **Validation**: Pydantic models ensure data integrity
- **Error handling**: Appropriate HTTP status codes
- **Cascade protection**: Prevent deletion of referenced data

### Time Estimates
- Phase 1.1 (Database Foundation): 2-3 hours ✅ COMPLETED
- Phase 1.2 (ClientProfile CRUD): 3-4 hours ✅ COMPLETED (~3.25 hours)
- Phase 1.3 (EvaluationRubric CRUD): 2-3 hours ✅ COMPLETED (~3 hours)
- Phase 1.4 (Course Section Management): 3.5-4.5 hours (145 min completed, ~1.5-2.5 hours remaining)
- Phase 1.5 (Assignment Management): 4-5 hours
- Phase 1.6 (Session Management): 4-5 hours
- Phase 1.7 (Evaluation System): 3-4 hours
- **Total Estimated Time**: 23-28 hours
- **Time Completed So Far**: ~12.4 hours

## Key Technical Decisions

### LLM Prompt Strategy
The system will use structured prompts that include:
1. Client profile information
2. Personality and communication style guidelines
3. Current emotional state tracking
4. Conversation history context
5. Realistic behavior instructions

### Evaluation Approach
Two-tier evaluation system:
1. **Automated Analysis**: Keyword detection, interaction patterns, conversation flow
2. **LLM-Assisted**: Using LLM to evaluate against rubric criteria with specific examples

### Session Management
- Sessions stored as complete transcripts
- Real-time state management for active sessions
- Ability to pause and resume sessions
- Export functionality for review

## Important Considerations

### Educational Value
- Ensure realistic but appropriate client behaviors
- Balance challenge with learning objectives
- Provide constructive feedback
- Support iterative learning

### Technical Considerations
- API rate limiting for LLM calls
- Session data privacy and storage
- Scalability for multiple concurrent users
- Response time optimization

### Safety & Ethics
- Content filtering for inappropriate interactions
- Clear educational context boundaries
- Sensitivity to represented demographics
- Instructor oversight capabilities

### Future Enhancements
- Multiple language support
- Voice interaction capabilities
- Video avatar integration
- Peer review features
- Advanced analytics dashboard
- Mobile application
- Integration with LMS systems

## Data Hierarchy and Relationships

### Core Data Structure
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

### Session Types

1. **Practice Sessions**: 
   - Student-initiated free practice
   - Student selects any available client and rubric
   - Evaluations always visible immediately
   - No attempt limits
   - Not linked to any assignment

2. **Assignment Sessions**:
   - Created from teacher assignments
   - Pre-selected client(s) and rubric(s)
   - Teacher controls evaluation visibility
   - May have attempt limits
   - Must complete all clients in assignment

### Key Features

- **Full Transcript Preservation**: All messages, timestamps, and metadata saved
- **Flexible Evaluation**: Rubrics can be applied by LLM after session completion
- **Teacher Monitoring**: View sessions organized by student, client, assignment, or date
- **Evaluation Control**: Teachers decide when students see evaluations
- **Multiple Attempts**: Assignments can allow multiple attempts per student
- **Assignment Flexibility**: 
  - Assignments can include multiple client profiles
  - Each client within an assignment can have a different rubric
  - Teachers can specify order of client interactions

## Phase 1.4: Course Section Management - Detailed Implementation Plan

### Overview
Course sections form the organizational foundation for the entire system. They establish the teacher-student relationships and provide context for assignments and sessions.

**Estimated Total Time**: 3.5-4.5 hours across 8 parts

### Part 1: Database Models and Schema (20-30 minutes) ✅ COMPLETE
**Goal**: Create database models for course sections and enrollments

**Implementation**:
- ✅ Created `backend/models/course_section.py`
- ✅ SQLAlchemy models: `CourseSectionDB`, `SectionEnrollmentDB`
- ✅ Pydantic schemas: Create, Update, Response
- ✅ Updated model registry in `__init__.py`

**Test Strategy**:
- ✅ Test model creation in database
- ✅ Verify foreign key constraints
- ✅ Test enrollment relationships

**Actual Time**: 25 minutes

### Part 2: Basic Section Service (30-40 minutes) ✅ COMPLETE
**Goal**: Create section service with teacher-specific operations

**Implementation**:
- ✅ Created `backend/services/section_service.py`
- ✅ Methods: `get_teacher_sections()`, `create_section_for_teacher()`, `can_update()`, `can_delete()`
- ✅ Global service instance following established patterns

**Test Strategy**:
- ✅ Unit test service instantiation
- ✅ Test teacher filtering
- ✅ Test permission methods
- ✅ 11 comprehensive unit tests all passing

**Actual Time**: 30 minutes

### Part 3: Section CRUD Endpoints (45-60 minutes) ✅ COMPLETE
**Goal**: Add teacher endpoints for section management

**Implementation**:
- ✅ Added 5 endpoints to `backend/api/teacher_routes.py`
- ✅ GET `/api/teacher/sections` - list sections
- ✅ POST `/api/teacher/sections` - create section
- ✅ GET `/api/teacher/sections/{id}` - get details
- ✅ PUT `/api/teacher/sections/{id}` - update
- ✅ DELETE `/api/teacher/sections/{id}` - delete
- ✅ Teacher isolation and permissions enforced
- ✅ Comprehensive error handling

**Test Strategy**:
- ✅ Integration test each endpoint
- ✅ Test validation rules
- ✅ Test cascade prevention
- ✅ 18 integration tests all passing

**Actual Time**: 45 minutes

### Part 4: Enrollment Service Layer (45-60 minutes) ✅ COMPLETE
**Goal**: Implement enrollment management logic

**Implementation**:
- ✅ Created `backend/services/enrollment_service.py`
- ✅ Methods: `enroll_student()`, `unenroll_student()`, `get_section_roster()`, `is_student_enrolled()`, `get_student_sections()`
- ✅ Global service instance following established patterns

**Business Rules**:
- ✅ No duplicate enrollments (reactivates if re-enrolling)
- ✅ Soft delete for unenrollment (preserves history)
- ✅ Only active enrollments count for queries
- ✅ Section validation before enrollment

**Test Strategy**:
- ✅ 20 comprehensive unit tests
- ✅ Test duplicate handling and reactivation
- ✅ Test soft delete and history
- ✅ Fixed SQLAlchemy session management issues
- ✅ All tests passing

**Actual Time**: 45 minutes

### Part 5: Enrollment Management Endpoints (45-60 minutes)
**Goal**: Add teacher endpoints for managing enrollments

**Endpoints**:
- GET `/api/teacher/sections/{id}/roster` - view roster
- POST `/api/teacher/sections/{id}/enroll` - enroll student
- DELETE `/api/teacher/sections/{id}/enroll/{student_id}` - unenroll

**Test Strategy**:
- Test enrollment process
- Test permissions
- Test soft delete

### Part 6: Student Section Access (30-45 minutes)
**Goal**: Add student endpoints to view their sections

**Implementation**:
- Create/update `backend/api/student_routes.py`
- Mock `get_current_student()` dependency
- Endpoints: GET `/api/student/sections`, GET `/api/student/sections/{id}`

**Security Rules**:
- Students only see enrolled sections
- Cannot see full roster

### Part 7: Section Summary and Statistics (30-40 minutes)
**Goal**: Add helpful summary data and queries

**Implementation**:
- Add summary calculations
- Search functionality
- Response enhancements with counts

### Part 8: Comprehensive Testing & Documentation (45-60 minutes)
**Goal**: Ensure robust implementation with full test coverage

**Implementation**:
- Create `test_phase_1_4_complete.py`
- Test complete workflows
- Update documentation

## Current Project Status

**Last Updated:** May 25, 2025
**Current Focus:** Phase 1.4 Part 5 Complete - Ready for Part 6 (Student Section Access)

### ✅ Phase 1.4 Part 5 Complete - Enrollment Management Endpoints

#### What Was Accomplished in Part 5

**API Endpoints Implemented**
- Added 3 enrollment management endpoints to `backend/api/teacher_routes.py`
- GET /api/teacher/sections/{id}/roster - View active enrollments in section
- POST /api/teacher/sections/{id}/enroll - Enroll student (handles reactivation)
- DELETE /api/teacher/sections/{id}/enroll/{student_id} - Soft delete enrollment

**Key Features**
- Uses enrollment_service for all business logic
- Teacher can only manage enrollments for own sections
- Soft delete preserves enrollment history
- Handles re-enrollment by reactivating existing records
- Comprehensive error handling with user-friendly messages

**Testing**
- Created `tests/integration/test_enrollment_api.py` with 15 test cases
- Created `tests/integration/conftest.py` with enrollment fixtures
- All integration tests passing
- Tests cover enrollment lifecycle, permissions, and edge cases
- Manual test script verifies all functionality

**Time Taken**: 45 minutes (within estimate)

### ✅ Phase 1.3 Part 5 Complete - Cascade Protection

#### What Was Accomplished in Part 5

**Service Layer Enhancement**
- Added `is_rubric_in_use()` method to RubricService
- Efficient database query using SQLAlchemy's COUNT function
- Checks if any sessions reference the rubric before allowing deletion

**API Endpoint Update**
- Modified DELETE `/api/teacher/rubrics/{id}` endpoint
- Returns 409 Conflict when rubric is being used by sessions
- User-friendly error message explaining why deletion failed
- Suggests user action: "Please end or reassign those sessions first"

**Comprehensive Testing**
- 3 new unit tests for the `is_rubric_in_use()` method
- 3 new integration tests for cascade protection scenarios
- Fixed test isolation issues with unique session IDs using UUIDs
- All 29 rubric-related tests passing

**Key Achievement**: Data integrity is now protected - rubrics cannot be deleted if they're being used by any sessions, preventing orphaned references and maintaining database consistency.

### ✅ Phase 1.3 Part 7 Complete - Comprehensive Test Suite

#### What Was Accomplished in Part 7

**Comprehensive Test Script**
- Created `test_phase_1_3_complete.py` that tests all Phase 1.3 functionality
- Tests organized into logical groups:
  - Basic CRUD Operations
  - Validation Tests (weights, negative values, duplicates)
  - Teacher Isolation
  - Error Handling (404, 400, 422)
  - Edge Cases (empty criteria, long names, many criteria)
  - Complete Workflow (Create → Read → Update → Delete)
  - Cascade Protection

**Test Coverage**
- All CRUD endpoints tested with various scenarios
- Enhanced validation messages verified
- Teacher isolation confirmed (all rubrics tagged with teacher_id)
- Edge cases handled gracefully
- Error responses verified for user-friendliness

**Key Achievement**: Phase 1.3 is now complete with a production-ready evaluation rubric system that provides clear validation messages, prevents data integrity issues, and supports teacher-specific data isolation.

### ✅ Phase 1.3 Part 6 Complete - Enhanced Validation & Error Handling

#### What Was Accomplished in Part 6

**Enhanced Pydantic Model Validation**
- Added descriptive field descriptions for all fields for better API documentation
- Enhanced weight validation to show actual values:
  - Negative weight: "Criterion weight cannot be negative. You provided -0.5, but weights must be between 0.0 and 1.0"
  - Excessive weight: "Criterion weight cannot exceed 1.0. You provided 1.5, but the maximum allowed weight is 1.0"
- Enhanced weight sum validation:
  - Shows actual sum vs expected (1.0)
  - Lists current weights for each criterion
  - Provides clear guidance: "Criteria weights must sum to exactly 1.0, but your weights sum to 0.800. Current weights: {Communication: 0.3, Empathy: 0.5}. Please adjust the weights so they total 1.0 (100% of the evaluation)."

**Service Layer Enhancements**
- Added duplicate criterion name validation in both `create_rubric_for_teacher()` and `update()` methods
- Clear error message: "Each criterion must have a unique name. Found duplicate criterion names: communication. Please use distinct names for each evaluation criterion."
- Validation works for both create and update operations

**Comprehensive Error Testing**
- Created `scripts/test_rubric_error_handling.py` that tests:
  - 404 Not Found errors with resource IDs
  - 422 Validation errors with helpful messages
  - 400 Bad Request errors for invalid data
  - 409 Conflict errors (cascade protection)
  - 403 Forbidden errors (permission checks)
  - Edge cases (long names, floating point tolerance, many criteria)
- Created `test_rubric_validation.py` to demonstrate enhanced validation locally
- Created `test_rubric_api_validation.py` for API-based validation testing

**Error Message Improvements**
- Before: "Criteria weights must sum to 1.0, got 0.8"
- After: Full breakdown with current weights and guidance on fixing
- Before: "Weight must be between 0 and 1"
- After: Shows actual value provided and acceptable range
- Before: "ensure this value has at least 1 items"
- After: "List of specific behaviors or skills to evaluate (at least one required)"

**Key Achievement**: Error messages are now user-friendly and guide users on how to fix validation issues, improving the developer experience when using the API. All 29 rubric-related tests continue to pass.

### ✅ Phase 1.2 Complete - ClientProfile CRUD Implementation

#### Overview
Phase 1.2 has been successfully completed with a full CRUD API for ClientProfile including authentication, permissions, and comprehensive error handling. The implementation took approximately 3.25 hours (very close to the 3-4 hour estimate).

#### What Was Accomplished

**1. Service Layer** (`backend/services/client_service.py`)
- ClientService class extending BaseCRUD with full CRUD operations
- Teacher-specific filtering methods:
  - `get_teacher_clients()` - Filter clients by teacher
  - `create_client_for_teacher()` - Create with teacher assignment
  - `can_update()` and `can_delete()` - Permission checks
- Complete teacher isolation ensuring data security

**2. API Endpoints** (`backend/api/teacher_routes.py`)
- GET `/api/teacher/clients` - List all clients for authenticated teacher
- POST `/api/teacher/clients` - Create new client  
- GET `/api/teacher/clients/{id}` - Get specific client
- PUT `/api/teacher/clients/{id}` - Update client (partial updates supported)
- DELETE `/api/teacher/clients/{id}` - Delete client

**3. Authentication System**
- Dependency injection pattern with `get_current_teacher()`
- Mock authentication returning "teacher-123" for testing
- Ready for JWT/session-based auth integration
- All endpoints use consistent authentication pattern

**4. Error Handling**
- 404 Not Found - Clear messages with resource IDs
- 403 Forbidden - Permission denied for other teachers' clients
- 400 Bad Request - Invalid request data
- 422 Unprocessable Entity - FastAPI's built-in validation errors
- 500 Internal Server Error - Safe error messages without stack traces

**5. Comprehensive Testing**
- Unit tests for ClientService methods (`tests/unit/test_client_service.py`)
- Integration tests for all API endpoints
- Error handling test suite (`scripts/test_error_handling.py`)
- Authentication dependency tests (`scripts/test_auth_dependency.py`)
- End-to-end system test (`test_phase_1_2_complete.py`)

#### Key Design Decisions

**Security Through Layers**
- Authentication: Mock function ready for real implementation
- Authorization: Teachers can only access their own clients
- Validation: Pydantic models ensure data integrity
- Error Handling: Informative yet secure error messages

**Incremental Development Success**
Breaking Phase 1.2 into 6 small parts proved highly effective:
- Each part was testable in isolation
- Errors were caught early
- Progress was visible and measurable
- Code quality remained high throughout

**API Design Patterns**
- RESTful conventions followed consistently
- Dependency injection for database and auth
- Clear separation of concerns
- Comprehensive error responses

#### Implementation Timeline

| Part | Description | Estimated | Actual |
|------|-------------|-----------|--------|
| 1 | Basic Client Service | 30 min | 20 min ✅ |
| 2 | Teacher-Filtered Methods | 60 min | 45 min ✅ |
| 3 | API Router Setup | 30 min | 25 min ✅ |
| 4 | CRUD Endpoints | 90 min | 60 min ✅ |
| 5 | Authentication Placeholder | 30 min | 20 min ✅ |
| 6 | Error Handling | 30 min | 25 min ✅ |
| **Total** | **Phase 1.2 Complete** | **4 hours** | **3.25 hours** |

#### Lessons Learned

**What Worked Well**
1. Incremental Approach: Small, focused changes prevented overwhelming complexity
2. Test-First: Writing tests before/with code caught issues early
3. Clear Documentation: Each part documented immediately
4. Dependency Injection: Made testing and future changes easier

**Challenges Overcome**
1. Type Annotations: Fixed Dict[str, Any] import issue
2. Error Handling: Balanced security with helpfulness
3. Mock Authentication: Designed for easy replacement
4. Custom Validation Handler: Removed in favor of FastAPI's built-in handling

#### Production Readiness

The current implementation is production-ready with these considerations:
1. Replace mock authentication with real JWT/session handling
2. Add request logging and monitoring
3. Consider rate limiting for API endpoints
4. Add database connection pooling if needed
5. Implement proper error logging (not just user messages)

#### Code Quality Highlights

- **DRY Principle**: Reused BaseCRUD effectively
- **SOLID Principles**: Single responsibility, dependency inversion
- **Clean Code**: Clear naming, good documentation
- **Security First**: Permission checks on all operations
- **User Experience**: Helpful error messages

### ✅ Completed
- Project directory structure created
- FastAPI application skeleton with health check endpoints
- All four data models implemented (ClientProfile, EvaluationRubric, Session, Evaluation)
- SQLAlchemy ORM models and Pydantic schemas defined
- SQLite database schema created
- Configuration management system using environment variables
- Basic project setup and initialization scripts
- API documentation auto-generated at `/docs`
- CRUD implementation plan defined

### ✅ Completed - Phase 1 CRUD Operations
- **Phase 1.1: Database Foundation & Base Service** ✓
  - Database initialization script with verification and sample data option
  - Base database service with smart session management
  - Generic BaseCRUD class providing full CRUD operations
  - Comprehensive pytest infrastructure with 15 passing tests
  - Test fixtures for all models
  - PyCharm run configurations for common tasks
  - SQLAlchemy 2.0 compatibility (text() for raw SQL)
  - Smart SQL logging (auto-disabled during tests)
  - Test runner scripts for easy execution

- **Phase 1.2: ClientProfile CRUD** ✓ (~3.25 hours)
  - Full CRUD API for ClientProfile with authentication and permissions
  - Teacher-specific filtering and isolation
  - Comprehensive error handling (404, 403, 400, 422)
  - Mock authentication ready for JWT integration
  - Complete test coverage

- **Phase 1.3: EvaluationRubric CRUD** ✓ (~3 hours)
  - Full CRUD API for evaluation rubrics
  - Criteria weight validation with helpful error messages
  - Cascade protection preventing deletion of rubrics in use
  - Duplicate criterion name prevention
  - Enhanced validation messages showing actual values
  - Comprehensive test suite verifying all functionality

### 🔄 In Progress
- **Phase 1.4: Course Section Management** (Parts 1-5 Complete)
  - ✅ Part 1: Database Models and Schema (25 min)
    - Created CourseSectionDB and SectionEnrollmentDB models
    - All 15 unit tests passing
    - Database tables verified and working
  - ✅ Part 2: Basic Section Service (30 min)
    - Created SectionService with teacher-specific methods
    - Full unit test coverage (11 tests)
    - Permission system implemented
  - ✅ Part 3: Section CRUD Endpoints (45 min)
    - All 5 CRUD endpoints implemented
    - 18 integration tests passing
    - Full error handling and teacher isolation
  - ✅ Part 4: Enrollment Service Layer (45 min)
    - Created EnrollmentService with 5 core methods
    - Soft delete pattern for enrollment history
    - 20 unit tests with full coverage
    - Business rules enforced
  - ✅ Part 5: Enrollment Management Endpoints (45 min)
    - All 3 enrollment endpoints implemented
    - Teacher can view roster, enroll, and unenroll students
    - Fixed typo bug in unenroll endpoint
    - Manual tests all passing
  - Ready for Part 6: Student Section Access

### 📝 Key Documentation Files
- `README.md` - Main project documentation (includes Phase 1.2 complete details)
- `PYCHARM_SETUP.md` - PyCharm IDE configuration guide
- Various test scripts in root and `/scripts` directories

### 📋 Next Steps
1. **Begin Phase 1.4**: Course Section Management implementation
2. Create section and enrollment models
3. Implement teacher section management
4. Add student enrollment features
5. Build roster viewing capabilities
6. Prepare foundation for assignments

### 🚀 Quick Start for Next Session

**Start the API Server:**
```bash
# From project root
python -m uvicorn backend.app:app --reload
# Or use the helper script
python start_server.py
```

**Run Tests:**
```bash
# All tests
python test_quick.py

# Rubric service tests only
python -m pytest tests/unit/test_rubric_service.py -v

# Rubric API integration tests
python -m pytest tests/integration/test_rubric_api.py -v

# Client service tests only  
python -m pytest tests/unit/test_client_service.py -v

# Test all CRUD endpoints
python test_all_crud.py

# Test authentication dependency
python scripts/test_auth_dependency.py

# Test error handling
python scripts/test_error_handling.py

# Test rubric error handling
python scripts/test_rubric_error_handling.py

# Section API integration tests - ALL PASSING ✅
python -m pytest tests/integration/test_section_api.py -v

# Course section tests - ALL PASSING ✅
python -m pytest tests/unit/test_course_section.py -v

# Section service tests - ALL PASSING ✅
python -m pytest tests/unit/test_section_service.py -v

# Test course section models - WORKING ✅
python test_course_section_models.py

# Test section service - WORKING ✅
python test_section_service.py

# Test section endpoints - WORKING ✅
python test_section_endpoints.py

# Enrollment service tests - ALL PASSING ✅
python -m pytest tests/unit/test_enrollment_service.py -v

# Test enrollment service - WORKING ✅
python test_enrollment_service.py

# Quick enrollment unit tests
python test_enrollment_unit.py

# Test enrollment API endpoints - ALL WORKING ✅
python test_enrollment_endpoints.py

# Run enrollment integration tests
python test_enrollment_integration.py
```

**Check API Documentation:**
- Visit http://localhost:8000/docs when server is running
- Current endpoints (all using authentication dependency):
  - `/api/teacher/test` and `/api/teacher/test-db` (test endpoints)
  - `/api/teacher/clients` (GET, POST)
  - `/api/teacher/clients/{id}` (GET, PUT, DELETE)
  - `/api/teacher/rubrics` (GET, POST)
  - `/api/teacher/rubrics/{id}` (GET, PUT, DELETE)
  - `/api/teacher/sections` (GET, POST) ✅
  - `/api/teacher/sections/{id}` (GET, PUT, DELETE) ✅
  - `/api/teacher/sections/{id}/roster` (GET) ✅ NEW
  - `/api/teacher/sections/{id}/enroll` (POST) ✅ NEW
  - `/api/teacher/sections/{id}/enroll/{student_id}` (DELETE) ✅ NEW

## Development Environment Setup

### Prerequisites
- Python 3.9+
- Git
- SQLite
- API keys for chosen LLM service
- PyCharm IDE (recommended)

### Initial Setup Commands
```bash
# Clone repository
git clone [repository-url]
cd virtual_client

# View detailed setup instructions
python setup_instructions.py

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API keys
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
# Edit .env to add your OpenAI or Anthropic API key

# Initialize database
python -m backend.scripts.init_db

# Or initialize with sample data
python -m backend.scripts.init_db --sample-data

# Run tests to verify setup
python test_quick.py
# Or: python -m pytest tests/ -v

# Run development server
cd backend
python app.py
# Or use uvicorn directly from project root:
# uvicorn backend.app:app --reload
```

### Verify Setup
- API running at: http://localhost:8000
- API documentation at: http://localhost:8000/docs
- Database created at: database/app.db
- All tests passing: `python test_quick.py`

### PyCharm Setup
1. **Open Project**: File → Open → Select `virtual_client` folder
2. **Configure Interpreter**: 
   - File → Settings → Project → Python Interpreter
   - Select `.venv` from the project
3. **Run Configurations** (automatically loaded):
   - **Quick Test** - Fast test runner
   - **All Tests** - Complete test suite
   - **Database Tests** - Database-specific tests
   - **Initialize Database** - Create database
   - **Initialize Database with Sample Data** - Create with test data
   - **FastAPI Server** - Run the web server
4. **Database Tool**: View → Tool Windows → Database → Add SQLite data source

## API Endpoints Overview

### Teacher Endpoints
#### Client Management
- `POST /api/teacher/clients` - Create virtual client
- `GET /api/teacher/clients` - List teacher's clients
- `GET /api/teacher/clients/{id}` - Get client details
- `PUT /api/teacher/clients/{id}` - Update client
- `DELETE /api/teacher/clients/{id}` - Delete client

#### Rubric Management
- `POST /api/teacher/rubrics` - Create evaluation rubric
- `GET /api/teacher/rubrics` - List teacher's rubrics
- `GET /api/teacher/rubrics/{id}` - Get rubric details
- `PUT /api/teacher/rubrics/{id}` - Update rubric
- `DELETE /api/teacher/rubrics/{id}` - Delete rubric

#### Section Management (IMPLEMENTED - Phase 1.4 Part 3) ✅
- `POST /api/teacher/sections` - Create course section
- `GET /api/teacher/sections` - List teacher's sections
- `GET /api/teacher/sections/{id}` - Get section details
- `PUT /api/teacher/sections/{id}` - Update section
- `DELETE /api/teacher/sections/{id}` - Delete section

#### Enrollment Management (Future - Phase 1.4 Parts 4-5)
- `GET /api/teacher/sections/{id}/roster` - View enrolled students
- `POST /api/teacher/sections/{id}/enroll` - Enroll a student
- `DELETE /api/teacher/sections/{id}/enroll/{student_id}` - Unenroll student

#### Assignment Management (Future - Phase 1.5)
- `POST /api/teacher/sections/{id}/assignments` - Create assignment
- `GET /api/teacher/sections/{id}/assignments` - List assignments
- `GET /api/teacher/assignments/{id}` - Get assignment details
- `PUT /api/teacher/assignments/{id}` - Update assignment
- `DELETE /api/teacher/assignments/{id}` - Delete assignment
- `POST /api/teacher/assignments/{id}/clients` - Add client to assignment
- `DELETE /api/teacher/assignments/{id}/clients/{client_id}` - Remove client

#### Monitoring (Future - Phase 1.6)
- `GET /api/teacher/sessions` - View all student sessions
- `GET /api/teacher/sessions/{id}` - View session details
- `GET /api/teacher/evaluations` - View all evaluations

### Student Endpoints
#### Section Access (Future - Phase 1.4)
- `GET /api/student/sections` - List enrolled sections
- `GET /api/student/sections/{id}` - Get section details

#### Assignment Access (Future - Phase 1.5)
- `GET /api/student/assignments` - List assignments across all sections
- `GET /api/student/assignments/{id}` - Get assignment details

#### Session Management (Future - Phase 1.6)
- `GET /api/student/clients` - List available practice clients
- `POST /api/student/sessions/practice` - Start practice session
- `POST /api/student/sessions/assignment/{id}` - Start assignment session
- `GET /api/student/sessions` - List all sessions
- `GET /api/student/sessions/{id}` - Get session details
- `POST /api/student/sessions/{id}/messages` - Send message to client
- `POST /api/student/sessions/{id}/end` - End session

#### Evaluations (Future - Phase 1.7)
- `GET /api/student/evaluations` - List visible evaluations
- `GET /api/student/evaluations/{id}` - Get evaluation details

## Next Steps

1. **Confirm Technology Choices**: Finalize the tech stack based on team expertise
2. **Set Up Development Environment**: Configure local development setup in PyCharm
3. **Initialize Project Structure**: Create the directory structure outlined above
4. **Begin Phase 1**: Start with data models and basic API structure
5. **Secure API Access**: Obtain necessary API keys for LLM service
6. **Gather Requirements**: Collect sample rubrics and client scenarios from domain experts

## Development Guidelines

### Incremental Development Approach
This project follows an incremental development methodology:
- **Small, focused changes**: Implement one feature at a time
- **Test as you go**: Write tests for each component before moving on
- **Clear communication**: Confirm understanding before implementing
- **Code review**: Each phase should be reviewed before proceeding

### Before Writing Code
1. Confirm understanding of requirements
2. Explain the implementation approach
3. Get approval before proceeding
4. Keep changes minimal and focused

### Suggesting Improvements
1. List suggestions clearly with rationale
2. Explain benefits and trade-offs
3. Wait for approval before implementing
4. Document decisions in code comments

## Contributing

[Add contributing guidelines here once established]

## License

[Add license information here]

---

*This document should be updated as the project evolves and new decisions are made.*