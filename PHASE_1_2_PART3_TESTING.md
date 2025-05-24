# Phase 1.2 Part 3 - Testing Guide

## Manual Testing Instructions

### 1. Start the FastAPI Server

Open a terminal in the project root and run:
```bash
# Option 1: From project root
python -m uvicorn backend.app:app --reload

# Option 2: Using the PyCharm run configuration
# Select "FastAPI Server" from the dropdown and click run
```

The server should start on http://localhost:8000

### 2. Test the Endpoints

Once the server is running, test these endpoints:

#### Using a Web Browser:
- http://localhost:8000/ - Should show API status
- http://localhost:8000/health - Should show health check
- http://localhost:8000/api/teacher/test - Should show "Teacher router is working!"
- http://localhost:8000/api/teacher/test-db - Should show database connection status
- http://localhost:8000/docs - Should show interactive API documentation

#### Using curl (Command Prompt):
```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# Test teacher router
curl http://localhost:8000/api/teacher/test

# Test database connection
curl http://localhost:8000/api/teacher/test-db
```

#### Using PowerShell:
```powershell
# Test endpoints
Invoke-WebRequest -Uri http://localhost:8000/api/teacher/test | Select-Object -ExpandProperty Content
```

### 3. Check API Documentation

Visit http://localhost:8000/docs in your browser. You should see:
- All endpoints listed
- "teacher" tag with the test endpoints
- Ability to try endpoints directly from the browser

## Expected Results

All endpoints should return JSON responses:

1. `/` - API status message
2. `/health` - Health check status
3. `/api/teacher/test` - "Teacher router is working!"
4. `/api/teacher/test-db` - Database connection confirmation

## What's Implemented

✅ `backend/api/teacher_routes.py` created with:
- Router configuration with prefix and tags
- Test endpoint (/test)
- Database test endpoint (/test-db)

✅ `backend/app.py` updated to:
- Import teacher_routes
- Include router with /api prefix

✅ API structure ready for CRUD endpoints

## Next Steps

If all tests pass, we're ready for Part 4: Adding CRUD endpoints one at a time.
