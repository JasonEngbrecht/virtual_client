# Authentication Architecture

## Current Implementation (Mock)

The project currently uses mock authentication for development. This will be replaced with real authentication (JWT or session-based) before production.

### Mock Authentication Functions

**Location**: `backend/api/dependencies.py`

```python
def get_current_teacher() -> str:
    """Mock authentication - returns hardcoded teacher ID"""
    return "teacher-123"

def get_current_student() -> str:
    """Mock authentication - returns hardcoded student ID"""
    return "student-123"
```

### Using Authentication in Routes

Authentication is applied using FastAPI's dependency injection:

```python
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_current_teacher

router = APIRouter()

@router.get("/api/teacher/items")
def list_items(
    teacher_id: str = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # teacher_id is automatically injected
    return service.get_teacher_items(db, teacher_id)
```

## Authentication Patterns

### Teacher Endpoints
All teacher endpoints require teacher authentication:

```python
router = APIRouter(
    prefix="/api/teacher",
    tags=["teacher"]
)

# Applied to individual endpoints
@router.post("/clients")
def create_client(
    client: ClientCreate,
    teacher_id: str = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    return client_service.create_client_for_teacher(db, client, teacher_id)
```

### Student Endpoints
Student endpoints use student authentication:

```python
router = APIRouter(
    prefix="/api/student",
    tags=["student"]
)

@router.get("/sections")
def list_my_sections(
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    return enrollment_service.get_student_sections(db, student_id)
```

### Public Endpoints
Some endpoints may not require authentication:

```python
@router.get("/health")
def health_check():
    # No authentication dependency
    return {"status": "healthy"}
```

## Authorization Patterns

### Resource Ownership
Teachers can only access their own resources:

```python
# In service layer
def can_update(self, db: Session, item_id: str, teacher_id: str) -> bool:
    item = self.get(db, item_id)
    return item and item.teacher_id == teacher_id

# In route
if not service.can_update(db, item_id, teacher_id):
    raise HTTPException(
        status_code=403,
        detail="You don't have permission to update this resource"
    )
```

### Student Access Control
Students have read-only access to enrolled resources:

```python
# Check enrollment before allowing access
if not enrollment_service.is_student_enrolled(db, section_id, student_id):
    raise HTTPException(
        status_code=404,  # Use 404 not 403 for security
        detail=f"Section with id '{section_id}' not found"
    )
```

## Future Authentication Implementation

### JWT Token Authentication (Planned)
```python
from jose import JWTError, jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return get_user(user_id)
```

### Role-Based Access
```python
def get_current_teacher(user: User = Depends(get_current_user)) -> str:
    if user.role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="This endpoint requires teacher role"
        )
    return user.id
```

## Testing with Mock Authentication

### Override in Tests
```python
def override_get_current_teacher():
    return "test-teacher-123"

app.dependency_overrides[get_current_teacher] = override_get_current_teacher
```

### Multiple Test Users
```python
@pytest.fixture
def teacher_auth():
    def _get_teacher(teacher_id: str = "test-teacher-123"):
        return lambda: teacher_id
    return _get_teacher

def test_teacher_isolation(client: TestClient, teacher_auth):
    # Test with teacher-123
    app.dependency_overrides[get_current_teacher] = teacher_auth("teacher-123")
    response1 = client.post("/api/teacher/items", json=item_data)
    
    # Test with teacher-456
    app.dependency_overrides[get_current_teacher] = teacher_auth("teacher-456")
    response2 = client.get(f"/api/teacher/items/{item_id}")
    assert response2.status_code == 403
```

## Security Best Practices

1. **Never trust client data** - Always verify ownership server-side
2. **Use consistent patterns** - Same auth method across all endpoints
3. **Fail securely** - Default to denying access
4. **Hide resource existence** - Use 404 instead of 403 for students
5. **Validate roles** - Check user role matches endpoint type
6. **Token expiration** - Plan for token refresh (future)
7. **Audit logging** - Log authentication attempts (future)

## Migration Plan

When implementing real authentication:

1. Create real `get_current_user()` function with JWT/session validation
2. Update `get_current_teacher()` and `get_current_student()` to check roles
3. Add login/logout endpoints
4. Update frontend to handle authentication flow
5. Add token refresh mechanism
6. Update tests to use proper auth tokens
7. Remove mock authentication functions