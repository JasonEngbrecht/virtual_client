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

### Reactivation Pattern
For soft-deleted items that can be reactivated:
```python
def reactivate_item(self, db: Session, item_id: str) -> Optional[ModelType]:
    # Check for existing inactive item
    existing = db.query(self.model).filter(
        self.model.id == item_id,
        self.model.is_active == False
    ).first()
    
    if existing:
        # Reactivate with updated timestamp
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    return None

# Example: Re-enrolling a student
def enroll_student(self, db: Session, section_id: str, student_id: str):
    # Check for existing enrollment (active or inactive)
    existing = db.query(SectionEnrollmentDB).filter(
        SectionEnrollmentDB.section_id == section_id,
        SectionEnrollmentDB.student_id == student_id
    ).first()
    
    if existing:
        if existing.is_active:
            return existing  # Already enrolled
        else:
            # Reactivate enrollment
            existing.is_active = True
            existing.enrolled_at = datetime.utcnow()
            db.commit()
            return existing
    
    # Create new enrollment if none exists
    # ...
```
**Used in**: SectionEnrollment, future re-enrollable resources

### JSON Fields
For flexible configuration data:
```python
settings: dict = mapped_column(JSON, default=dict)
```

### Token Tracking Pattern
Track API usage at the session level for cost monitoring:
```python
# Session model fields
total_tokens: int = mapped_column(Integer, default=0)
estimated_cost: float = mapped_column(Float, default=0.0)
status: str = mapped_column(String, default="active")  # 'active' or 'completed'

# Update on each message
session.total_tokens += message_tokens
session.estimated_cost = (session.total_tokens / 100) * PRICE_PER_100_TOKENS
```
**Pricing**: 
- Claude Haiku: $0.003 per 100 tokens (~$0.003 per conversation)
- Claude Sonnet: $0.03 per 100 tokens (~$0.03 per conversation)

### Token Counting Utility Pattern
Centralize token counting logic in a dedicated utility:
```python
# backend/utils/token_counter.py
from typing import Dict

# Pricing per 1M tokens
PRICING: Dict[str, Dict[str, float]] = {
    "haiku": {
        "input": 0.25,
        "output": 1.25,
        "average": 0.75  # Used for MVP
    },
    "sonnet": {
        "input": 3.00,
        "output": 15.00,
        "average": 9.00
    }
}

def count_tokens(text: str) -> int:
    """Estimate tokens using 4 chars ≈ 1 token rule"""
    if not text:
        return 0
    return max(1, len(text) // 4)

def calculate_cost(tokens: int, model: str = "haiku", token_type: str = "average") -> float:
    """Calculate cost for given tokens"""
    price_per_million = PRICING[model][token_type]
    return (tokens / 1_000_000) * price_per_million
```

### Automatic Token Counting Pattern
Count tokens automatically when not provided:
```python
# In add_message method
if message.token_count == 0 and message.content:
    message.token_count = count_tokens(message.content)

# Update session totals for ALL messages (user and assistant)
if message.token_count > 0:
    session.total_tokens += message.token_count
    cost_incurred = calculate_cost(message.token_count)
    session.estimated_cost += cost_incurred
```
**Benefits**:
- No need to manually count tokens
- Consistent counting across the application
- Both user and assistant messages tracked
- Easy to switch pricing models

### Session Status Pattern
Replace boolean flags with explicit status fields:
```python
# Instead of:
is_active: bool = mapped_column(Boolean, default=True)

# Use:
status: Literal["active", "completed"] = mapped_column(String, default="active")

# Allows for future states like "paused", "expired", "error"
```

### Session Lifecycle Management
Manage session state transitions with business logic:
```python
def end_session(self, db: Session, session_id: str, student_id: str, session_notes: Optional[str] = None) -> Optional[SessionDB]:
    """End an active session with validation"""
    # Get session with student validation
    session = self.get_session(db, session_id, student_id)
    if not session:
        return None
    
    # Prevent ending already completed sessions
    if session.status == 'completed':
        return None
    
    # Update session state
    update_data = {
        'status': 'completed',
        'ended_at': datetime.utcnow()
    }
    if session_notes:
        update_data['session_notes'] = session_notes
    
    return self.update(db, session_id, **update_data)

# Check for active sessions before creating new ones
def get_active_session(self, db: Session, student_id: str, client_profile_id: str) -> Optional[SessionDB]:
    sessions = self.get_multi(
        db,
        student_id=student_id,
        client_profile_id=client_profile_id,
        status='active',
        limit=1
    )
    return sessions[0] if sessions else None
```

### Model Simplification Pattern
For MVP, remove fields that aren't immediately needed:
```python
# SessionDB for MVP - minimal fields
class SessionDB(Base):
    id: str
    student_id: str  
    client_profile_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    status: str  # 'active' or 'completed'
    total_tokens: int
    estimated_cost: float
    session_notes: Optional[str]
    
# Removed: rubric_id, evaluation_result_id, messages JSON
# These can be added in later phases when needed
```

### Foreign Key Relationships
```python
# In model definition
teacher_id: str = mapped_column(String, ForeignKey("users.id"))

# Relationship
teacher = relationship("User", back_populates="sections")
```

### ORM-Based Database Initialization Pattern
Use SQLAlchemy ORM for database initialization instead of raw SQL:
```python
# backend/scripts/init_db_orm.py
from sqlalchemy import text
from backend.services.database import db_service, Base
from backend.models import (  # Import all models to register with Base
    ClientProfileDB, SessionDB, MessageDB, ...
)

def init_database_orm():
    """Initialize database using SQLAlchemy ORM models"""
    # Create all tables from registered models
    db_service.create_tables()
    
    # Verify tables with proper SQL escaping
    with db_service.get_db() as db:
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
    
    return True
```
**Benefits**:
- Ensures schema matches ORM models
- No need to maintain separate SQL files
- Automatic handling of relationships and constraints
- Works across different databases (SQLite, PostgreSQL)

### Model Ownership Fields
**IMPORTANT**: Different models use different field names for ownership:

| Model | Ownership Field | Example |
|-------|-----------------|----------|
| CourseSectionDB | `teacher_id` | `section.teacher_id` |
| ClientProfileDB | `created_by` | `client.created_by` |
| EvaluationRubricDB | `created_by` | `rubric.created_by` |
| AssignmentDB | via section | `section.teacher_id` |

```python
# When checking ownership in services:
# For sections:
if section.teacher_id != teacher_id:
    return False

# For clients and rubrics:
if client.created_by != teacher_id:
    return False
```

---

## 🔧 Environment Configuration Pattern

### Loading Environment Variables
Always load `.env` file at the top of entry points:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
```

**Where to add dotenv loading:**
- Main application files (`app.py`, `start_server.py`)
- Test configuration (`conftest.py`, `run_tests.py`)
- Streamlit apps (`mvp/utils.py`)
- Any standalone scripts

**Key Environment Variables:**
- `ANTHROPIC_API_KEY` - Required for AI conversations
- `APP_ENV` - development/production
- `DATABASE_URL` - Database connection string
- `LLM_PROVIDER` - anthropic/openai
- `SECRET_KEY` - Application secret key

**Best Practices:**
- Never commit `.env` files to version control
- Provide `.env.example` with dummy values
- Load dotenv at the very beginning of files
- Use `os.getenv()` with defaults for optional values

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

### Student-Specific Methods
Pattern for student-owned resources (e.g., sessions):
```python
def create_session(self, db: Session, session_data: SessionCreate, student_id: str) -> SessionDB:
    """Create session enforcing authenticated student ID"""
    session_dict = session_data.model_dump()
    session_dict['student_id'] = student_id  # Override with authenticated ID
    session_dict['status'] = 'active'
    session_dict['total_tokens'] = 0
    session_dict['estimated_cost'] = 0.0
    return self.create(db, **session_dict)

def get_session(self, db: Session, session_id: str, student_id: Optional[str] = None) -> Optional[SessionDB]:
    """Get session with optional student validation"""
    session = self.get(db, session_id)
    if not session:
        return None
    
    # If student_id provided, validate ownership
    if student_id and session.student_id != student_id:
        return None  # Return None instead of 403 for security
    
    return session

def get_student_sessions(self, db: Session, student_id: str, status: Optional[str] = None) -> List[SessionDB]:
    """Get all sessions for a student with optional filtering"""
    filters = {'student_id': student_id}
    if status:
        filters['status'] = status
    return self.get_multi(db, **filters)
```

### Service Composition
Services can use other services:
```python
# In enrollment endpoints
if not section_service.can_update(db, section_id, teacher_id):
    raise HTTPException(status_code=403, detail="...")

enrollments = enrollment_service.get_section_roster(db, section_id)
```

### Conversation Orchestration Pattern
For complex flows that coordinate multiple services:
```python
class ConversationService:
    """Orchestrates conversation flow between multiple services"""
    
    def start_conversation(self, db: DBSession, student: StudentAuth, client_id: str) -> Session:
        # 1. Validate prerequisites
        client = client_service.get(db, client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # 2. Create session
        session_db = session_service.create_session(db, SessionCreate(
            student_id=student.student_id,
            client_profile_id=client_id
        ), student.student_id)
        
        # 3. Generate AI context
        system_prompt = prompt_service.generate_system_prompt(client)
        
        # 4. Get AI greeting
        anthropic = anthropic_service()
        greeting = anthropic.generate_response(
            messages=[{"role": "user", "content": "Introduce yourself..."}],
            system_prompt=system_prompt
        )
        
        # 5. Store greeting as first message
        session_service.add_message(db, session_db.id, MessageCreate(
            role="assistant",
            content=greeting,
            token_count=count_tokens(greeting)
        ))
        
        return Session.model_validate(session_db)

    def send_message(self, db: DBSession, session_id: str, content: str, user: StudentAuth) -> Message:
        # 1. Validate access
        session_db = session_service.get_session(db, session_id)
        if not session_db or session_db.student_id != user.student_id:
            raise ValueError("Access denied")
        
        # 2. Store user message
        user_msg = session_service.add_message(db, session_id, MessageCreate(
            role="user", content=content
        ))
        
        # 3. Get conversation context
        history = session_service.get_messages(db, session_id, limit=50)
        
        # 4. Generate AI response with full context
        response_content, tokens = self.get_ai_response(
            db, session_db, content, history[:-1]  # Exclude just-added message
        )
        
        # 5. Store AI response
        ai_msg = session_service.add_message(db, session_id, MessageCreate(
            role="assistant", content=response_content, token_count=tokens
        ))
        
        return Message.model_validate(ai_msg)
```

**Key Points**:
- Coordinate multiple services in a single flow
- Handle errors at each step with descriptive messages
- Maintain transaction consistency
- Pass authentication context through the flow
- Return properly typed responses

### Global Service Instances
Create singleton at module level:
```python
# At bottom of service file
service_name = ServiceName(ModelDB)
```

### Service Import Pattern
**IMPORTANT**: Import service instances, not modules:
```python
# ✅ CORRECT - Import the instance directly
from backend.services.client_service import client_service
from backend.services.session_service import session_service
from backend.services.prompt_service import prompt_service

# Usage
client = client_service.get(db, client_id)
session = session_service.create_session(db, session_data, student_id)

# ❌ WRONG - Don't import modules and access instance
from backend.services import client_service  # This imports module
client_service.client_service.get(db, client_id)  # Too verbose
```

**Special Case - Anthropic Service**:
```python
# Anthropic service uses a factory function pattern
from backend.services.anthropic_service import anthropic_service

# Usage - call the function to get instance
anthropic = anthropic_service()
response = anthropic.generate_response(...)
```

### Access Validation Pattern
Consistent access checking across services:
```python
def validate_student_session_access(self, db: DBSession, session_id: str, student_id: str) -> SessionDB:
    """Validate student has access to session"""
    session = self.get_session(db, session_id)
    
    if not session:
        raise ValueError(f"Session with ID {session_id} not found")
    
    if session.student_id != student_id:
        raise ValueError(f"Student {student_id} does not have access to session {session_id}")
    
    if session.status != "active":
        raise ValueError(f"Session {session_id} is not active")
    
    return session

# Usage in methods
def send_message(self, db: DBSession, session_id: str, content: str, user: StudentAuth) -> Message:
    # Single line validates all access rules
    session = self.validate_student_session_access(db, session_id, user.student_id)
    
    # Continue with business logic...
```

### AI/LLM Service Pattern
Centralized service for all AI interactions:
```python
# backend/services/anthropic_service.py
class AnthropicService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided")
        
        # Initialize both sync and async clients
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        self.model = self._get_model_config()
    
    def _get_model_config(self) -> str:
        """Auto-select model based on environment"""
        environment = os.getenv("APP_ENV", "development")
        model_override = os.getenv("ANTHROPIC_MODEL")  # Allow override
        
        if model_override:
            return model_override
        
        if environment == "production":
            return "claude-3-sonnet-20240229"  # More powerful
        return "claude-3-haiku-20240307"  # Cheaper for dev

# Global singleton pattern
_anthropic_service_instance = None

def get_anthropic_service() -> AnthropicService:
    global _anthropic_service_instance
    if _anthropic_service_instance is None:
        _anthropic_service_instance = AnthropicService()
    return _anthropic_service_instance
```

**Key Features**:
- Environment-based model selection (Haiku for dev, Sonnet for prod)
- Singleton pattern for consistent instance
- Both sync and async support
- Integrated with token counting utility
- Comprehensive error handling

### Retry Pattern for External APIs
Use tenacity for automatic retries on rate limits:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(anthropic.RateLimitError)
)
def generate_response(self, messages, system_prompt=None, max_tokens=500):
    # API call that will retry on rate limits
    response = self.client.messages.create(
        model=self.model,
        messages=messages,
        system=system_prompt,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.content[0].text
```

### AI Service Error Handling Pattern
```python
def test_connection(self) -> Dict[str, Any]:
    try:
        response = self.client.messages.create(...)
        return {
            "status": "connected",
            "model": self.model,
            "environment": self.environment,
            "test_response": response.content[0].text
        }
    except anthropic.APIConnectionError as e:
        return {"status": "error", "error_type": "connection", "error": str(e)}
    except anthropic.AuthenticationError as e:
        return {"status": "error", "error_type": "authentication", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error_type": "unknown", "error": str(e)}
```

### Circuit Breaker Pattern
Prevent cascading failures when external services are down:
```python
class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        
    def can_execute(self) -> Tuple[bool, Optional[str]]:
        if self.state == "closed":
            return True, None
            
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = "half_open"
                return True, None
            return False, f"Service unavailable. Try again in {seconds} seconds."
            
        return True, None  # half_open
        
    def record_success(self):
        if self.state == "half_open":
            # Transition to closed after enough successes
            self.state = "closed"
        self.failure_count = 0
        
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"
```

**Configuration**:
- `ANTHROPIC_FAILURE_THRESHOLD` - Failures before opening (default: 5)
- `ANTHROPIC_RECOVERY_TIMEOUT` - Seconds before retry (default: 300)
- `ANTHROPIC_HALF_OPEN_REQUESTS` - Test requests in recovery (default: 3)

### Cost Tracking Pattern
Track API usage costs with configurable alerts:
```python
class AnthropicService:
    def __init__(self):
        self.cost_alert = CostAlert(
            warning_threshold=float(os.getenv("ANTHROPIC_COST_WARNING", "0.10")),
            critical_threshold=float(os.getenv("ANTHROPIC_COST_CRITICAL", "0.50")),
            daily_limit=float(os.getenv("ANTHROPIC_DAILY_LIMIT", "10.00"))
        )
        self.session_costs: Dict[str, float] = {}
        self.daily_cost = 0.0
        
    def _track_cost(self, session_id: Optional[str], tokens: int, is_input: bool):
        # Calculate cost based on model and token type
        cost = calculate_cost(tokens, self.model, "input" if is_input else "output")
        
        # Update tracking
        self.daily_cost += cost
        if session_id:
            self.session_costs[session_id] = self.session_costs.get(session_id, 0.0) + cost
        
        # Check alerts
        if session_id and self.session_costs[session_id] >= self.cost_alert.critical_threshold:
            logger.critical(f"Session {session_id} exceeds critical cost threshold")
        
        if self.daily_cost >= self.cost_alert.daily_limit:
            self.status = ServiceStatus.UNAVAILABLE
```

### Error Categorization Pattern
Convert technical errors to user-friendly messages:
```python
def _categorize_error(self, error: Exception) -> ErrorType:
    """Categorize by class name for compatibility"""
    error_class_name = error.__class__.__name__
    
    if "AuthenticationError" in error_class_name:
        return ErrorType.AUTHENTICATION
    elif "RateLimitError" in error_class_name:
        return ErrorType.RATE_LIMIT
    elif "APIConnectionError" in error_class_name:
        return ErrorType.CONNECTION
    # ... more mappings
    
def _get_user_friendly_error(self, error_type: ErrorType) -> str:
    messages = {
        ErrorType.AUTHENTICATION: "Authentication failed. Please check your credentials.",
        ErrorType.RATE_LIMIT: "Too many requests. Please wait a moment and try again.",
        ErrorType.CONNECTION: "Unable to connect to the AI service.",
        # ... more messages
    }
    return messages.get(error_type, "An unexpected error occurred.")
```

### Fallback Response Pattern
Provide educational responses when API is unavailable:
```python
def _generate_fallback_response(self, context: str = "") -> str:
    """Generate educational fallback when API unavailable"""
    fallback_responses = [
        "I apologize, but I'm having trouble responding right now. Let's take a moment to reflect on what we've discussed so far.",
        "I seem to be having some difficulty at the moment. Perhaps we could explore this topic from a different angle?",
        # ... more responses
    ]
    
    response = random.choice(fallback_responses)
    if context:
        response += f" {context}"
    return response
```

### Service Health Monitoring Pattern
Track and report service health status:
```python
def get_service_status(self) -> Dict[str, Any]:
    return {
        "status": self.status.value,  # healthy/degraded/unavailable
        "circuit_breaker_state": self.circuit_breaker.state,
        "daily_cost": round(self.daily_cost, 4),
        "daily_limit": self.cost_alert.daily_limit,
        "model": self.model,
        "environment": self.environment,
        "last_error": self.last_error
    }
```

### Comprehensive Error Handling with Circuit Breaker
Implement robust error handling with circuit breaker pattern:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        
    def can_execute(self) -> Tuple[bool, Optional[str]]:
        if self.state == "closed":
            return True, None
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half_open"
                return True, None
            return False, f"Service unavailable. Try again in {seconds} seconds."
        return True, None  # half_open

# Use in service
if not self.circuit_breaker.can_execute()[0]:
    return self._generate_fallback_response()
```

### Cost Tracking and Alerts Pattern
Track API costs with configurable alerts:
```python
@dataclass
class CostAlert:
    warning_threshold: float = 0.10  # $0.10
    critical_threshold: float = 0.50  # $0.50  
    daily_limit: float = 10.00  # $10.00

def _track_cost(self, session_id: Optional[str], tokens: int, is_input: bool = True):
    # Reset daily cost if new day
    current_date = datetime.utcnow().date()
    if current_date > self.cost_reset_date:
        self.daily_cost = 0.0
        self.cost_reset_date = current_date
    
    # Calculate and track cost
    cost = calculate_cost(tokens, self.model, "input" if is_input else "output")
    self.daily_cost += cost
    if session_id:
        self.session_costs[session_id] = self.session_costs.get(session_id, 0.0) + cost
    
    # Check alerts
    if session_id and self.session_costs[session_id] >= self.cost_alert.critical_threshold:
        logger.critical(f"Session {session_id} exceeds critical cost threshold")
    if self.daily_cost >= self.cost_alert.daily_limit:
        self.status = ServiceStatus.UNAVAILABLE
```

### Error Categorization Pattern
Categorize errors for appropriate handling:
```python
def _categorize_error(self, error: Exception) -> ErrorType:
    error_class_name = error.__class__.__name__
    
    if "AuthenticationError" in error_class_name:
        return ErrorType.AUTHENTICATION
    elif "RateLimitError" in error_class_name:
        return ErrorType.RATE_LIMIT
    elif "APIConnectionError" in error_class_name:
        return ErrorType.CONNECTION
    elif "APITimeoutError" in error_class_name:
        return ErrorType.TIMEOUT
    # ... more error types
    return ErrorType.UNKNOWN

# Use categorization for user-friendly messages
error_type = self._categorize_error(e)
user_message = self._get_user_friendly_error(error_type)
```

### Fallback Response Pattern
Provide educational continuity during outages:
```python
def _generate_fallback_response(self, context: str = "") -> str:
    fallback_responses = [
        "I apologize, but I'm having trouble responding right now. Let's take a moment to reflect on what we've discussed so far.",
        "I seem to be having some difficulty at the moment. Perhaps we could explore this topic from a different angle?",
        "I need a moment to gather my thoughts. In the meantime, how are you feeling about our conversation so far?"
    ]
    
    import random
    response = random.choice(fallback_responses)
    if context:
        response += f" {context}"
    return response
```

### Service Health Monitoring Pattern
Monitor and report service health:
```python
class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

def get_service_status(self) -> Dict[str, Any]:
    return {
        "status": self.status.value,
        "circuit_breaker_state": self.circuit_breaker.state,
        "daily_cost": round(self.daily_cost, 4),
        "daily_limit": self.cost_alert.daily_limit,
        "model": self.model,
        "environment": self.environment,
        "last_error": self.last_error
    }
```

**Key Features**:
- Circuit breaker prevents cascading failures
- Cost tracking prevents budget overruns
- Fallback responses maintain educational value
- User-friendly error messages
- Comprehensive health monitoring
- Environment variable configuration

### Conversation Context Management Pattern
Format conversation history for AI while maintaining context:
```python
def _format_conversation_for_ai(
    self,
    messages: list[MessageDB],
    latest_user_message: str
) -> list[Dict[str, str]]:
    """Format messages for Anthropic API format"""
    formatted = []
    
    # Add all historical messages
    for msg in messages:
        formatted.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add the latest user message
    formatted.append({
        "role": "user",
        "content": latest_user_message
    })
    
    return formatted

# Usage: Pass to AI with proper context window
formatted_msgs = self._format_conversation_for_ai(
    messages=history[:-1],  # Exclude the just-added message
    latest_user_message=new_content
)

response = anthropic.generate_response(
    messages=formatted_msgs,
    system_prompt=system_prompt,
    max_tokens=500  # Control response length
)
```

### Service Method Naming
- `get_*` - Retrieve data
- `create_*` - Create new records
- `update_*` - Modify existing records
- `delete_*` - Remove records (hard or soft)
- `can_*` - Permission checks
- `is_*` - Boolean checks
- `publish_*` / `unpublish_*` - State transitions
- `list_*` - Retrieve multiple items with filtering

### Date-Based Filtering Pattern
For resources with availability windows:
```python
def list_available_assignments(self, db: Session, section_ids: List[str], as_of: Optional[datetime] = None):
    if not as_of:
        as_of = datetime.utcnow()
    
    query = db.query(AssignmentDB).filter(
        AssignmentDB.section_id.in_(section_ids),
        AssignmentDB.is_published == True
    )
    
    # Filter by available_from (null or past date)
    query = query.filter(
        (AssignmentDB.available_from == None) | (AssignmentDB.available_from <= as_of)
    )
    
    # Filter by due_date (null or future date) 
    query = query.filter(
        (AssignmentDB.due_date == None) | (AssignmentDB.due_date > as_of)
    )
    
    return query.all()
```

### Business Logic Enforcement
Enforce business rules at the service layer, not just API layer:
```python
# Example: Assignment publishing restrictions
def update(self, db: Session, assignment_id: str, update_data: AssignmentUpdate, teacher_id: str):
    assignment = self.get(db, assignment_id)
    
    # Business rule: Limited updates on published assignments
    if assignment.is_published:
        allowed_updates = {'description', 'due_date', 'max_attempts', 'is_published'}
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Filter out restricted fields
        restricted_updates = set(update_dict.keys()) - allowed_updates
        if restricted_updates:
            logger.warning(f"Cannot update fields {restricted_updates} on published assignment")
            for field in restricted_updates:
                update_dict.pop(field, None)
        
        return super().update(db, assignment_id, **update_dict)
    
    # Draft assignments allow all updates
    return super().update(db, assignment_id, **update_data.model_dump(exclude_unset=True))
```

### Publishing Pattern
For resources with draft/published states:
```python
def publish_item(self, db: Session, item_id: str, user_id: str) -> Optional[ItemDB]:
    # 1. Check permissions
    if not self.can_update(db, item_id, user_id):
        return None
    
    # 2. Validate prerequisites (e.g., required relationships)
    if not self._validate_publishing_requirements(db, item_id):
        return None
    
    # 3. Update state
    item = self.get(db, item_id)
    item.is_published = True
    db.commit()
    db.refresh(item)
    return item

def _validate_publishing_requirements(self, db: Session, item_id: str) -> bool:
    # Check specific requirements
    # e.g., Assignment must have at least one active client
    active_count = db.query(RelatedModel).filter(
        RelatedModel.item_id == item_id,
        RelatedModel.is_active == True
    ).count()
    return active_count > 0
```

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

### MVP/Prototype Testing Pattern

During rapid prototyping phases (like Streamlit MVP):

```python
# One simple integration test per feature
def test_feature_happy_path():
    """Test the core functionality works"""
    # Setup
    data = create_test_data()
    
    # Execute
    result = feature_function(data)
    
    # Verify core behavior
    assert result is not None
    assert result.status == "success"
    # Skip edge cases for MVP

# Document edge cases for later
"""
TODO: After MVP validation, add tests for:
- Empty data handling
- Permission boundaries  
- Concurrent access
- Error scenarios
"""
```

**What NOT to test in MVP:**
- Every error scenario
- UI components (Streamlit internals)
- Permission edge cases
- Performance optimizations
- Every helper function

**What TO test in MVP:**
- Database connectivity
- API authentication works
- Core business logic (e.g., cost calculation)
- Happy path for each major feature

### Service Mocking Pattern
Properly mock services based on their import pattern:

**Standard Service Mocking**:
```python
@pytest.fixture
def mock_dependencies(monkeypatch):
    # Mock service instances directly
    mock_client_service = Mock()
    mock_client_service.get.return_value = mock_client
    
    mock_session_service = Mock()
    mock_session_service.create_session.return_value = mock_session_db
    
    # Apply mocks to the imported instances
    monkeypatch.setattr("backend.services.conversation_service.client_service", mock_client_service)
    monkeypatch.setattr("backend.services.conversation_service.session_service", mock_session_service)
```

**Anthropic Service Mocking** (factory function pattern):
```python
# Mock the instance that will be returned
mock_anthropic_instance = Mock()
mock_anthropic_instance.generate_response.return_value = "AI response"

# Mock the factory function to return the instance
mock_anthropic_service = Mock(return_value=mock_anthropic_instance)

monkeypatch.setattr("backend.services.conversation_service.anthropic_service", mock_anthropic_service)
```

**Mock Objects for Pydantic Validation**:
```python
# When mocking database objects that will be validated by Pydantic,
# include ALL required fields:
from datetime import datetime

mock_session_db = Mock(
    id="session-456",
    student_id="student-123",
    client_profile_id="client-123",
    status="active",
    total_tokens=25,
    estimated_cost=0.0001,
    session_notes=None,  # Include nullable fields
    started_at=datetime.utcnow(),  # Include datetime fields
    ended_at=None
)

# This mock can now be safely passed to Pydantic validation:
# Session.model_validate(mock_session_db)
```

### Floating-Point Comparison Pattern
Use pytest's `approx()` for comparing floating-point values:
```python
from pytest import approx

# ❌ AVOID - Can fail due to precision issues
assert session.estimated_cost == 0.0045

# ✅ CORRECT - Handles floating-point precision
assert session.estimated_cost == approx(0.0045)

# For multiple decimal places
assert cost == approx(0.123456, rel=1e-6)  # Relative tolerance
assert cost == approx(0.123456, abs=1e-6)  # Absolute tolerance
```
**Use for**: Cost calculations, percentages, any floating-point math

### Integration Test Database Setup Pattern
**IMPORTANT**: Always use the standard `db_session` fixture from `conftest.py` for integration tests.

**❌ AVOID** - Creating custom database fixtures:
```python
# DON'T DO THIS - causes threading issues with SQLite
@pytest.fixture(scope="module")
def test_db():
    init_database(":memory:")
    yield
```

**✅ CORRECT** - Use standard fixtures:
```python
def test_endpoint(db_session):  # db_session from conftest.py
    # Your test code here
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

**Benefits**:
- Consistent database setup across all tests
- No SQLite threading issues
- Proper transaction rollback between tests
- Uses ORM-based initialization

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

### Student Assignment Viewing Pattern
Established in Phase 1.5 Part 7:

```python
# Pattern 1: Check all access conditions and return 404 for any failure
async def get_student_assignment(assignment_id: str, student_id: str):
    assignment = assignment_service.get(db, assignment_id)
    
    # Return 404 for ANY of these conditions:
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    
    if not enrollment_service.is_student_enrolled(db, assignment.section_id, student_id):
        raise HTTPException(404, "Assignment not found")  # Same message!
    
    if not assignment.is_published:
        raise HTTPException(404, "Assignment not found")  # Same message!
    
    # Date checks
    now = datetime.utcnow()
    if assignment.available_from and now < assignment.available_from:
        raise HTTPException(404, "Assignment not found")  # Same message!
    
    if assignment.due_date and now > assignment.due_date:
        raise HTTPException(404, "Assignment not found")  # Same message!
    
    return assignment

# Pattern 2: Enrich responses with related data
response_assignments = []
for assignment in assignments:
    assignment_dict = Assignment.model_validate(assignment).model_dump()
    assignment_dict['section_name'] = section_map.get(assignment.section_id)
    
    # Add computed fields
    stats = assignment_service.get_assignment_stats(db, assignment.id)
    assignment_dict['client_count'] = stats['active_clients']
    
    response_assignments.append(Assignment(**assignment_dict))

# Pattern 3: Filter only active relationships for students
active_clients = [client for client in clients if client.is_active]
```

### Implementing Soft Delete

1. Add `is_active` field to model
2. Override delete method to set `is_active = False`
3. Filter queries by `is_active == True`
4. Consider reactivation logic for re-enrollment

---

## 🚀 MVP Development Patterns

### Streamlit Application Structure
```python
# mvp/teacher_test.py
import streamlit as st
import sys
sys.path.append('..')  # Add parent directory to path

from backend.database import get_db
from backend.services.client_service import client_service

# Page config
st.set_page_config(
    page_title="Teacher Test Interface",
    page_icon="🧑‍🏫",
    layout="wide"
)

# Session state initialization
if 'current_teacher' not in st.session_state:
    st.session_state.current_teacher = 'teacher-123'

# Main app logic
def main():
    st.title("Virtual Client Testing")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Create Client", "Test Conversation", "View History"]
    )
    
    if page == "Create Client":
        show_create_client_page()
    elif page == "Test Conversation":
        show_test_conversation_page()
    # ...

if __name__ == "__main__":
    main()
```

### Cost Control Patterns

#### Token Counting on Every Message
```python
# In llm_service.py
import anthropic

def count_tokens(text: str) -> int:
    # Use anthropic's token counter or tiktoken
    # Rough estimate: ~4 characters per token
    return len(text) // 4

def create_message_with_tracking(session_id: str, role: str, content: str):
    token_count = count_tokens(content)
    
    message = MessageDB(
        session_id=session_id,
        role=role,
        content=content,
        token_count=token_count,
        timestamp=datetime.utcnow()
    )
    
    # Update session total
    session.total_tokens += token_count
    session.estimated_cost = calculate_cost(session.total_tokens)
    
    return message
```

#### User-Level Rate Limiting
```python
# Simple in-memory rate limiter for MVP
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests_per_hour=100):
        self.max_requests = max_requests_per_hour
        self.requests = defaultdict(list)
    
    def check_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old requests
        self.requests[user_id] = [
            req for req in self.requests[user_id] 
            if req > hour_ago
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()
```

#### Cost Alerts
```python
# In session_service.py
COST_ALERT_THRESHOLD = 0.10  # Alert at $0.10

def check_cost_alerts(session: SessionDB):
    if session.estimated_cost > COST_ALERT_THRESHOLD:
        logger.warning(
            f"High cost session {session.id}: "
            f"${session.estimated_cost:.3f}"
        )
        # Could send email, Slack notification, etc.
```

### Rate Limiting Patterns

#### Sliding Window Rate Limiter
```python
# backend/utils/rate_limiter.py
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple

class RateLimiter:
    """Sliding window rate limiter with per-user and global limits"""
    
    def __init__(
        self,
        user_limit: int = 10,    # 10 requests per minute per user
        user_window: int = 60,   # 1 minute
        global_limit: int = 1000,  # 1000 requests per hour
        global_window: int = 3600  # 1 hour
    ):
        self.user_limit = user_limit
        self.user_window = user_window
        self.global_limit = global_limit
        self.global_window = global_window
        
        # In-memory storage (replace with Redis for production)
        self._user_requests: Dict[str, deque] = defaultdict(deque)
        self._global_requests: deque = deque()
        
    def check_limit(self, user_id: Optional[str] = None) -> Tuple[bool, Optional[int]]:
        """Check if request is within limits. Returns (allowed, retry_after_seconds)"""
        current_time = time.time()
        
        # Check global limit
        global_allowed, global_retry = self._check_global_limit(current_time)
        if not global_allowed:
            return False, global_retry
        
        # Check user limit if user_id provided
        if user_id:
            user_allowed, user_retry = self._check_user_limit(user_id, current_time)
            if not user_allowed:
                return False, user_retry
        
        # Record the request
        self._record_request(user_id, current_time)
        return True, None
```

#### Rate Limit Decorators
```python
# Flexible decorator with configurable limits
def rate_limit(
    limiter: Optional[RateLimiter] = None,
    get_user_id: Optional[Callable] = None,
    raise_on_limit: bool = True
):
    """Decorator for rate limiting functions"""
    if limiter is None:
        limiter = default_rate_limiter
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = None
            if get_user_id:
                try:
                    user_id = get_user_id(*args, **kwargs)
                except:
                    pass  # Continue without user-specific limit
            
            allowed, retry_after = limiter.check_limit(user_id)
            if not allowed:
                if raise_on_limit:
                    raise RateLimitExceeded(
                        f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        retry_after
                    )
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Convenience decorators
@rate_limit_user  # Expects 'user_id' in kwargs
@rate_limit_student  # Expects 'student_id' in kwargs
```

#### Using Rate Limiting
```python
# Manual checking
from backend.utils import default_rate_limiter

allowed, retry_after = default_rate_limiter.check_limit("user-123")
if not allowed:
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
        headers={"Retry-After": str(retry_after)}
    )

# With decorators
@rate_limit(get_user_id=lambda *args, **kwargs: kwargs.get('user').student_id)
def send_message(db, session_id: str, content: str, user: StudentAuth):
    # Function implementation
    pass

# For API endpoints
@router.post("/messages")
@rate_limit_student
async def create_message(
    message: MessageCreate,
    student_id: str = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Endpoint implementation
    pass
```

#### Environment Variable Configuration
```python
# Configure via environment variables
DEFAULT_USER_LIMIT = int(os.getenv("RATE_LIMIT_USER_PER_MINUTE", "10"))
DEFAULT_GLOBAL_LIMIT = int(os.getenv("RATE_LIMIT_GLOBAL_PER_HOUR", "1000"))

# Usage statistics
usage = limiter.get_user_usage("user-123")
print(f"Requests: {usage['requests_in_window']}/{usage['limit']}")
print(f"Remaining: {usage['remaining']}")
```

#### Testing Rate Limits
```python
# Mock time for testing
@patch('time.time')
def test_sliding_window(mock_time):
    mock_time.return_value = 1000.0  # Set initial time BEFORE creating limiter
    limiter = RateLimiter(user_limit=2, user_window=60)
    
    # Make requests
    assert limiter.check_limit("user1")[0] is True
    assert limiter.check_limit("user1")[0] is True
    assert limiter.check_limit("user1")[0] is False  # 3rd request blocked
    
    # Move time forward
    mock_time.return_value = 1061.0  # 61 seconds later
    assert limiter.check_limit("user1")[0] is True  # Old requests expired

# Extract user_id from positional args
get_user_id=lambda *args, **kwargs: args[1].student_id if len(args) > 1 else None
```

**Key Features**:
- Sliding window algorithm for accurate rate limiting
- Per-user and global limits with different time windows
- Automatic cleanup of old requests
- Retry-after calculation for proper HTTP headers
- Easy migration path to Redis (just replace storage backend)
- Decorators for clean integration
- Usage statistics and monitoring

### Message Storage for Scale

#### Proper Table Design
```sql
-- Messages table designed for 6M+ messages
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    token_count INTEGER NOT NULL,
    sequence_number INTEGER NOT NULL,
    
    -- Indexes for performance
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_session_sequence (session_id, sequence_number),
    
    -- Foreign key
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

#### Pagination for Message History
```python
def get_session_messages(
    db: Session, 
    session_id: str, 
    limit: int = 50,
    offset: int = 0
) -> List[MessageDB]:
    return db.query(MessageDB)\
        .filter(MessageDB.session_id == session_id)\
        .order_by(MessageDB.sequence_number)\
        .limit(limit)\
        .offset(offset)\
        .all()
```

### Anthropic Integration Patterns

#### Client Setup with Retry
```python
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

class AnthropicService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"  # Start with cheapest
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self, 
        system_prompt: str, 
        messages: List[dict]
    ) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                max_tokens=500,  # Control response length
                temperature=0.7
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            logger.error("Rate limit hit")
            raise
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
```

#### System Prompt Generation
```python
def generate_system_prompt(client: ClientProfile) -> str:
    return f"""
You are playing the role of {client.name}, a {client.age}-year-old {client.gender} 
who is {client.race} and from a {client.socioeconomic_status} background.

Background: {client.background_story}

You are experiencing these challenges: {', '.join(client.issues)}

Your personality traits: {', '.join(client.personality_traits)}
Communication style: {client.communication_style}

IMPORTANT RULES:
1. Stay in character at all times
2. Respond as this person would, not as an AI
3. Show the emotional state and challenges naturally
4. Keep responses concise (2-3 sentences usually)
5. This is an educational simulation for social work students
6. Maintain appropriate boundaries for educational context
"""
```

### Streamlit Conversation UI
```python
def show_conversation():
    # Message display
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            st.caption(f"Tokens: {msg['tokens']}")
    
    # Input handling
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "tokens": count_tokens(prompt)
        })
        
        # Generate AI response
        with st.spinner("Client is thinking..."):
            response = generate_client_response(
                st.session_state.current_client,
                st.session_state.messages
            )
        
        # Add AI message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "tokens": count_tokens(response)
        })
        
        # Rerun to update chat
        st.rerun()
```

### MVP Testing Patterns

#### Quick Feedback Collection
```python
# In Streamlit sidebar
with st.sidebar:
    st.subheader("Quick Feedback")
    
    quality = st.slider(
        "Conversation Quality",
        min_value=1,
        max_value=10,
        value=7
    )
    
    if st.button("Submit Feedback"):
        feedback = {
            "session_id": st.session_state.session_id,
            "quality_score": quality,
            "timestamp": datetime.utcnow(),
            "user_id": st.session_state.current_user
        }
        save_feedback(feedback)
        st.success("Thanks for your feedback!")
```

#### Session Monitoring
```python
# admin_monitor.py
def show_active_sessions():
    sessions = get_active_sessions()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Sessions", len(sessions))
    col2.metric("Messages/min", calculate_message_rate())
    col3.metric("Avg Response Time", f"{avg_response_time:.1f}s")
    col4.metric("Total Cost Today", f"${daily_cost:.2f}")
    
    # Live session feed
    for session in sessions:
        with st.expander(f"Session {session.id[:8]}..."):
            st.write(f"Student: {session.student_id}")
            st.write(f"Client: {session.client_name}")
            st.write(f"Messages: {session.message_count}")
            st.write(f"Cost: ${session.estimated_cost:.3f}")
```

### Deployment Patterns

#### Environment Variables
```python
# .env file for local development
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./virtual_client.db
ENVIRONMENT=development
MAX_TOKENS_PER_SESSION=10000
RATE_LIMIT_PER_HOUR=100

# Load in app
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    st.error("Please set ANTHROPIC_API_KEY in .env file")
    st.stop()
```

#### Streamlit Cloud Config
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 10
enableCORS = false
```

### MVP Utilities Pattern
Centralize all common Streamlit functionality in a shared utils module:

```python
# mvp/utils.py
import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import text  # Required for raw SQL queries
from backend.services.database import db_service
from backend.models.auth import TeacherAuth, StudentAuth

# Database connection for Streamlit
def get_database_connection() -> Session:
    """Get a fresh database session for Streamlit apps"""
    return db_service.SessionLocal()

# Mock authentication for MVP
def get_mock_teacher() -> TeacherAuth:
    return TeacherAuth(id="teacher-1", teacher_id="teacher-1")

def get_mock_student() -> StudentAuth:
    return StudentAuth(id="student-1", student_id="student-1")

# Standardized page configuration
def setup_page_config(page_title: str = "Virtual Client MVP", 
                      page_icon: str = "🎓", 
                      layout: str = "wide"):
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )

# UI helper functions
def show_error_message(message: str):
    st.error(f"❌ {message}")

def show_success_message(message: str):
    st.success(f"✅ {message}")

# Cost and token formatting
def format_cost(cost: float) -> str:
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.00:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"

def format_tokens(tokens: int) -> str:
    return f"{tokens:,}" if tokens >= 1000 else str(tokens)

# Model pricing constants
DEFAULT_MODEL = "claude-3-haiku-20240307"
MODEL_COSTS = {
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}
}
```

**Key Features**:
- Consistent database connections for Streamlit
- Mock authentication that matches actual auth models
- Standardized UI components and messages
- Centralized cost/token formatting
- Model pricing configuration

### Streamlit Session State Pattern
Initialize session state consistently across all MVP pages:

```python
def initialize_session_state() -> None:
    """Initialize common session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.total_cost = 0.0
        st.session_state.total_tokens = 0
```

### Streamlit Form Validation Pattern
Validate form inputs within Streamlit's form context:

```python
def create_client_form():
    """Create form with validation"""
    with st.form("client_form", clear_on_submit=True):
        # Input fields
        name = st.text_input("Name*", placeholder="e.g., Maria Rodriguez")
        personality_traits = st.multiselect("Traits", PERSONALITY_TRAITS)
        
        submitted = st.form_submit_button("Create Client", type="primary")
        
        if submitted:
            # Validation checks
            if not name:
                show_error_message("Name is required")
                return None
            
            if len(personality_traits) < 2:
                show_error_message("Please select at least 2 personality traits")
                return None
            
            # Create and return validated data
            return ClientProfileCreate(name=name, personality_traits=personality_traits)
    
    return None
```

**Key Points**:
- Use `clear_on_submit=True` to reset form after successful submission
- Return `None` for validation failures
- Show clear error messages using standardized UI helpers
- Validate before creating Pydantic models

### Streamlit Data Display Pattern
Display lists of items in a responsive grid layout:

```python
def display_client_list(teacher_id: str):
    """Display clients in a grid with expandable details"""
    try:
        db = get_database_connection()
        clients = client_service.get_teacher_clients(db, teacher_id)
        
        if not clients:
            show_info_message("No clients created yet. Create your first client above!")
            return
        
        # Display in 2-column grid
        for i in range(0, len(clients), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(clients):
                    client = clients[i + j]
                    with col:
                        # Display client card
                        st.markdown(f"### {client.name}")
                        st.write(f"**Age:** {client.age}")
                        
                        # Expandable details
                        with st.expander("View Full Details"):
                            # Show complete information
                            pass
                        
                        # Action buttons
                        if st.button(f"Test", key=f"test_{client.id}"):
                            st.session_state.selected_client_id = client.id
    
    except Exception as e:
        show_error_message(f"Error loading clients: {str(e)}")
    finally:
        db.close()
```

**Key Points**:
- Always use try/except/finally for database operations
- Use unique keys for buttons in loops (`key=f"test_{client.id}"`)
- Display summary information with expandable details
- Store selections in session state for cross-page access

### Streamlit Tab Organization Pattern
Organize related features using tabs:

```python
def main():
    st.title("Teacher Interface")
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs(["Create Client", "Test Conversations", "View History"])
    
    with tab1:
        # Feature 1 implementation
        client_data = create_client_form()
        if client_data:
            # Handle form submission
            pass
    
    with tab2:
        # Feature 2 placeholder
        show_info_message("Coming in next part!")
    
    with tab3:
        # Feature 3 placeholder
        show_info_message("Coming soon!")
```

**Benefits**:
- Clean organization of related features
- Easy navigation without page reloads
- Progressive implementation (add features to tabs incrementally)
- Clear visual separation of functionality

### SQL Query Pattern for Streamlit
Always use `text()` for raw SQL queries in newer SQLAlchemy versions:

```python
from sqlalchemy import text

# ❌ WRONG - Causes error in SQLAlchemy 2.0+
result = db.execute("SELECT COUNT(*) FROM client_profiles")

# ✅ CORRECT - Explicitly declare as text
result = db.execute(text("SELECT COUNT(*) FROM client_profiles"))
```

### MVP Testing Pattern
Test MVP utilities without creating separate test scripts:

```python
# tests/unit/test_mvp_utils.py
class TestMVPUtils:
    def test_get_database_connection(self):
        db = get_database_connection()
        assert isinstance(db, Session)
        db.close()  # Clean up
    
    def test_format_cost(self):
        assert format_cost(0.0001) == "$0.0001"  # 4 decimals < $0.01
        assert format_cost(0.123) == "$0.123"    # 3 decimals < $1.00
        assert format_cost(10.50) == "$10.50"    # 2 decimals >= $1.00

# tests/integration/test_mvp_setup.py
class TestMVPIntegration:
    def test_mvp_directory_structure(self):
        mvp_path = project_root / "mvp"
        required_files = [
            "__init__.py", "utils.py", "test_streamlit.py",
            "teacher_test.py", "student_practice.py", "admin_monitor.py"
        ]
        for filename in required_files:
            assert (mvp_path / filename).exists()
```

### Streamlit UI Testing Challenges
Streamlit's architecture makes traditional unit testing difficult. Use these approaches:

**1. Business Logic Testing** - Test logic separately from UI:
```python
# Instead of testing Streamlit components, test the logic
class TestTeacherInterfaceLogic:
    def test_personality_traits_validation_logic(self):
        traits = ["anxious", "cooperative"]
        assert 2 <= len(traits) <= 5  # Valid range
        
    def test_client_data_transformation(self):
        form_data = {"name": "Test", "age": 30, "personality_traits": ["anxious", "cooperative"]}
        client = ClientProfileCreate(**form_data)
        assert client.name == "Test"
```

**2. Integration Testing** - Test database operations and service calls:
```python
# Test the actual service integration
def test_create_client_full_flow(db_session, teacher):
    client_data = ClientProfileCreate(name="Test Client", age=30, personality_traits=["anxious", "cooperative"])
    created = client_service.create_client_for_teacher(db_session, client_data, teacher.teacher_id)
    assert created.id is not None
```

**3. Manual Testing** - For UI-specific features:
- Run the Streamlit app locally
- Test form validation visually
- Verify layout and responsiveness
- Check error message display

**Recommendation**: Focus on integration tests for Streamlit apps - they provide better coverage than attempting to mock Streamlit components.

### Streamlit Conversation Interface Pattern
Implement real-time chat interface with session state management:

```python
def manage_conversation_state():
    """Initialize conversation-specific session state"""
    if 'conversation_active' not in st.session_state:
        st.session_state.conversation_active = False
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = []
    if 'conversation_cost' not in st.session_state:
        st.session_state.conversation_cost = 0.0
    if 'conversation_tokens' not in st.session_state:
        st.session_state.conversation_tokens = 0

# Start conversation
if st.button("🚀 Start Test Conversation", type="primary"):
    try:
        db = get_database_connection()
        session = conversation_service.start_conversation(
            db=db,
            student=mock_student,
            client_id=st.session_state.selected_client_id
        )
        
        # Update session state
        st.session_state.conversation_active = True
        st.session_state.current_session_id = session.id
        
        # Get initial greeting from messages
        messages = session_service.get_messages(db, session.id)
        if messages:
            for msg in messages:
                st.session_state.conversation_messages.append({
                    'role': msg.role,
                    'content': msg.content,
                    'tokens': msg.token_count
                })
        
        st.rerun()
    finally:
        db.close()

# Display messages
for msg in st.session_state.conversation_messages:
    render_chat_message(
        role=msg['role'],
        content=msg['content'],
        tokens=msg.get('tokens')
    )

# Message input with form to handle submission
with st.form("message_form", clear_on_submit=True):
    user_input = st.text_area("Your message:", height=100)
    send_button = st.form_submit_button("Send", type="primary")
    
    if send_button and user_input:
        # Process message...
        st.rerun()  # Refresh to show new message
```

**Key Points**:
- Use session state for conversation persistence
- Always use try/finally for database connections
- Use st.rerun() to refresh UI after state changes
- Forms with clear_on_submit for input handling
- Store messages in session state for display

### Environment-Aware Error Messages Pattern
Provide helpful context-specific error messages:

```python
def handle_conversation_error(e: Exception) -> None:
    """Show user-friendly error messages based on error type"""
    error_msg = str(e)
    
    if "ANTHROPIC_API_KEY" in error_msg:
        show_error_message(
            "Anthropic API key not configured. Please set the ANTHROPIC_API_KEY "
            "environment variable to enable conversations."
        )
    elif "invalid x-api-key" in error_msg:
        show_error_message(
            "Invalid API key. Please check your ANTHROPIC_API_KEY configuration."
        )
    elif "rate limit" in error_msg.lower():
        show_error_message(
            "Rate limit exceeded. Please wait a moment and try again."
        )
    elif "connection" in error_msg.lower():
        show_error_message(
            "Unable to connect to the AI service. Please check your internet connection."
        )
    else:
        show_error_message(f"An error occurred: {error_msg}")
```

### Session Metrics Display Pattern
Display real-time conversation metrics:

```python
def display_conversation_metrics():
    """Show conversation statistics in columns"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.session_state.conversation_active:
            st.write(f"**Session ID:** {st.session_state.current_session_id[:8]}...")
        else:
            st.write("**Status:** No active conversation")
    
    with col2:
        # Additional status info
        pass
    
    with col3:
        if st.session_state.conversation_active:
            st.metric("Total Tokens", format_tokens(st.session_state.conversation_tokens))
            st.metric("Est. Cost", format_cost(st.session_state.conversation_cost))
```

### Test Skip Pattern for API Dependencies
Skip tests gracefully when external dependencies are unavailable:

```python
import os
import pytest

# Check for API key availability
HAS_ANTHROPIC_API_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))

@pytest.mark.skipif(not HAS_ANTHROPIC_API_KEY, reason="Anthropic API key not configured")
class TestConversationIntegration:
    """Tests requiring Anthropic API"""
    def test_start_conversation(self, db_session, student, test_client):
        # Test with real API
        pass

# Alternative: Test specific error handling
@pytest.mark.skipif(HAS_ANTHROPIC_API_KEY, reason="Skip error tests when API key is available")
def test_conversation_error_handling_no_api_key(db_session, student, test_client):
    """Test graceful handling when no API key"""
    with pytest.raises(RuntimeError, match="Failed to generate AI greeting"):
        conversation_service.start_conversation(db=db_session, student=student, client_id=test_client.id)

# Always run: Test UI logic without API
class TestConversationUILogic:
    """Test UI logic without requiring API"""
    def test_session_state_management(self):
        # Test state transitions
        pass
```

### Service Import Correction Pattern
When services use direct attribute access instead of methods:

```python
# If seeing AttributeError: 'ConversationService' object has no attribute 'session_service'
# The service is accessing session_service directly, not as a method

# In conversation_service.py:
from backend.services.session_service import session_service  # Import the instance

class ConversationService:
    def send_message(self, ...):
        # Direct access to imported service instance
        messages = session_service.get_messages(db, session_id)
        # NOT: self.session_service.get_messages()

# In tests, mock the imported instance:
from backend.services import session_service as session_service_module
monkeypatch.setattr(session_service_module, "get_messages", mock_get_messages)
```

### Conversation Flow Error Handling Pattern
Handle errors at each step of complex flows:

```python
def start_conversation_with_greeting(db, student, client_id):
    try:
        # Step 1: Validate client exists
        client = client_service.get(db, client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Step 2: Create session
        session = session_service.create_session(...)
        
        # Step 3: Generate AI greeting
        try:
            greeting = anthropic.generate_response(...)
        except Exception as e:
            # Clean up session if AI fails
            session_service.delete(db, session.id)
            raise RuntimeError(f"Failed to generate AI greeting: {str(e)}")
        
        # Step 4: Store greeting
        session_service.add_message(...)
        
        return session
        
    except ValueError as e:
        # Domain errors - pass through
        raise
    except Exception as e:
        # Unexpected errors - wrap with context
        raise RuntimeError(f"Failed to start conversation: {str(e)}")
```

**Key Points**:
- Validate prerequisites before creating resources
- Clean up partially created resources on failure
- Distinguish between expected errors (ValueError) and unexpected ones
- Provide context in error messages
- Use specific error types for different failure modes

### Data Export Pattern
Provide downloadable exports of data in user-friendly formats:

```python
def format_conversation_export(conversation: Dict[str, Any]) -> str:
    """Format conversation data for export as markdown"""
    session = conversation['session']
    client = conversation['client']
    messages = conversation.get('messages', [])
    
    # Build structured markdown
    export_lines = [
        f"# Conversation Export",
        f"\n## Session Information",
        f"- **Session ID**: {session.id}",
        f"- **Client**: {client.name}",
        f"- **Started**: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Total Tokens**: {format_tokens(session.total_tokens or 0)}",
        f"- **Estimated Cost**: {format_cost(session.estimated_cost or 0.0)}",
        f"\n## Client Profile",
        # ... client details
        f"\n## Conversation Transcript\n"
    ]
    
    # Add timestamped messages
    for msg in messages:
        timestamp = msg.timestamp.strftime('%H:%M:%S')
        role = "Student" if msg.role == "user" else "Client"
        tokens_info = f" ({msg.token_count} tokens)" if msg.token_count else ""
        
        export_lines.extend([
            f"**[{timestamp}] {role}**{tokens_info}:",
            f"{msg.content}",
            ""  # Empty line for readability
        ])
    
    return "\n".join(export_lines)

# In Streamlit UI
export_text = format_conversation_export(conversation_data)
st.download_button(
    label="📥 Export Conversation",
    data=export_text,
    file_name=f"conversation_{client.name.replace(' ', '_')}_{timestamp}.md",
    mime="text/markdown",
    key=f"export_{session.id}"  # Unique key for button
)
```

**Key Features**:
- Use markdown for readability and compatibility
- Include all relevant metadata (IDs, timestamps, costs)
- Structure data hierarchically (session → client → messages)
- Add timestamps and token counts to messages
- Use descriptive filenames with sanitized client names
- Unique keys for download buttons in loops

**Export Formats by Use Case**:
- **Conversations**: Markdown (human-readable, preserves formatting)
- **Data Tables**: CSV (Excel-compatible, easy analysis)
- **Reports**: PDF (professional, print-ready)
- **Configurations**: JSON (machine-readable, re-importable)

---

*This patterns guide is a living document. Update it when establishing new patterns or improving existing ones.*