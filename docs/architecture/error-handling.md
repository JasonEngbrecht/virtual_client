# Error Handling Architecture

## Overview
Consistent error handling provides a better developer experience and makes debugging easier. The project uses FastAPI's HTTPException for all API errors.

## Standard Error Responses

### 404 Not Found
Used when a requested resource doesn't exist.

**Pattern**:
```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail=f"{resource_type} with id '{resource_id}' not found"
)
```

**Example**:
```python
client = client_service.get(db, client_id)
if not client:
    raise HTTPException(
        status_code=404,
        detail=f"Client with id '{client_id}' not found"
    )
```

### 403 Forbidden
Used when user lacks permission for an operation.

**Pattern**:
```python
raise HTTPException(
    status_code=403,
    detail="You don't have permission to {action} this {resource}"
)
```

**Example**:
```python
if not rubric_service.can_update(db, rubric_id, teacher_id):
    raise HTTPException(
        status_code=403,
        detail="You don't have permission to update this rubric"
    )
```

### 400 Bad Request
Used for invalid requests or business rule violations.

**Common Scenarios**:
- Empty update payload
- Invalid state transitions
- Business rule violations

**Examples**:
```python
# Empty update
if not update_data:
    raise HTTPException(
        status_code=400,
        detail="No fields provided for update"
    )

# Duplicate criterion names
if has_duplicates:
    raise HTTPException(
        status_code=400,
        detail=f"Each criterion must have a unique name. Found duplicate: {duplicate_name}"
    )
```

### 409 Conflict
Used when operation would violate data integrity.

**Example**:
```python
if rubric_service.is_rubric_in_use(db, rubric_id):
    raise HTTPException(
        status_code=409,
        detail="Cannot delete rubric that is being used by one or more sessions"
    )
```

### 422 Unprocessable Entity
Automatically handled by FastAPI/Pydantic for validation errors.

**What triggers it**:
- Missing required fields
- Invalid field types
- Validation constraint violations

**Response format**:
```json
{
    "detail": [
        {
            "loc": ["body", "field_name"],
            "msg": "validation error message",
            "type": "error_type"
        }
    ]
}
```

## Service Layer Error Handling

Services should return None or False rather than raising exceptions:

```python
def get_item(self, db: Session, item_id: str) -> Optional[ItemModel]:
    """Returns None if not found"""
    return db.query(self.model).filter(self.model.id == item_id).first()

def delete_item(self, db: Session, item_id: str) -> bool:
    """Returns False if item doesn't exist"""
    item = self.get(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
```

Routes then handle the error responses:

```python
item = service.get_item(db, item_id)
if not item:
    raise HTTPException(status_code=404, detail=f"Item with id '{item_id}' not found")
```

## Validation Error Messages

### Pydantic Model Validation
Enhance error messages with descriptions:

```python
class RubricCriterion(BaseModel):
    name: str = Field(..., description="Unique name for this evaluation criterion")
    weight: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Weight must be between 0.0 and 1.0"
    )
```

### Custom Validators
Provide helpful error messages:

```python
@validator('criteria')
def validate_weights_sum(cls, criteria):
    total = sum(c.weight for c in criteria)
    if not 0.999 <= total <= 1.001:  # Float precision tolerance
        weights_str = ", ".join([f"{c.name}: {c.weight}" for c in criteria])
        raise ValueError(
            f"Criteria weights must sum to exactly 1.0, but your weights sum to {total:.3f}. "
            f"Current weights: {{{weights_str}}}. "
            f"Please adjust the weights so they total 1.0 (100% of the evaluation)."
        )
    return criteria
```

## Security Considerations

### Information Disclosure
Be careful not to reveal sensitive information in error messages:

**Bad**:
```python
detail="User 'john.doe@example.com' not found in database"
```

**Good**:
```python
detail="Invalid credentials"
```

### Student Access Patterns
For student endpoints, use 404 instead of 403 to avoid revealing resource existence:

```python
# For student trying to access non-enrolled section
if not enrollment_service.is_student_enrolled(db, section_id, student_id):
    raise HTTPException(
        status_code=404,  # Not 403!
        detail=f"Section with id '{section_id}' not found"
    )
```

## Testing Error Handling

### Integration Tests
```python
def test_get_nonexistent_returns_404(client: TestClient):
    response = client.get("/api/teacher/items/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    assert "nonexistent-id" in response.json()["detail"]

def test_unauthorized_returns_403(client: TestClient):
    # Create item as teacher-123
    # Try to update as teacher-456
    response = client.put("/api/teacher/items/{id}", json=update_data)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
```

### Error Test Patterns
1. Test each error condition separately
2. Verify both status code and message
3. Check that sensitive info isn't leaked
4. Ensure error messages are helpful

## Best Practices

1. **Be consistent** - Same error = same message format
2. **Be helpful** - Include IDs and explain what went wrong
3. **Be secure** - Don't leak sensitive information
4. **Be specific** - "Client not found" better than "Not found"
5. **Include context** - What was being attempted
6. **Guide fixes** - Tell user how to resolve the issue
7. **Log internally** - Log full errors server-side for debugging