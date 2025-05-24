# Testing Guide for PyCharm

## Quick Start

All tests should now pass! The issues have been fixed:
- ✅ SQLAlchemy text() wrapper added for raw SQL queries
- ✅ pytest-asyncio warning resolved with configuration

## Running Tests in PyCharm

### Using Run Configurations (Recommended)
After restarting PyCharm or reloading the project, you'll see new run configurations in the dropdown:
- **All Tests** - Runs all tests in the project
- **Database Tests** - Runs only database-related tests
- **Initialize Database** - Creates the database
- **Initialize Database with Sample Data** - Creates database with test data

### Using the UI
1. **Run all tests**: Right-click on `tests` folder → Run 'pytest in tests'
2. **Run specific test file**: Click green arrow next to test class/function
3. **Run with coverage**: Right-click → Run 'pytest in tests' with Coverage

### Using Terminal
```bash
# Run all tests
python run_tests.py

# Run database tests only
python run_tests.py tests/unit/test_database.py

# Run with verbose output
python run_tests.py -v

# Run specific test
python -m pytest tests/unit/test_database.py::TestDatabaseService::test_tables_created -v
```

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── unit/                # Unit tests (isolated components)
│   └── test_database.py # Database and CRUD tests
└── integration/         # Integration tests (coming soon)
```

## Key Fixtures Available

- `test_db_service` - Test database service instance
- `db_session` - Database session for tests
- `sample_teacher_id` - Test teacher ID
- `sample_student_id` - Test student ID
- `sample_client_profile` - Pre-created client profile
- `sample_rubric` - Pre-created evaluation rubric
- `sample_session` - Pre-created session

## Debugging Tests in PyCharm

1. Set breakpoints by clicking in the gutter
2. Right-click test → Debug 'pytest...'
3. Use the debugger panel to step through code

## Coverage Reports

After running tests with coverage:
1. View → Tool Windows → Coverage
2. See line-by-line coverage in editor (green/red bars)
3. HTML report: `htmlcov/index.html`

## Common Issues

### Import Errors
- Ensure virtual environment is activated
- Check PyCharm interpreter settings

### Database Errors
- Tests use in-memory SQLite database
- Each test gets a fresh database

### Async Warnings
- Already fixed in pytest.ini
- Set to function scope by default
