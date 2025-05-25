# Service Layer Architecture

## Overview
The service layer provides business logic and database operations, sitting between the API routes and the database models. All services inherit from `BaseCRUD` to ensure consistent patterns.

## Base Service Pattern

### BaseCRUD Class
Located in `backend/services/database.py`, provides standard CRUD operations:

```python
class BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]:
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType
    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType
    def remove(self, db: Session, id: Any) -> ModelType
```

### Creating a New Service

1. **Import required types**:
```python
from typing import List, Optional, Type
from sqlalchemy.orm import Session
from backend.services.database import BaseCRUD
from backend.models.your_model import YourModelDB, YourModelCreate, YourModelUpdate
```

2. **Define service class**:
```python
class YourService(BaseCRUD[YourModelDB, YourModelCreate, YourModelUpdate]):
    def __init__(self, model: Type[YourModelDB]):
        super().__init__(model)
```

3. **Add custom methods**:
```python
    def get_teacher_items(self, db: Session, teacher_id: str) -> List[YourModelDB]:
        """Get all items belonging to a specific teacher"""
        return db.query(self.model).filter(
            self.model.teacher_id == teacher_id
        ).all()
    
    def create_for_teacher(self, db: Session, obj_in: YourModelCreate, teacher_id: str) -> YourModelDB:
        """Create item with teacher assignment"""
        obj_data = obj_in.dict()
        obj_data["teacher_id"] = teacher_id
        return self.create(db, obj_data)
```

4. **Create global instance**:
```python
# At bottom of file
your_service = YourService(YourModelDB)
```

## Existing Services

### ClientService
**File**: `backend/services/client_service.py`
**Purpose**: Manages virtual client profiles
**Key Methods**:
- `get_teacher_clients()` - Filter by teacher
- `create_client_for_teacher()` - Create with teacher assignment
- `can_update()` / `can_delete()` - Permission checks

### RubricService
**File**: `backend/services/rubric_service.py`
**Purpose**: Manages evaluation rubrics
**Key Methods**:
- `get_teacher_rubrics()` - Filter by teacher
- `create_rubric_for_teacher()` - Create with validation
- `is_rubric_in_use()` - Cascade protection check

### SectionService
**File**: `backend/services/section_service.py`
**Purpose**: Manages course sections
**Key Methods**:
- `get_teacher_sections()` - Filter by teacher
- `create_section_for_teacher()` - Create with teacher assignment

### EnrollmentService
**File**: `backend/services/enrollment_service.py`
**Purpose**: Manages student enrollments
**Key Methods**:
- `enroll_student()` - Enroll with duplicate handling
- `unenroll_student()` - Soft delete
- `get_section_roster()` - List enrolled students
- `is_student_enrolled()` - Check enrollment status
- `get_student_sections()` - Get student's sections

## Service Patterns

### Permission Checks
Standard pattern for checking permissions:
```python
def can_update(self, db: Session, item_id: str, teacher_id: str) -> bool:
    item = self.get(db, item_id)
    return item and item.teacher_id == teacher_id

def can_delete(self, db: Session, item_id: str, teacher_id: str) -> bool:
    return self.can_update(db, item_id, teacher_id)
```

### Soft Delete Pattern
For maintaining history:
```python
def soft_delete(self, db: Session, item_id: str) -> bool:
    item = self.get(db, item_id)
    if item:
        item.is_active = False
        db.commit()
        return True
    return False
```

### Filter Active Records
```python
def get_active_items(self, db: Session) -> List[ModelType]:
    return db.query(self.model).filter(
        self.model.is_active == True
    ).all()
```

### Cascade Protection
Check dependencies before deletion:
```python
def is_safe_to_delete(self, db: Session, item_id: str) -> bool:
    # Check if item is referenced elsewhere
    dependent_count = db.query(DependentModel).filter(
        DependentModel.item_id == item_id
    ).count()
    return dependent_count == 0
```

## Testing Services

### Unit Test Structure
```python
def test_service_method():
    # Create in-memory database
    db = create_test_database()
    
    # Create test data
    test_item = create_test_item()
    
    # Call service method
    result = service.method(db, test_item)
    
    # Assert results
    assert result.expected_field == expected_value
```

### Mock Data
Use factories or direct creation:
```python
def create_test_teacher_id():
    return "test-teacher-123"

def create_test_item(teacher_id: str):
    return ModelCreate(
        name="Test Item",
        teacher_id=teacher_id
    )
```

## Best Practices

1. **Keep services focused** - One service per resource type
2. **Use dependency injection** - Pass database session as parameter
3. **Return models, not schemas** - Let routes handle serialization
4. **Handle None gracefully** - Check if items exist before operations
5. **Use transactions** - Database operations should be atomic
6. **Validate business rules** - Services enforce business logic
7. **Keep it testable** - Avoid external dependencies