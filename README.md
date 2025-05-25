# Virtual Client - Social Work Training App

An educational application designed to help social work students practice client interactions through AI-powered simulations.

## 📍 Navigation Guide for Development

**Start here every time:**
1. **[`CURRENT_SPRINT.md`](CURRENT_SPRINT.md)** - ⚡ Your immediate task (read this FIRST)
2. **[`PATTERNS.md`](PATTERNS.md)** - 🔧 Implementation patterns (check if needed)
3. **[`docs/`](docs/)** - 📚 Detailed docs (only if referenced in CURRENT_SPRINT)

**Other important files:**
- [`NEXT_CHAT_PROMPT.md`](NEXT_CHAT_PROMPT.md) - For starting new chat sessions
- [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md) - How to maintain docs
- [`.claude-ignore.md`](.claude-ignore.md) - What to skip during development

## 📊 Current Status

**Active Development**: Phase 1.4 Part 6 - Student Section Access  
**See**: [`CURRENT_SPRINT.md`](CURRENT_SPRINT.md) for immediate tasks

### Progress Overview
- ✅ Phase 1.1: Database Foundation
- ✅ Phase 1.2: ClientProfile CRUD
- ✅ Phase 1.3: EvaluationRubric CRUD  
- 🔄 Phase 1.4: Course Section Management (Parts 1-5 complete)
- ⏳ Phase 1.5-1.7: Coming soon

## 🗂️ Documentation Structure

This project uses a focused documentation approach to improve development efficiency:

### For Current Work
- **[`CURRENT_SPRINT.md`](CURRENT_SPRINT.md)** - What to work on right now
- **[`PATTERNS.md`](PATTERNS.md)** - Quick reference for established patterns

### For Architecture Reference
- **[`docs/architecture/`](docs/architecture/)** - Technical documentation
  - [`services.md`](docs/architecture/services.md) - Service layer patterns
  - [`error-handling.md`](docs/architecture/error-handling.md) - Error response standards
  - [`authentication.md`](docs/architecture/authentication.md) - Auth patterns

### For Historical Context
- **[`docs/completed/`](docs/completed/)** - Completed phase documentation
  - [`phase-1-2-client-crud.md`](docs/completed/phase-1-2-client-crud.md)
  - [`phase-1-3-rubric-crud.md`](docs/completed/phase-1-3-rubric-crud.md)
  - [`phase-1-4-section-management.md`](docs/completed/phase-1-4-section-management.md)

### For Design Decisions
- **[`docs/decisions/`](docs/decisions/)** - Architecture decision records
  - [`why-soft-delete.md`](docs/decisions/why-soft-delete.md)

## 🚀 Quick Start

### Prerequisites
- Python 3.12
- PyCharm IDE (recommended)
- Git

### Setup
```bash
# Clone repository
git clone [repository-url]
cd virtual_client

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m backend.scripts.init_db

# Run server
python start_server.py
```

### Development Commands
```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/unit/test_enrollment_service.py -v

# Quick test run
python test_quick.py
```

### API Documentation
When server is running: http://localhost:8000/docs

## 🏗️ Project Structure

```
virtual_client/
├── backend/
│   ├── api/           # API routes
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── scripts/       # Utility scripts
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # API tests
├── docs/              # Extended documentation
├── CURRENT_SPRINT.md  # Active work
├── PATTERNS.md        # Quick reference
└── README.md          # This file
```

## 🎯 Project Goals

Build a training application where:
- **Teachers** create virtual clients and evaluation rubrics
- **Students** practice conversations with AI-powered clients
- **System** provides automated feedback based on rubrics

## 🔧 Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Testing**: pytest
- **Future**: OpenAI/Anthropic integration

## 📋 Development Workflow

1. Check [`CURRENT_SPRINT.md`](CURRENT_SPRINT.md) for current tasks
2. Reference [`PATTERNS.md`](PATTERNS.md) for established patterns
3. Look up specific patterns in [`docs/architecture/`](docs/architecture/) as needed
4. Review completed work in [`docs/completed/`](docs/completed/) for context
5. Run tests frequently during development

## 🤝 Contributing Guidelines

- Work incrementally with small, focused changes
- Write tests for new functionality
- Follow established patterns (see [`PATTERNS.md`](PATTERNS.md))
- Update documentation as you go
- Ask for clarification rather than making assumptions

## 📝 Key Project Decisions

- **Soft Delete**: Enrollments use soft delete to preserve history
- **Mock Auth**: Using hardcoded IDs during development
- **Service Pattern**: All services inherit from BaseCRUD
- **Error Standards**: Consistent error responses across endpoints

For more details on decisions, see [`docs/decisions/`](docs/decisions/).

---

**For detailed project history and future roadmap**, see the documentation in [`docs/`](docs/).