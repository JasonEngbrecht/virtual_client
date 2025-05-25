# Virtual Client - Development Environment

## 🖥️ System Information
- **OS**: Windows
- **IDE**: PyCharm Professional
- **Python**: 3.12
- **Virtual Environment**: `.venv` in project root
- **Project Path**: `C:\Users\engbrech\Python\virtual_client`

## 🛠️ PyCharm Configuration
- Python interpreter configured to `.venv`
- Run configurations loaded from `.idea/runConfigurations/`
- Database tool configured for SQLite at `database\app.db`
- Test runner configured for pytest

### PyCharm Run Configurations Available:
- **Quick Test** - Fast test runner
- **All Tests** - Complete test suite
- **Database Tests** - Database-specific tests
- **Initialize Database** - Create database
- **Initialize Database with Sample Data** - Create with test data
- **FastAPI Server** - Run the web server

## 📁 File System Notes
- Use backslashes for Windows paths: `C:\Users\engbrech\Python\virtual_client`
- SQLite database at: `database\app.db`
- Virtual environment activation: `.venv\Scripts\activate` (Windows)
- Test database uses in-memory SQLite (no file)

## 🔧 Common Commands (Windows)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Start server
python start_server.py

# Run all tests
python run_tests.py

# Quick test run
python test_quick.py

# Specific test file
python -m pytest tests/unit/test_enrollment_service.py -v

# Initialize database
python -m backend.scripts.init_db

# With sample data
python -m backend.scripts.init_db --sample-data
```

## 🧪 Testing Strategy

### Test Organization
```
tests/
├── conftest.py          # Shared fixtures
├── unit/               # Fast, isolated tests
│   ├── test_client_service.py
│   ├── test_rubric_service.py
│   ├── test_section_service.py
│   └── test_enrollment_service.py
└── integration/        # API endpoint tests
    ├── test_teacher_api.py
    ├── test_rubric_api.py
    ├── test_section_api.py
    ├── test_enrollment_api.py
    └── test_student_section_api.py  # Current focus
```

### Testing Commands by Speed

#### 1. Unit Tests (Fast - Run Often)
```bash
# All unit tests
python -m pytest tests/unit/ -v

# Specific service
python -m pytest tests/unit/test_enrollment_service.py -v
```

#### 2. Integration Tests (Slower - Run After Implementation)
```bash
# All integration tests
python -m pytest tests/integration/ -v

# Specific endpoint group
python -m pytest tests/integration/test_student_section_api.py -v
```

#### 3. Quick Smoke Test
```bash
# Runs subset of critical tests
python test_quick.py
```

#### 4. Full Test Suite
```bash
# Runs everything
python run_tests.py
```

## 📋 Testing Checklist for Each Phase Part

1. **Before Starting**:
   - Run `python test_quick.py` to ensure clean state
   - Check for any failing tests from previous session

2. **During Development**:
   - Write unit tests for new service methods
   - Write integration tests for new endpoints
   - Run tests frequently during development

3. **After Implementation**:
   - Run new tests for current implementation
   - Run service tests for modified services
   - Run API tests for modified endpoints
   - Run `test_quick.py` for general regression
   - Run `python run_tests.py` for full validation

4. **Before Ending Session**:
   - Document any failing tests in CURRENT_SPRINT.md
   - Note which tests are critical for next session

## 🌐 API Development

### Server Commands
```bash
# Development server with auto-reload
python start_server.py

# Direct uvicorn (more control)
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Automatic docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

### Testing API Manually
```bash
# Using curl (Git Bash or WSL on Windows)
curl http://localhost:8000/api/teacher/test

# Using httpie (if installed)
http GET localhost:8000/api/teacher/test

# Or use:
# - Postman
# - PyCharm HTTP Client
# - Browser (for GET requests)
```

## 🐛 Debugging in PyCharm

### Setting Breakpoints
1. Click in the gutter next to line numbers
2. Right-click for conditional breakpoints
3. Use Debug mode (Shift+F9) instead of Run (Shift+F10)

### Debug Configurations
- Use "FastAPI Server" configuration for API debugging
- Use "pytest" configurations for test debugging
- Set PYTHONDONTWRITEBYTECODE=1 to avoid .pyc files

### Common Issues
- **Import errors**: Check Python interpreter is set to `.venv`
- **Database locked**: Stop all running servers/tests
- **Port already in use**: Kill process on port 8000

## 📦 Dependency Management

### Install new packages
```bash
# Activate venv first!
.venv\Scripts\activate

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Current Key Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **pytest**: Testing framework
- **httpx**: Test client for FastAPI

---

*This environment guide ensures consistent development setup across sessions.*