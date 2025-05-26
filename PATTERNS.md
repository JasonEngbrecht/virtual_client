# Virtual Client - Established Patterns Reference

Quick reference for implementation patterns. Organized by category for easy navigation.

## 📑 Table of Contents
- [🔐 Authentication Patterns](#-authentication-patterns)
- [📊 Database Patterns](#-database-patterns)
- [🏗️ Service Architecture](#️-service-architecture)
- [🛣️ API Route Patterns](#️-api-route-patterns)
- [🚨 Error Handling](#-error-handling)
- [🧪 Testing Patterns](#-testing-patterns)
- [📐 Code Organization](#-code-organization)
- [🔄 Common Workflows](#-common-workflows)

---

## 🔐 Authentication Patterns

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

### Security Principles
- Teacher isolation: Teachers only see their own data
- Student isolation: Students only see enrolled sections
- Use 404 instead of 403 to avoid revealing resource existence

---

## 📊 Database Patterns

### UUID Primary Keys
All models use UUIDs for better distributed system support:
```python
from uuid import uuid4
from sqlalchemy import String
from sqlalchemy.orm import mapped_column

id: str = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
```

### Timestamps
Standard timestamp fields for all models:
```python
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column

created_at: datetime = mapped_column(DateTime, default=datetime.utcnow)
updated_at: datetime = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
```

### Soft Delete Pattern
Preserve data history instead of hard deleting:
```python
# Model field
is_active: bool = mapped_column(Boolean, default=True)

# Soft delete implementation
def soft_delete(self, db: Session, item_id: str) -> bool:
    item = db.query(self.model).filter(self.model.id == item_id).first()
    if item:
        item.is_active = False
        db.commit()
        return True
    return False

# Query only active items
db.query(Model).filter(Model.is_active == True).all()
```
**Used in**: SectionEnrollment, future models needing history

### JSON Fields
For flexible configuration data:
```python
settings: dict = mapped_column(JSON, default=dict)
```

### Foreign Key Relationships
```python
# In model definition
teacher_id: str = mapped_column(String, ForeignKey("users.id"))

# Relationship
teacher = relationship("User", back_populates="sections")
```

---

## 🏗️ Service Architecture

### Base Service Pattern
All services inherit from `BaseCRUD` for consistent interface:
```python
from typing import Type
from .database import BaseCRUD

class ServiceName(BaseCRUD[ModelDB, SchemaCreate, SchemaUpdate]):
    def __init__(self, model: Type[ModelDB]):
        super().__init__(model)
```

### Teacher-Specific Methods
Standard pattern for teacher-owned resources:
```python
def get_teacher_items(self, db: Session, teacher_id: str):
    return db.query(self.model).filter(
        self.model.teacher_id == teacher_id
    ).all()

def create_item_for_teacher(self, db: Session, item_data: SchemaCreate, teacher_id: str):
    item = self.model(**item_data.model_dump(), teacher_id=teacher_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def can_update(self, db: Session, item_id: str, teacher_id: str) -> bool:
    item = self.get(db, item_id)
    return item and item.teacher_id == teacher_id

def can_delete(self, db: Session, item_id: str, teacher_id: str) -> bool:
    return self.can_update(db, item_id, teacher_id)
```

### Service Composition
Services can use other services:
```python
# In enrollment endpoints
if not section_service.can_update(db, section_id, teacher_id):
    raise HTTPException(status_code=403, detail="...")

enrollments = enrollment_service.get_section_roster(db, section_id)
```

### Global Service Instances
Create singleton at module level:
```python
# At bottom of service file
service_name = ServiceName(ModelDB)
```

### Service Method Naming
- `get_*` - Retrieve data
- `create_*` - Create new records
- `update_*` - Modify existing records
- `delete_*` - Remove records (hard or soft)
- `can_*` - Permission checks
- `is_*` - Boolean checks

### Efficient Aggregation Queries
Use SQL aggregation for statistics to avoid N+1 queries:
```python
def get_section_stats(self, db: Session, section_id: str) -> Dict:
    """Get enrollment statistics using SQL aggregation"""
    stats = db.query(
        func.count(case((Model.is_active == True, 1))).label('active_count'),
        func.count(case((Model.is_active == False, 1))).label('inactive_count'),
        func.count(Model.id).label('total_count')
    ).filter(
        Model.section_id == section_id
    ).first()
    
    return {
        "active_count": stats.active_count or 0,
        "inactive_count": stats.inactive_count or 0,
        "total_count": stats.total_count or 0
    }
```

### Bulk Statistics Pattern
For multiple items, use GROUP BY to get all stats in one query:
```python
def get_all_sections_stats(self, db: Session, teacher_id: str) -> List[Dict]:
    # Get all sections first
    sections = db.query(Section.id, Section.name).filter(
        Section.teacher_id == teacher_id
    ).all()
    
    # Get stats for all sections in one query
    stats = db.query(
        Model.section_id,
        func.count(case((Model.is_active == True, 1))).label('active'),
        func.count(Model.id).label('total')
    ).filter(
        Model.section_id.in_([s.id for s in sections])
    ).group_by(
        Model.section_id
    ).all()
    
    # Combine results, handling sections with no enrollments
    stats_dict = {stat.section_id: stat for stat in stats}
    return [
        {
            "section_id": section.id,
            "name": section.name,
            "active": stats_dict.get(section.id, {}).active or 0,
            "total": stats_dict.get(section.id, {}).total or 0
        }
        for section in sections
    ]
```

---

## 🛣️ API Route Patterns

### Router Structure
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/role",  # e.g., "/teacher", "/student"
    tags=["role"],
    responses={404: {"description": "Not found"}},
)
```

### Standard CRUD Routes
```python
@router.get("", response_model=List[ItemSchema])
async def list_items():
    """List all items for authenticated user"""

@router.post("", response_model=ItemSchema, status_code=201)
async def create_item(item_data: ItemCreate):
    """Create new item"""

@router.get("/{id}", response_model=ItemSchema)
async def get_item(id: str):
    """Get specific item by ID"""

@router.put("/{id}", response_model=ItemSchema)
async def update_item(id: str, item_data: ItemUpdate):
    """Update item (supports partial updates)"""

@router.delete("/{id}", status_code=204)
async def delete_item(id: str):
    """Delete item"""
```

### Nested Resource Routes
For hierarchical relationships:
```python
@router.get("/sections/{section_id}/roster")
@router.post("/sections/{section_id}/enroll")
@router.delete("/sections/{section_id}/enroll/{student_id}")
```

### Route Ordering
**Important**: Place specific routes before parameterized routes to avoid conflicts:
```python
# ✅ CORRECT - /sections/stats comes before /sections/{id}
@router.get("/sections/stats")  # This must come first
async def get_all_stats(): ...

@router.get("/sections/{section_id}")  # This comes after
async def get_section(section_id: str): ...

# ❌ WRONG - /sections/stats will never be reached
@router.get("/sections/{section_id}")
@router.get("/sections/stats")  # This will be treated as section_id="stats"
```

### Response Models
Always declare response models for type safety:
```python
@router.get("", response_model=List[ItemSchema])
@router.post("", response_model=ItemSchema, status_code=201)
```

### Statistics Response Pattern
For statistics endpoints, return consistent format:
```python
# Single item stats
{
    "item_id": "uuid",
    "name": "Item Name",  # Include identifying info
    "active_count": 25,
    "inactive_count": 3,
    "total_count": 28
}

# Bulk stats - array of same structure
[
    {"item_id": "...", "name": "...", "active_count": 25, ...},
    {"item_id": "...", "name": "...", "active_count": 0, ...}  # Include zero counts
]
```

### Partial Updates
PUT endpoints accept partial data:
```python
update_data = item_data.model_dump(exclude_unset=True)
if not update_data:
    raise HTTPException(
        status_code=400,
        detail="No valid fields provided for update"
    )
```

---

## 🚨 Error Handling

### Standard HTTP Status Codes

#### 200 OK
Default for successful GET, PUT

#### 201 Created
```python
@router.post("", status_code=201)
```

#### 204 No Content
```python
@router.delete("/{id}", status_code=204)
async def delete_item(id: str):
    # ... delete logic ...
    return None  # Returns empty response with 204
```

#### 400 Bad Request
```python
raise HTTPException(
    status_code=400,
    detail="Specific error message explaining the issue"
)
```
**Use for**: Invalid data, business rule violations

#### 403 Forbidden
```python
raise HTTPException(
    status_code=403,
    detail="You don't have permission to access this resource"
)
```
**Use for**: Teacher accessing another teacher's resources

#### 404 Not Found
```python
raise HTTPException(
    status_code=404,
    detail=f"Resource with id '{resource_id}' not found"
)
```
**Include**: Resource type and ID in message

#### 409 Conflict
```python
raise HTTPException(
    status_code=409,
    detail="Cannot delete resource because it is in use"
)
```
**Use for**: Cascade protection, duplicate prevention

#### 422 Validation Error
Handled automatically by FastAPI/Pydantic for request validation

### Error Message Guidelines
- Be specific but secure (don't leak sensitive info)
- Include actionable information when possible
- Use consistent format across endpoints
- For students: Use 404 instead of 403 (security through obscurity)

---

## 🧪 Testing Patterns

### Test File Organization
```
tests/
├── conftest.py          # Shared fixtures
├── unit/               # Service/model tests
│   ├── test_client_service.py
│   └── test_rubric_service.py
└── integration/        # API endpoint tests
    ├── test_teacher_api.py
    └── test_student_api.py
```

### Integration Test Structure
```python
def test_endpoint_name(client: TestClient, db_session: Session):
    # Arrange - Set up test data
    test_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    
    # Act - Call the endpoint
    response = client.post("/api/teacher/items", json=test_data)
    
    # Assert - Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_data["name"]
    assert "id" in data
```

### Common Test Fixtures
In `tests/conftest.py`:
```python
@pytest.fixture
def teacher_headers():
    # Mock auth headers for teacher
    return {"Authorization": "Bearer teacher-123"}

@pytest.fixture
def student_headers():
    # Mock auth headers for student
    return {"Authorization": "Bearer student-123"}

@pytest.fixture
def sample_client(db_session):
    # Create and return test client
    client = ClientProfileDB(...)
    db_session.add(client)
    db_session.commit()
    return client
```

### Testing Error Cases
```python
def test_not_found_error(client: TestClient):
    response = client.get("/api/teacher/items/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_permission_denied(client: TestClient):
    # Create item as teacher-123
    # Try to access as teacher-456
    response = client.get("/api/teacher/items/{id}", 
                         headers={"Authorization": "Bearer teacher-456"})
    assert response.status_code == 403
```

### Test Naming Conventions
- `test_<action>_<expected_result>`
- `test_<endpoint>_<scenario>`
- Examples:
  - `test_create_client_success`
  - `test_update_client_not_found`
  - `test_delete_rubric_in_use_fails`

---

## 📐 Code Organization

### Import Order
```python
# 1. Standard library imports
import json
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 3. Local application imports
from ..services import get_db
from ..services.client_service import client_service
from ..models.client_profile import ClientProfile

# 4. Type imports (if using TYPE_CHECKING)
if TYPE_CHECKING:
    from ..models.user import User
```

### File Naming Conventions
| Type | Pattern | Example |
|------|---------|---------|
| Models | `{resource}.py` | `client_profile.py` |
| Services | `{resource}_service.py` | `client_service.py` |
| Routes | `{role}_routes.py` | `teacher_routes.py` |
| Tests | `test_{what}.py` | `test_client_service.py` |

### Module Structure
```python
"""
Module docstring explaining purpose
"""

# Imports

# Constants
DEFAULT_PAGE_SIZE = 50

# Classes/Functions

# Module-level instances (for services)
service_instance = ServiceClass()
```

---

## 🔄 Common Workflows

### Adding a New CRUD Resource

1. **Create the model** (`backend/models/resource.py`):
   ```python
   class ResourceDB(Base):
       __tablename__ = "resources"
       # ... fields ...
   
   class ResourceCreate(BaseModel):
       # ... fields ...
   
   class Resource(ResourceCreate):
       id: str
       created_at: datetime
   ```

2. **Create the service** (`backend/services/resource_service.py`):
   ```python
   class ResourceService(BaseCRUD[ResourceDB, ResourceCreate, ResourceUpdate]):
       def __init__(self):
           super().__init__(ResourceDB)
   
   resource_service = ResourceService()
   ```

3. **Add routes** (to appropriate router):
   ```python
   from ..services.resource_service import resource_service
   
   @router.get("/resources", response_model=List[Resource])
   async def list_resources(
       db: Session = Depends(get_db),
       teacher_id: str = Depends(get_current_teacher)
   ):
       return resource_service.get_teacher_resources(db, teacher_id)
   ```

4. **Write tests**:
   - Unit tests for service methods
   - Integration tests for API endpoints

5. **Update model registry** (`backend/models/__init__.py`):
   ```python
   from .resource import ResourceDB, Resource, ResourceCreate
   ```

### Adding Teacher-Specific Endpoints

1. Check teacher ownership in service layer
2. Use consistent error responses (403 for forbidden)
3. Filter queries by teacher_id
4. Test permission boundaries

### Adding Student Endpoints

1. Check enrollment status first
2. Use 404 instead of 403 (don't reveal existence)
3. Limit data exposure (no other students' info)
4. Test access controls thoroughly

### Implementing Soft Delete

1. Add `is_active` field to model
2. Override delete method to set `is_active = False`
3. Filter queries by `is_active == True`
4. Consider reactivation logic for re-enrollment

---

*This patterns guide is a living document. Update it when establishing new patterns or improving existing ones.*