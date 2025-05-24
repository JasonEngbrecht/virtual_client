# Phase 1.2 Testing Checklist

Before moving to Phase 1.3, run these tests to ensure Phase 1.2 is completely working:

## 1. Start the API Server
```bash
python -m uvicorn backend.app:app --reload
```
Verify it starts without errors.

## 2. Run Unit Tests
```bash
# All unit tests
python -m pytest tests/ -v

# Just client service tests
python -m pytest tests/unit/test_client_service.py -v

# With coverage report
python -m pytest tests/unit/test_client_service.py --cov=backend.services.client_service --cov-report=term-missing
```

## 3. Run Integration Tests
```bash
# Quick test suite
python test_quick.py

# All CRUD operations
python test_all_crud.py

# Authentication dependency
python scripts/test_auth_dependency.py

# Error handling
python scripts/test_error_handling.py

# Server verification after fix
python test_server_fix.py
```

## 4. Run End-to-End Test
```bash
# Comprehensive system test
python test_phase_1_2_complete.py
```

## 5. Manual API Testing
Visit http://localhost:8000/docs and manually test a few operations:
- Create a client
- List clients
- Update a client
- Try invalid data (see 422 errors)
- Try non-existent ID (see 404 errors)

## Expected Results
- [ ] Server starts without errors
- [ ] All pytest unit tests pass
- [ ] test_quick.py shows all tests passing
- [ ] test_all_crud.py completes successfully
- [ ] test_auth_dependency.py works correctly
- [ ] test_error_handling.py shows proper error codes (422 for validation)
- [ ] test_phase_1_2_complete.py shows all tests passing
- [ ] Manual API testing works as expected

## Common Issues
1. **Server won't start**: Check for syntax errors, missing imports
2. **Database errors**: Run `python -m backend.scripts.init_db` to reinitialize
3. **Import errors**: Ensure you're in the project root with venv activated
4. **Connection refused**: Make sure server is running for integration tests

## If All Tests Pass ✅
You're ready to move to Phase 1.3 (EvaluationRubric CRUD)!

## If Tests Fail ❌
1. Check the specific error messages
2. Fix the identified issues
3. Re-run the failed tests
4. Don't proceed until all tests pass
