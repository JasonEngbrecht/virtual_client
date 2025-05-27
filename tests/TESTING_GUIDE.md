# Testing Guide for Virtual Client

## 🚀 MVP Testing Strategy

**For MVP/Prototype Phase (Current):**
- Focus on manual testing for Streamlit interfaces
- Write minimal automated tests (1-2 per feature)
- Test only critical paths: DB connection, API auth, cost calculations
- Skip edge cases, UI tests, and comprehensive coverage
- Document issues for later rather than fixing all edge cases

**After MVP Validation:**
- Return to comprehensive testing patterns below
- Add edge case handling
- Implement full test coverage

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Available Fixtures](#available-fixtures)
6. [Test Patterns](#test-patterns)
7. [Common Issues](#common-issues)
8. [Debugging Tests](#debugging-tests)

## Quick Start

All tests should pass with the following commands:

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/unit/test_database.py -v

# Run specific test
python -m pytest tests/unit/test_database.py::TestDatabaseService::test_database_service_initialization -v

# Run tests with coverage
python run_tests.py --cov=backend --cov-report=term-missing
```

**Current Test Status** (as of Day 3 Part 3):
- ✅ Unit tests: 235+ passing
- ✅ Integration tests: 234+ passing
- ✅ Total tests: 469 passing
- ✅ Recent additions: 13 tests for conversation service

## Test Organization

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── TESTING_GUIDE.md                 # This file
├── TEST_FIXES.md                    # Historical fixes reference
├── unit/                            # Unit tests (isolated components)
│   ├── test_client_service.py       # Client profile service tests
│   ├── test_course_section.py       # Course section model tests
│   ├── test_database.py             # Database and CRUD tests
│   ├── test_enrollment_service.py   # Enrollment service tests
│   ├── test_rubric_service.py       # Rubric service tests
│   └── test_section_service.py      # Section service tests
└── integration/                     # Integration tests (API endpoints)
    ├── conftest.py                  # Integration-specific fixtures
    ├── test_client_api.py           # Client CRUD endpoints
    ├── test_enrollment_api.py       # Enrollment endpoints
    ├── test_rubric_api.py           # Rubric endpoints
    ├── test_section_api.py          # Section endpoints
    ├── test_section_stats_api.py    # Section statistics endpoints
    └── test_student_section_api.py  # Student-specific endpoints
```

## Running Tests

### Using PyCharm Run Configurations
The project includes pre-configured run configurations:
- **All Tests** - Runs all tests in the project
- **Database Tests** - Runs only database-related tests
- **Initialize Database** - Creates the database
- **Initialize Database with Sample Data** - Creates database with test data

### Using PyCharm UI
1. **Run all tests**: Right-click on `tests` folder → Run 'pytest in tests'
2. **Run specific test file**: Click green arrow next to test class/function
3. **Run with coverage**: Right-click → Run 'pytest in tests' with Coverage

### Using Terminal
```bash
# Run all tests
python run_tests.py

# Run specific test suite
python -m pytest tests/integration/test_enrollment_api.py -v

# Run with markers
python -m pytest -m "not slow" -v

# Run with coverage
python run_tests.py --cov=backend --cov-report=html

# Run tests in parallel (if pytest-xdist is installed)
python -m pytest -n auto
```

### Useful Test Commands
```bash
# Show available fixtures
python -m pytest --fixtures

# Run failed tests from last run
python -m pytest --lf

# Run tests that match a pattern
python -m pytest -k "test_enroll"

# Show test durations
python -m pytest --durations=10
```

## Writing Tests

### Test Structure

#### Unit Tests
Unit tests should test individual components in isolation using mocks:

```python
"""
Unit tests for [Component Name]
"""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.some_service import SomeService

class TestSomeService:
    """Test cases for SomeService class"""
    
    def test_service_method(self):
        """Test that service method works correctly"""
        # Arrange
        service = SomeService()
        mock_db = MagicMock()
        
        # Act
        result = service.method(mock_db, param1, param2)
        
        # Assert
        assert result.field == expected_value
```

#### Integration Tests
Integration tests should test API endpoints with real database:

```python
"""
Integration tests for [Feature] API endpoints
"""
import pytest
from fastapi.testclient import TestClient

class TestFeatureAPI:
    """Test [feature] endpoints"""
    
    def test_endpoint_success(self, client, mock_teacher_auth, db_session):
        """Test successful API call"""
        # Arrange
        data = {"field": "value"}
        
        # Act
        response = client.post("/api/endpoint", json=data)
        
        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["field"] == "value"
```

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestSectionService`)
- Test methods: `test_*` (e.g., `test_create_section_success`)
- Use descriptive names that explain what is being tested

### Test Documentation
- Each test module should have a docstring explaining what it tests
- Each test class should have a docstring describing the component being tested
- Each test method should have a docstring explaining the specific scenario

## Available Fixtures

### Global Fixtures (tests/conftest.py)

#### Database Fixtures
- `db_session` - Fresh database session for each test
- `event_loop` - Async event loop for async tests

#### Sample Data Fixtures
- `sample_teacher_id` - Returns "teacher-123"
- `sample_student_id` - Returns "test-student-456"
- `sample_client_profile` - Creates a ClientProfileDB instance
- `sample_rubric` - Creates an EvaluationRubricDB instance
- `sample_session` - Creates a SessionDB instance
- `mock_llm_response` - Mock LLM response for testing

### Integration Fixtures (tests/integration/conftest.py)

#### Client and Auth Fixtures
- `client` - FastAPI test client with database override
- `mock_teacher_auth` - Mocks teacher authentication (teacher-123)

#### Test Data Fixtures
- `test_section` - Creates a course section for teacher-123
- `test_section_other_teacher` - Creates a section for another teacher
- `test_enrollment` - Creates an active enrollment
- `test_inactive_enrollment` - Creates an inactive enrollment

## Test Patterns

### 1. Database Test Pattern
Tests use an in-memory SQLite database that is created fresh for each test:

```python
def test_with_database(self, db_session):
    """Test that uses database"""
    # Database is fresh and empty
    # All models are available
    # Changes are isolated to this test
```

### 2. API Test Pattern
Integration tests use the FastAPI test client:

```python
def test_api_endpoint(self, client, mock_teacher_auth):
    """Test API endpoint"""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    data = response.json()
    # Validate response data
```

### 3. Error Testing Pattern
Test both success and error cases:

```python
def test_not_found(self, client, mock_teacher_auth):
    """Test 404 response"""
    response = client.get("/api/resource/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_forbidden(self, client, mock_teacher_auth, test_section_other_teacher):
    """Test 403 response"""
    response = client.get(f"/api/sections/{test_section_other_teacher.id}")
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
```

### 4. Mock Pattern for Unit Tests
Use mocks to isolate unit tests:

```python
def test_service_method(self):
    """Test service method with mocks"""
    service = MyService()
    mock_db = MagicMock(spec=Session)
    
    with patch.object(service, 'get', return_value=mock_object):
        result = service.method(mock_db, param)
        assert result == expected
```

### 5. Service Mocking Pattern
When mocking services imported by other services:

```python
# Mock services that are imported as instances
def test_with_service_mocks(monkeypatch):
    mock_client_service = Mock()
    mock_client_service.get.return_value = mock_client
    
    # Apply to the imported instance, not the module
    monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
```

**Special case for Anthropic service** (factory function):
```python
# Anthropic service uses factory pattern
mock_anthropic_instance = Mock()
mock_anthropic_instance.generate_response.return_value = "AI response"
mock_anthropic_service = Mock(return_value=mock_anthropic_instance)

monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
```

### 6. Pydantic Model Validation in Tests
When mocking database objects that will be validated by Pydantic:

```python
from datetime import datetime

# Include ALL required fields for Pydantic validation
mock_session_db = Mock(
    id="session-456",
    student_id="student-123",
    client_profile_id="client-123",
    status="active",
    total_tokens=25,
    estimated_cost=0.0001,
    session_notes=None,      # Include nullable fields
    started_at=datetime.utcnow(),  # Include datetime fields
    ended_at=None
)

# This can now be safely validated
Session.model_validate(mock_session_db)  # Won't raise ValidationError
```

### 7. Mocking SQLAlchemy db.refresh()
When testing with Mock objects that might be passed to `db.refresh()`:

```python
# SQLAlchemy's refresh() introspects objects, which fails on Mock
# Solution: Mock db.refresh to handle Mock objects gracefully

def mock_refresh(obj):
    # Do nothing for mock objects
    if isinstance(obj, Mock):
        return
    # Call original for real objects
    return original_refresh(obj)

monkeypatch.setattr(db_session, "refresh", mock_refresh)
```

### 8. Lambda Function User ID Extraction
When using decorators that extract user IDs from function arguments:

```python
# ❌ WRONG - Assumes keyword argument
get_user_id=lambda *args, **kwargs: kwargs.get('student').student_id

# ✅ CORRECT - Handle positional arguments
get_user_id=lambda *args, **kwargs: args[1].student_id if len(args) > 1 else None

# For functions with signature: func(db, student, ...)
# args[0] = db
# args[1] = student (what we want)
```

### 9. Mocking Anthropic Exceptions
Anthropic SDK exceptions require specific parameters. Use helper functions:

```python
import httpx

# Helper functions for creating Anthropic exceptions
def create_api_connection_error():
    """Create an APIConnectionError for testing"""
    return anthropic.APIConnectionError(
        request=httpx.Request("POST", "https://api.anthropic.com")
    )

def create_authentication_error(message="Invalid API key"):
    """Create an AuthenticationError for testing"""
    response = httpx.Response(
        401,
        json={"error": {"message": message, "type": "authentication_error"}},
        request=httpx.Request("POST", "https://api.anthropic.com")
    )
    return anthropic.AuthenticationError(
        response=response, 
        body={"error": {"message": message}}
    )

# Usage in tests
mock_client.messages.create.side_effect = create_authentication_error()
```

**Note**: The `httpx` library is required for creating these exceptions properly.

### 10. Testing Error Categorization
When testing error handling, use class name checking for compatibility:

```python
def _categorize_error(self, error: Exception) -> ErrorType:
    """Categorize by class name for better compatibility"""
    error_class_name = error.__class__.__name__
    
    if "AuthenticationError" in error_class_name:
        return ErrorType.AUTHENTICATION
    # ... more checks
```

This approach is more robust than `isinstance()` checks when dealing with mocked exceptions.

### 11. Mock Message Sequence Numbers
When mocking messages that need sequence numbers:

```python
# Track sequence numbers per session
message_sequences = {}

def mock_add_message(db, session_id, message_data):
    if session_id not in message_sequences:
        message_sequences[session_id] = 0
    message_sequences[session_id] += 1
    
    return Mock(
        id=f"msg-{message_sequences[session_id]}",
        session_id=session_id,
        sequence_number=message_sequences[session_id],  # Integer, not Mock
        # ... other fields
    )
```

## Common Issues

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'backend'`
**Solution**: 
- Ensure virtual environment is activated
- Check that backend is in Python path (handled by conftest.py)
- Verify PyCharm is using the correct interpreter

### MVP Module Import Errors
**Problem**: `ModuleNotFoundError: No module named 'utils'` when testing MVP modules
**Solution**:
- MVP modules need proper sys.path setup before imports:
```python
# In mvp/teacher_test.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Now import from mvp.utils
from mvp.utils import (
    setup_page_config,
    get_database_connection,
    # ...
)
```
- Use full module paths (`mvp.utils` not just `utils`)
- Ensure sys.path manipulation happens BEFORE other imports

### Database Not Found
**Problem**: Tables not created or "no such table" errors
**Solution**:
- Models must be imported before `Base.metadata.create_all()`
- Check that all models inherit from `Base`
- Verify model imports in conftest.py
- If using legacy `init_db.py`, ensure `database/schema.sql` exists

### Schema File Missing
**Problem**: `FileNotFoundError: Schema file not found: database/schema.sql`
**Solution**:
- Some legacy tests still use `init_db.py` which requires schema.sql
- Either keep schema.sql file or migrate tests to use ORM-based initialization
- Use `backend/scripts/init_db_orm.py` instead of `init_db.py` for new tests

### Fixture Not Found
**Problem**: `fixture 'fixture_name' not found`
**Solution**:
- Check fixture is defined in appropriate conftest.py
- Ensure conftest.py is in the test directory
- Use `pytest --fixtures` to list available fixtures

### Test Isolation Issues
**Problem**: Tests fail when run together but pass individually
**Solution**:
- Each test should use fresh database (handled by db_session fixture)
- Don't rely on test execution order
- Clean up any global state changes

### Integration Tests Hanging
**Problem**: Integration tests hang or timeout when functions create their own database connections
**Solution**:
- This often happens when tested functions use `get_database_connection()` internally
- SQLite can have locking issues with multiple connections
- Solutions:
  1. Add timeout markers to prevent indefinite hanging:
  ```python
  @pytest.mark.timeout(5)  # 5 second timeout
  def test_that_might_hang(self):
      # test code
  ```
  2. Mock the database connection in the tested function
  3. Refactor functions to accept database sessions as parameters
  4. Use the same database session throughout the test
- Example from teacher history tests:
  ```python
  # fetch_conversation_history creates its own db connection
  # This can cause SQLite locking in tests
  def fetch_conversation_history(teacher_id: str):
      db = get_database_connection()  # Creates new connection
      # ... query logic
      db.close()
  ```

### Async Test Issues
**Problem**: Warnings about async fixture scope
**Solution**: Already configured in pytest.ini:
```ini
asyncio_default_fixture_loop_scope = function
```

### Foreign Key Constraint Errors
**Problem**: `NOT NULL constraint failed` or `FOREIGN KEY constraint failed`
**Solution**:
- Commit parent objects before using their IDs:
  ```python
  section = CourseSectionDB(...)
  db_session.add(section)
  db_session.commit()  # Commit to get ID
  
  assignment = AssignmentDB(section_id=section.id, ...)
  ```
- Ensure all required foreign key relationships are satisfied

### Empty JSON Field Validation Errors
**Problem**: Model validation fails for empty JSON arrays (e.g., rubric criteria)
**Solution**:
- Provide valid data that meets model requirements:
  ```python
  # Don't use empty criteria array
  rubric = EvaluationRubricDB(
      criteria=[{  # At least one criterion required
          "name": "Test",
          "weight": 1.0,
          "evaluation_points": ["Point"],
          # ... other required fields
      }]
  )
  ```

### Floating-Point Precision Errors
**Problem**: Tests fail due to floating-point precision issues (e.g., `0.0006000000000000001 != 0.0006`)
**Solution**:
- Use `pytest.approx()` for floating-point comparisons:
  ```python
  # ❌ WRONG - Can fail due to precision
  assert total_cost == 0.0006
  
  # ✅ CORRECT - Handles floating-point precision
  assert total_cost == pytest.approx(0.0006)
  
  # With custom tolerance
  assert value == pytest.approx(expected, rel=1e-6)  # Relative tolerance
  assert value == pytest.approx(expected, abs=1e-6)  # Absolute tolerance
  ```
- Common in cost calculations, percentages, and any math operations
- Also affects formatted output tests - consider how values are rounded

## Debugging Tests

### PyCharm Debugging
1. Set breakpoints by clicking in the gutter
2. Right-click test → Debug 'pytest...'
3. Use debugger panel to inspect variables
4. Step through code with F7/F8

### Print Debugging
```python
def test_something(self, capsys):
    """Test with print debugging"""
    print("Debug info:", variable)
    # Test code
    captured = capsys.readouterr()
    # Can also assert on printed output
```

### Database Debugging
```python
def test_database_state(self, db_session):
    """Test with SQL debugging"""
    # Enable SQL echo temporarily
    db_session.bind.echo = True
    
    # Your test code
    
    # Check database state
    result = db_session.execute(text("SELECT * FROM table"))
    print(result.fetchall())
```

### Diagnostic Tools
If tests are failing mysteriously, use diagnostic scripts:

```bash
# Run comprehensive diagnostics
python DIAGNOSE_TESTS.py

# Check test infrastructure
python test_infrastructure_final.py
```

## Test Coverage

### Viewing Coverage
After running tests with coverage:
1. **Terminal**: See summary in console output
2. **HTML Report**: Open `htmlcov/index.html` in browser
3. **PyCharm**: View → Tool Windows → Coverage

### Coverage Goals
- Aim for >80% coverage overall
- Critical paths should have 100% coverage
- Don't test:
  - Simple getters/setters
  - Framework code
  - External API calls (mock them instead)

### Improving Coverage
1. Run coverage report: `python run_tests.py --cov=backend --cov-report=term-missing`
2. Look for files with low coverage
3. Add tests for uncovered lines
4. Focus on business logic and error cases

## Best Practices

1. **Test Independence**: Each test should be able to run in isolation
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **One Assertion Per Test**: Keep tests focused (multiple related assertions are OK)
5. **Test Edge Cases**: Empty lists, None values, invalid inputs
6. **Mock External Dependencies**: Don't make real API calls in tests
7. **Use Fixtures**: Don't repeat setup code
8. **Test Error Cases**: Test what happens when things go wrong
9. **Keep Tests Fast**: Mock slow operations
10. **Update Tests When Code Changes**: Tests document expected behavior
11. **Test All API Endpoints**: Ensure every endpoint has integration tests (lesson from Phase 1.4 - discovered missing client API tests)
12. **Regular Test Audits**: Periodically check test coverage to find gaps

## Markers

The project uses pytest markers to categorize tests:

```python
@pytest.mark.slow  # Marks slow tests
@pytest.mark.integration  # Integration tests
@pytest.mark.unit  # Unit tests
```

Run specific categories:
```bash
# Skip slow tests
python -m pytest -m "not slow"

# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration
```

## Continuous Integration

Tests should be run:
1. Before committing code
2. In pull requests
3. Before merging to main
4. In CI/CD pipeline

## Need Help?

1. Check `TEST_FIXES.md` for historical issues and solutions
2. Run `DIAGNOSE_TESTS.py` for comprehensive diagnostics
3. Check test output carefully - pytest provides good error messages
4. Use `pytest -vv` for verbose output
5. Enable SQL echo in database tests to see queries
6. Set breakpoints and use the debugger

Remember: Tests are documentation. They show how the code is supposed to work!