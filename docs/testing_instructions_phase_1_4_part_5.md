## Updated Testing Instructions for Phase 1.4 Part 5

### Prerequisites

1. **Ensure database is up to date**:
   ```bash
   # Recreate the database with new course section tables
   python -m backend.scripts.init_db
   ```

2. **Activate virtual environment**:
   ```bash
   .venv\Scripts\activate
   ```

3. **Start the FastAPI server**:
   ```bash
   python -m uvicorn backend.app:app --reload
   ```

### Testing Options

#### Option 1: Manual API Testing
This is the most reliable way to test the endpoints:

```bash
# Run the manual test script
python test_enrollment_endpoints.py
```

This script will:
- Create a test section
- Test all enrollment operations
- Clean up after itself
- Show clear pass/fail results

#### Option 2: Run Integration Tests
The pytest integration tests require proper database setup:

```bash
# First, verify database tables exist
python test_db_tables.py

# Then run the enrollment tests
python -m pytest tests/integration/test_enrollment_api.py -v -s

# Or use the test runner
python test_enrollment_integration.py
```

#### Option 3: Test Individual Endpoints with curl

1. **Create a test section**:
```bash
curl -X POST http://localhost:8000/api/teacher/sections ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"Test Section\", \"description\": \"Test\", \"course_code\": \"TEST101\"}"
```

2. **View empty roster** (use section ID from step 1):
```bash
curl http://localhost:8000/api/teacher/sections/{SECTION_ID}/roster
```

3. **Enroll a student**:
```bash
curl -X POST http://localhost:8000/api/teacher/sections/{SECTION_ID}/enroll ^
  -H "Content-Type: application/json" ^
  -d "{\"student_id\": \"student-001\", \"role\": \"student\"}"
```

4. **Unenroll a student**:
```bash
curl -X DELETE http://localhost:8000/api/teacher/sections/{SECTION_ID}/enroll/student-001
```

### Troubleshooting Test Failures

If you see "no such table: course_sections" errors:
1. The database needs to be recreated with the new tables
2. Run: `python -m backend.scripts.init_db`
3. Verify tables: `python test_db_tables.py`

If you see 403 Forbidden errors:
1. This is likely a teacher ID mismatch
2. The mock authentication returns "teacher-123"
3. Ensure test sections are created with teacher_id="teacher-123"

### Expected Results

✅ **Manual test script** (`test_enrollment_endpoints.py`):
- All 10 tests should pass
- Clear success messages for each operation

✅ **Integration tests**:
- 15 tests total
- 4 tests check permission errors (expected 403)
- 11 tests check normal operations

✅ **API Documentation**:
- Visit http://localhost:8000/docs
- New endpoints should appear under teacher routes
- Test them interactively in the Swagger UI

### Quick Verification

The fastest way to verify everything works:

```bash
# 1. Ensure server is running
# 2. Run the manual test
python test_enrollment_endpoints.py

# Should see:
# ✅ All enrollment endpoint tests completed!
```

This confirms:
- Endpoints are accessible
- Database operations work
- Business logic is correct
- Error handling works properly
