# Virtual Client - Established Patterns Reference

Quick reference guide for common patterns used throughout the project.

## 🔐 Authentication

### Mock Authentication Pattern
**Current Implementation**: Mock functions return hardcoded user IDs
```python
def get_current_teacher() -> str:
    return "teacher-123"

def get_current_student() -> str:
    return "student-123"
```
**Location**: `backend/api/dependencies.py`
**Future**: Will be replaced with JWT/session-based auth

### Dependency Injection
```python
@router.get("/endpoint")
def endpoint(teacher_id: str = Depends(get_current_teacher)):
    # teacher_id is automatically injected
```

## 🏗️ Service Layer Architecture

### Base Service Pattern
All services inherit from `BaseCRUD`:
```python
class ServiceName(BaseCRUD[ModelDB, SchemaCreate, SchemaUpdate]):
    def __init__(self, model: Type[ModelDB]):
        super().__init__(model)
```
**Example**: `backend/services/client_service.py`

### Teacher-Specific Methods
```python
def get_teacher_items(self, db: Session, teacher_id: str):
    return db.query(self.model).filter(
        self.model.teacher_id == teacher_id
    ).all()

def can_update(self, db: Session, item_id: str, teacher_id: str) -> bool:
    item = self.get(db, item_id)
    return item and item.teacher_id == teacher_id
```

### Global Service Instances
```python
# At bottom of service file
service_name = ServiceName(ModelDB)
```

## 🚨 Error Handling

### Standard Error Responses

#### 404 Not Found
```python
raise HTTPException(
    status_code=404,
    detail=f"Resource with id '{resource_id}' not found"
)
```
**Include**: Resource type and ID

#### 403 Forbidden
```python
raise HTTPException(
    status_code=403,
    detail="You don't have permission to access this resource"
)
```
**Use for**: Teacher accessing another teacher's resources

#### 400 Bad Request
```python
raise HTTPException(
    status_code=400,
    detail="Specific error message explaining the issue"
)
```
**Example**: "No fields provided for update"

#### 422 Validation Error
**Handled automatically by FastAPI/Pydantic**

## 📊 Database Patterns

### Soft Delete Pattern
Used for maintaining history:
```python
# Instead of DELETE
item.is_active = False
db.commit()

# Queries filter by is_active
db.query(Model).filter(Model.is_active == True)
```
**Used in**: SectionEnrollment

### UUID Primary Keys
All models use UUIDs:
```python
id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
```

### Timestamps
Standard fields:
```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: Optional[datetime] = None
```

## 🛣️ API Route Patterns

### Standard CRUD Routes
```python
@router.get("")  # List all
@router.post("")  # Create new
@router.get("/{id}")  # Get one
@router.put("/{id}")  # Update
@router.delete("/{id}")  # Delete
```

### Response Models
Always use Pydantic response models:
```python
@router.get("", response_model=List[ItemSchema])
@router.post("", response_model=ItemSchema, status_code=201)
```

### Partial Updates
PUT endpoints support partial updates:
```python
# Only update provided fields
update_data = obj_in.dict(exclude_unset=True)
```

## 🧪 Testing Patterns

### Integration Test Structure
```python
def test_endpoint_name(client: TestClient, db_session: Session):
    # Arrange
    test_data = create_test_data()
    
    # Act
    response = client.post("/api/endpoint", json=test_data)
    
    # Assert
    assert response.status_code == expected_code
    assert response.json()["field"] == expected_value
```

### Test Fixtures
Located in `tests/conftest.py`:
- `test_client`: FastAPI test client
- `db_session`: Test database session
- Model-specific factories

## 📐 Code Organization

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Blank line
5. Type imports (if using TYPE_CHECKING)

### File Naming
- Services: `{resource}_service.py`
- Routes: `{role}_routes.py`
- Models: `{resource}.py`
- Tests: `test_{what_testing}.py`

## 🔄 Common Workflows

### Adding New CRUD Resource
1. Create model in `backend/models/`
2. Create service in `backend/services/` (inherit BaseCRUD)
3. Add routes to appropriate router file
4. Write integration tests
5. Update model registry in `models/__init__.py`

### Adding New Endpoint
1. Identify appropriate router file
2. Check if service method exists
3. Add endpoint with proper auth dependency
4. Include response model
5. Handle errors consistently
6. Write integration test

## 📝 Documentation

### Endpoint Documentation
FastAPI auto-generates from:
- Function docstrings
- Pydantic model descriptions
- Response model definitions
- Status code declarations

### Code Comments
- Why, not what
- Document business rules
- Explain non-obvious decisions