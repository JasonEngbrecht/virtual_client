# Current Sprint: Phase 1.5 - Assignment Management

## 📍 Session Handoff
**Last Updated**: 2025-05-25 (Updated breakdown)
**Last Completed**: Phase 1.4 Part 8 - Testing & Documentation ✅
**Ready to Start**: Phase 1.5 Part 1 - Assignment Database Models
**Tests Passing**: All tests passing ✅ (171 total - 151 from test suite + 20 new client tests)
**Notes for Next Session**: 
- Phase 1.4 fully complete with comprehensive documentation
- Missing client API tests from Phase 1.2 have been added
- 81% overall code coverage achieved
- All patterns documented and ready for reuse
- Phase 1.5 has been broken into 8 testable parts (similar to Phase 1.4)
- PROJECT_ROADMAP.md updated with detailed breakdown

## 📍 Where We Are in the Journey
- **Previous Phase**: 1.4 Course Section Management ✅ (All 8 parts complete)
- **Current Phase**: 1.5 Assignment Management (Starting)
- **Overall Progress**: ~63% of Phase 1 complete (14.75 of 23 hours minimum)
- **See**: [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) for full context

**Status**: Not Started | **Estimated Time**: 4-5 hours

## 🎯 Sprint Goal
Implement assignment management within course sections, allowing teachers to create assignments that link clients and rubrics, with support for both practice and graded modes.

## 📋 Planned Tasks

### Part 1: Assignment Database Models (30-40 min)
- [ ] Create `backend/models/assignment.py`
- [ ] Define `AssignmentDB` model with core fields
- [ ] Create Pydantic schemas (AssignmentCreate, AssignmentUpdate, Assignment)
- [ ] Write unit tests for model validation

### Part 2: Assignment-Client Junction Model (30-40 min)
- [ ] Add `AssignmentClientDB` model to assignment.py
- [ ] Implement soft delete support (is_active)
- [ ] Create Pydantic schemas (AssignmentClientCreate, AssignmentClient)
- [ ] Write unit tests for junction relationships

### Part 3: Assignment Service Core (30-40 min)
- [ ] Create `backend/services/assignment_service.py` with basic CRUD
- [ ] Add teacher permission checks (can_update, can_delete)
- [ ] Implement create_assignment_for_teacher method
- [ ] Write unit tests for service methods

### Part 4: Assignment Teacher Endpoints (30-40 min)
- [ ] Add assignment CRUD to teacher routes
- [ ] Implement list/create/read/update/delete endpoints
- [ ] Add response models and validation
- [ ] Write integration tests

### Part 5: Assignment Publishing (25-35 min)
- [ ] Add publishing/unpublishing endpoints
- [ ] Implement date validation logic
- [ ] Add draft vs published filtering
- [ ] Write tests for state transitions

### Part 6: Assignment-Client Management (35-45 min)
- [ ] Add endpoints for managing assignment clients
- [ ] Implement add/remove client with rubric
- [ ] Add bulk operations support
- [ ] Write integration tests

### Part 7: Student Assignment Viewing (30-40 min)
- [ ] Add student endpoints for assignments
- [ ] Filter by enrollment and publish status
- [ ] Show only date-appropriate assignments
- [ ] Write integration tests

### Part 8: Testing & Documentation (30-40 min)
- [ ] Run full test suite
- [ ] Fix any regressions
- [ ] Update API documentation
- [ ] Create phase summary

## 🔧 Technical Requirements

### Database Schema
```sql
-- assignments table
CREATE TABLE assignments (
    id VARCHAR PRIMARY KEY,
    section_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) DEFAULT 'practice', -- 'practice' or 'graded'
    settings JSON,
    available_from TIMESTAMP,
    due_date TIMESTAMP,
    is_published BOOLEAN DEFAULT FALSE,
    max_attempts INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES course_sections(id)
);

-- assignment_clients table (junction)
CREATE TABLE assignment_clients (
    id VARCHAR PRIMARY KEY,
    assignment_id VARCHAR NOT NULL,
    client_id VARCHAR NOT NULL,
    rubric_id VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (client_id) REFERENCES client_profiles(id),
    FOREIGN KEY (rubric_id) REFERENCES evaluation_rubrics(id),
    UNIQUE(assignment_id, client_id)
);
```

### Key Features to Implement
1. **Assignment Types**: Practice vs Graded modes
2. **Publishing**: Draft vs Published states
3. **Scheduling**: Available from/due dates
4. **Attempts**: Configurable max attempts
5. **Client Pool**: Multiple clients per assignment
6. **Rubric Flexibility**: Different rubric per client

## ⚠️ Key Patterns to Follow

From Phase 1.4:
- **Service Composition**: Combine services in routes
- **Teacher Isolation**: Filter by section ownership
- **Soft Delete**: For assignment-client associations
- **Efficient Queries**: Avoid N+1 problems
- **Permission Checks**: Use section_service.can_update()

## 🧪 Testing Strategy

### Unit Tests
- Assignment model validation
- Service method isolation
- Business rule enforcement

### Integration Tests  
- Full CRUD workflows
- Permission boundaries
- Date/time filtering
- Student access control

### Test Scenarios
1. Create assignment with multiple clients
2. Update assignment (published vs draft)
3. Student can only see published assignments
4. Respect enrollment and date filters
5. Handle timezone considerations

## ✅ Definition of Done
- [ ] All 6 parts implemented
- [ ] All tests passing (maintain 80%+ coverage)
- [ ] API documentation updated
- [ ] Phase summary created
- [ ] Ready for Phase 1.6 (Session Management)

## 📚 Quick Reference
- **Models**: See `course_section.py` for similar patterns
- **Services**: Copy structure from `section_service.py`
- **Routes**: Follow patterns in `teacher_routes.py`
- **Tests**: Use fixtures from `test_section_api.py`

---

# Previous Sprint: Phase 1.4 Course Section Management ✅

## Summary
Successfully implemented course sections with enrollments, student access, and statistics across 8 parts:

1. **Database Models** (25 min) - Section and enrollment tables
2. **Section Service** (30 min) - CRUD with permissions  
3. **Section Endpoints** (45 min) - Teacher section management
4. **Enrollment Service** (45 min) - Smart enrollment logic
5. **Enrollment Endpoints** (45 min) - Roster management
6. **Student Access** (45 min) - Read-only student views
7. **Statistics** (35 min) - Efficient count queries
8. **Testing & Documentation** (45 min) - 171 total tests

**Key Achievements**:
- 15 new API endpoints
- 171 tests (including 20 added client tests)
- 81% code coverage
- Comprehensive documentation
- All security boundaries enforced

**Patterns Established**:
- Soft delete with reactivation
- Teacher isolation at service layer
- Student 404s for security
- Efficient SQL aggregation
- Service composition in routes

See [`docs/completed/phase-1-4-section-management.md`](docs/completed/phase-1-4-section-management.md) for full details.