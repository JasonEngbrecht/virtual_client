# Virtual Client - Social Work Training App

An AI-powered training platform for social work students to practice client interactions.

## 🚀 Quick Start for Developers

### Start Here:
1. **[`CURRENT_SPRINT.md`](CURRENT_SPRINT.md)** - ⚡ Your immediate task
2. **[`PATTERNS.md`](PATTERNS.md)** - 🔧 How we build things
3. **[`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md)** - 🗺️ Where we're going

### Current Focus
**MVP Phase Week 1** - Building Minimum Viable Conversation
- Simplified session tracking
- Anthropic integration  
- Streamlit prototype
- Real user testing

See [`CURRENT_SPRINT.md`](CURRENT_SPRINT.md) for daily tasks.

## 📁 Project Structure
```
virtual_client/
├── backend/           # FastAPI application
├── tests/            # Test suites
├── docs/             # Extended documentation
├── CURRENT_SPRINT.md # What to do now
├── PATTERNS.md       # How to do it
├── PROJECT_ROADMAP.md # Why we're doing it
└── README.md         # You are here
```

## 🛠️ Setup & Commands

### Initial Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.scripts.init_db
```

### Daily Commands
```bash
python start_server.py    # Start API server
python run_tests.py       # Run all tests
python test_quick.py      # Quick test run
```

### API Documentation
http://localhost:8000/docs (when server running)

## 📚 Documentation Map

### For Current Work
- [`CURRENT_SPRINT.md`](CURRENT_SPRINT.md) - Immediate tasks
- [`PATTERNS.md`](PATTERNS.md) - Code patterns
- [`docs/architecture/`](docs/architecture/) - Technical details

### For Project Context
- [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) - Full vision & phases
- [`docs/architecture/DATA_MODELS.md`](docs/architecture/DATA_MODELS.md) - All data models
- [`docs/completed/`](docs/completed/) - Past work
- [`docs/decisions/`](docs/decisions/) - Design choices

### Other Important Files
- [`NEXT_CHAT_PROMPT.md`](NEXT_CHAT_PROMPT.md) - New session setup
- [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md) - Doc maintenance
- [`.claude-ignore.md`](.claude-ignore.md) - What to skip

## 🤝 Development Workflow
1. Read `CURRENT_SPRINT.md`
2. Check `PATTERNS.md` for implementation guidance
3. Reference `PROJECT_ROADMAP.md` for context
4. Code incrementally with tests
5. Update docs as you go

## 🔧 Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite (demo) / PostgreSQL (production)
- **Testing**: pytest
- **Future**: OpenAI/Anthropic integration

## 🎯 Project Goals
Build a training application where:
- **Teachers** create virtual clients and evaluation rubrics
- **Students** practice conversations with AI-powered clients  
- **System** provides automated feedback based on rubrics

---

**Prerequisites**: Python 3.12, PyCharm IDE (recommended), Git

For setup instructions, architecture details, and API documentation, see [`docs/`](docs/)