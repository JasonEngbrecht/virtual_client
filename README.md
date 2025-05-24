# Virtual Client - Social Work Training App

**Status:** In Development | **Phase:** 1 - Foundation

This project will create a virtual client that social work (and other areas) can interface with to practice working with clients.

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
│   │   ├── llm_service.py     # LLM API integration
│   │   ├── evaluation_service.py  # Rubric-based evaluation
│   │   └── storage_service.py # Database operations
│   ├── prompts/
│   │   └── client_prompts.py  # LLM prompt templates
│   └── api/
│       ├── teacher_routes.py  # Teacher endpoints
│       └── student_routes.py  # Student endpoints
├── frontend/
│   ├── teacher_dashboard.py   # Teacher interface
│   └── student_interface.py   # Student chat interface
├── database/
│   ├── schema.sql            # Database schema
│   └── app.db               # SQLite database file
├── tests/
│   └── test_*.py            # Unit tests
├── requirements.txt
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

### Phase 1: Foundation (Week 1)
- [x] Set up project structure
- [x] Configure FastAPI application
- [x] Design and implement data models
- [x] Set up SQLite database with schema
- [ ] Create basic CRUD operations
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

### 🚧 In Progress
- Phase 1: Basic CRUD operations for models

### 📋 Next Steps
- Implement CRUD endpoints for teacher operations
- Create database service layer
- Begin LLM integration (Phase 2)

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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env to add your OpenAI or Anthropic API key

# Initialize database
python -m backend.scripts.init_db

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

## API Endpoints Overview

### Teacher Endpoints
- `POST /api/teacher/clients` - Create virtual client
- `GET /api/teacher/clients` - List all clients
- `PUT /api/teacher/clients/{id}` - Update client
- `DELETE /api/teacher/clients/{id}` - Delete client
- `POST /api/teacher/rubrics` - Create/upload rubric
- `GET /api/teacher/rubrics` - List rubrics
- `GET /api/teacher/sessions` - View all student sessions
- `GET /api/teacher/evaluations` - View evaluation results

### Student Endpoints
- `GET /api/student/clients` - List available clients
- `POST /api/student/sessions` - Start new session
- `POST /api/student/sessions/{id}/messages` - Send message
- `GET /api/student/sessions/{id}` - Get session details
- `POST /api/student/sessions/{id}/end` - End session
- `GET /api/student/evaluations/{id}` - Get evaluation feedback

## Next Steps

1. **Confirm Technology Choices**: Finalize the tech stack based on team expertise
2. **Set Up Development Environment**: Configure local development setup in PyCharm
3. **Initialize Project Structure**: Create the directory structure outlined above
4. **Begin Phase 1**: Start with data models and basic API structure
5. **Secure API Access**: Obtain necessary API keys for LLM service
6. **Gather Requirements**: Collect sample rubrics and client scenarios from domain experts

## Contributing

[Add contributing guidelines here once established]

## License

[Add license information here]

---

*This document should be updated as the project evolves and new decisions are made.*