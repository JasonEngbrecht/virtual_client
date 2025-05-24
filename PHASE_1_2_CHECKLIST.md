# Phase 1.2: ClientProfile CRUD - Implementation Checklist

## Overview
Implement full CRUD operations for ClientProfile with teacher-specific access control.

## Tasks

### 1. Client Service Layer
**File**: `backend/services/client_service.py`

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import ClientProfileDB, ClientProfileCreate, ClientProfileUpdate
from .database import BaseCRUD

class ClientService(BaseCRUD[ClientProfileDB]):
    def __init__(self):
        super().__init__(ClientProfileDB)
    
    def get_teacher_clients(self, db: Session, teacher_id: str) -> List[ClientProfileDB]:
        """Get all clients for a specific teacher"""
        pass
    
    def create_client(self, db: Session, client: ClientProfileCreate, teacher_id: str) -> ClientProfileDB:
        """Create a new client for a teacher"""
        pass
    
    # Add more methods...

client_service = ClientService()
```

### 2. Teacher API Routes
**File**: `backend/api/teacher_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..services import get_db
from ..services.client_service import client_service
from ..models import ClientProfile, ClientProfileCreate, ClientProfileUpdate

router = APIRouter()

# Placeholder for auth
def get_current_teacher(token: str = Depends()) -> str:
    # TODO: Implement actual authentication
    return "teacher-1"

@router.post("/clients", response_model=ClientProfile)
async def create_client(
    client_data: ClientProfileCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """Create a new virtual client"""
    pass

# Add more routes...
```

### 3. Update Main App
**File**: `backend/app.py`

Add:
```python
from .api import teacher_routes

app.include_router(teacher_routes.router, prefix="/api/teacher", tags=["teacher"])
```

### 4. Unit Tests
**File**: `tests/unit/test_client_service.py`

- Test create_client
- Test get_teacher_clients
- Test update with permission check
- Test delete with cascade check

### 5. Integration Tests  
**File**: `tests/integration/test_teacher_api.py`

- Test all endpoints
- Test authentication
- Test error cases
- Test permission boundaries

## Success Criteria

- [ ] All CRUD operations working
- [ ] Teachers can only see/modify their own clients
- [ ] Proper error handling (404, 403, 400)
- [ ] All tests passing
- [ ] API documentation updated at /docs

## Notes

- Use existing BaseCRUD methods where possible
- Add teacher_id filtering to all operations
- Consider soft delete vs hard delete
- Update session/evaluation cascading rules
