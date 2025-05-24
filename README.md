# Virtual Client - Social Work Training App

**Status:** In Development | **Phase:** 1.2 - ClientProfile CRUD | **Progress:** Database Foundation Complete ✅

This project will create a virtual client that social work (and other areas) can interface with to practice working with clients.

## 🌟 Latest Achievement
**Phase 1.1 Complete!** - Database foundation is fully implemented with:
- ✅ Database initialization scripts
- ✅ Generic CRUD operations 
- ✅ 15 passing tests
- ✅ PyCharm run configurations
- ✅ SQLAlchemy 2.0 compatibility

**Next:** Phase 1.2 - Implementing ClientProfile CRUD operations

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

### Session
```python
{
    "id": "uuid",
    "student_id": "string",
    "client_profile_id": "uuid",
    "rubric_id": "uuid",
    "messages": [
        {
            "role": "student|client",
            "content": "text",
            "timestamp": "datetime"
        }
    ],
    "started_at": "timestamp",
    "ended_at": "timestamp",
    "evaluation_result": "evaluation_id"
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
- [ ] **Phase 1.2: ClientProfile CRUD** (Next)
  - [ ] Storage service for client operations
  - [ ] Teacher API routes (Create, Read, Update, Delete)
  - [ ] Unit and integration tests
- [ ] Phase 1.3: EvaluationRubric CRUD
  - [ ] Storage service with criteria validation
  - [ ] Teacher API routes for rubric management
  - [ ] Cascade protection testing
- [ ] Phase 1.4: Session Management
  - [ ] Session service (Create, Read, Update messages, End)
  - [ ] Student and teacher API routes
  - [ ] Session state management tests
- [ ] Phase 1.5: Evaluation System
  - [ ] Evaluation service (Create from session, Read)
  - [ ] Scoring algorithm implementation
  - [ ] Student and teacher retrieval routes
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
- Phase 1.1 (Database Foundation): 2-3 hours
- Phase 1.2 (ClientProfile CRUD): 3-4 hours
- Phase 1.3 (EvaluationRubric CRUD): 2-3 hours
- Phase 1.4 (Session Management): 4-5 hours
- Phase 1.5 (Evaluation System): 3-4 hours
- **Total Estimated Time**: 14-19 hours

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

## Current Project Status

**Last Updated:** May 23, 2025

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

### 🚧 Ready to Start
- **Phase 1.2**: ClientProfile CRUD
  - Client service layer with business logic
  - Teacher API routes for client management
  - Permission-based access control
  - Comprehensive unit and integration tests

### 📋 Next Steps
1. **Begin Phase 1.2**: ClientProfile CRUD implementation
2. Create client service layer (`backend/services/client_service.py`)
3. Implement teacher routes (`backend/api/teacher_routes.py`)
4. Add authentication/authorization helpers
5. Write comprehensive tests for new components
6. Update API documentation

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

#### Monitoring
- `GET /api/teacher/sessions` - View all student sessions
- `GET /api/teacher/sessions/{id}` - View session details
- `GET /api/teacher/evaluations` - View all evaluations

### Student Endpoints
#### Session Management
- `GET /api/student/clients` - List available clients
- `POST /api/student/sessions` - Start new session
- `GET /api/student/sessions` - List own sessions
- `GET /api/student/sessions/{id}` - Get session details
- `POST /api/student/sessions/{id}/messages` - Send message to client
- `POST /api/student/sessions/{id}/end` - End session

#### Evaluations
- `GET /api/student/evaluations` - List own evaluations
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