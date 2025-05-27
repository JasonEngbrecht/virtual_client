# Current Sprint: MVP - Minimum Viable Conversation

## 📍 Session Handoff
**Last Updated**: 2025-01-31 19:30
**Last Completed**: Day 3 Part 3: Conversation Handler Service - ALL methods fully implemented and tested ✅
**Ready to Start**: Day 3 Part 4: Rate Limiting
**Tests Passing**: All tests passing ✅ (494 tests total - added 25 new tests: 18 unit + 7 integration)
**Notes for Next Session**: 
- Successfully implemented all conversation methods: `send_message`, `get_ai_response`, `end_conversation`, and helpers
- Fixed session service end_session signature issue (needed student_id parameter)
- Full conversation flow working from start to end with proper access control
- Token counting and cost tracking integrated throughout
- Conversation context properly maintained for AI responses
- Key patterns established: error handling, access validation, proper mocking
- Ready to add rate limiting to prevent abuse

**Agreed Implementation Plan for Day 3**:
Breaking Anthropic Integration into 5 manageable parts:
1. **Part 1: Anthropic API Setup** - Create service, config, test connection
2. **Part 2: Prompt Generation** - Convert client profiles to system prompts
3. **Part 3: Conversation Handler** - Integrate session, messages, and AI
4. **Part 4: Rate Limiting** - Per-user and global limits
5. **Part 5: Error Handling** - Graceful fallbacks and logging

## 📍 Where We Are in the Journey
- **Previous Phase**: 1.5 Assignment Management ✅ (All parts complete)
- **Current Phase**: MVP - Minimum Viable Conversation
- **Foundation Progress**: 17.25 hours of CRUD infrastructure complete
- **See**: [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) for updated vision

**Status**: Starting | **Target**: 1 week sprint | **Success Metric**: Working conversations

## 🎯 Sprint Goal
Build a minimal but functional conversation system to validate the core experience with real teachers and students. Get feedback on AI conversation quality before building more infrastructure.

## 📊 Success Metrics for Week 1
- ✅ 10+ test conversations completed
- ✅ API cost under $0.01 per conversation
- ✅ 80%+ positive feedback on conversation quality
- ✅ Clear list of improvements for Phase 2
- ✅ 5+ teachers have tested the system

## 📋 Week 1 Daily Tasks

### Day 1-2: Simplified Session & Message Models
**Goal**: Create minimal but scalable conversation tracking

#### Work Breakdown (6 Parts - Test After Each):

**Part 1: Update Session Model** ✅
- [x] Remove: `rubric_id`, `evaluation_result_id`, `messages` JSON column
- [x] Add: `total_tokens`, `estimated_cost`
- [x] Change `is_active` to `status` (active/completed)
- [x] Update Pydantic schemas to match
- [x] **Test**: Ensure existing tests still pass (All 317 tests passing)

**Additional work completed**:
- Fixed all legacy rubric tests that referenced session.rubric_id
- Updated rubric service to check assignment-client relationships instead
- Created 18 comprehensive tests for the updated session model
- Fixed import errors by removing Message and SendMessageResponse from exports

**Part 2: Create Message Model** ✅
- [x] Create new `message.py` with `MessageDB` table
- [x] Fields: id, session_id, role, content, timestamp, token_count, sequence_number
- [x] Create Pydantic schemas (MessageCreate, Message)
- [x] Add to model registry (`__init__.py`)
- [x] **Test**: Simple model instantiation test (8 comprehensive tests created)

**Part 3: Database Migration** ✅
- [x] Update database initialization to create messages table
- [x] Ensure foreign key relationships work
- [x] Use SQLite for local development (PostgreSQL when deploying to Railway)
- [x] **Test**: Database creation with both tables

**Additional work completed**:
- Created ORM-based database initialization (`backend/scripts/init_db_orm.py`)
- Created 12 comprehensive tests for database migration
- Fixed conftest.py to import MessageDB model
- Updated sample_session fixture to use new fields
- Fixed integration test database initialization issues:
  - Updated test_section_api.py to use standard db_session fixture
  - Updated test_client_api.py to use standard db_session fixture
  - Removed module-scoped test_db fixtures causing threading issues
  - All 343 tests now passing

**Part 4: Basic Session Service** ✅
- [x] Create `session_service.py` with basic CRUD
- [x] Methods: create_session, get_session, end_session
- [x] Follow existing service patterns
- [x] **Test**: Basic session creation/retrieval (20 tests created, all passing)

**Additional work completed**:
- Implemented student validation (students can only access their own sessions)
- Added get_student_sessions() with status filtering and pagination
- Added get_active_session() to find active sessions for student-client pairs
- Added update_token_count() for tracking API usage and costs
- Fixed floating-point precision issues in tests using pytest.approx()
- Comprehensive test coverage including edge cases and permissions

**Part 5: Message Operations** ✅
- [x] Add to session service: add_message, get_messages
- [x] Implement pagination for message history
- [x] Maintain sequence numbers
- [x] **Test**: Message creation and retrieval (17 tests created, all passing)

**Part 6: Token Counting** ✅
- [x] Add token counting utility function
- [x] Integrate into message creation
- [x] Update session totals on each message
- [x] Add cost calculation (Haiku: $0.003/conv, Sonnet: $0.03/conv)
- [x] **Test**: Token counting accuracy (29 tests created, all passing)

**Additional work completed**:
- Created dedicated utils package with token_counter.py module
- Implemented character-based token estimation (4 chars ≈ 1 token)
- Added support for multiple pricing models with easy configuration
- Automatic token counting for messages without explicit counts
- Both user and assistant messages now contribute to session totals
- Cost formatting utilities for display
- Comprehensive test coverage including edge cases

### Day 3: Anthropic Integration
**Goal**: Connect AI and start generating responses

#### Detailed Implementation Plan (5 Parts):

**Part 1: Anthropic API Setup** ✅
- [x] Create `backend/services/anthropic_service.py`
- [x] Set up API client with configuration
- [x] Add environment variable handling for API key (ANTHROPIC_API_KEY)
- [x] Create basic test connection method
- [x] Add configuration for model selection (Haiku for testing, Sonnet for production)
- [x] **Test**: Basic API connection and response (21 unit tests, 7 integration tests)

**Part 2: Prompt Generation Service** ✅
- [x] Create `backend/services/prompt_service.py`
- [x] Implement `generate_system_prompt(client: ClientProfile) -> str`
  ```python
  def generate_system_prompt(client: ClientProfile) -> str:
      # Convert profile attributes to personality instructions
      # Include context, background, behavior patterns
      # Add educational safeguards
      # Set conversation boundaries
  ```
- [x] Include personality traits from client profile
- [x] Add educational context and boundaries
- [x] Create prompt templates for consistency
- [x] **Test**: Generate prompts for various client types (24 tests created)

**Part 3: Conversation Handler Service** ✅ COMPLETE
- [x] Create `backend/services/conversation_service.py` - All methods implemented ✅
- [x] Integrate with session_service, anthropic_service, and prompt_service ✅
- [x] Methods implemented:
  - [x] `start_conversation(student_id, client_id) -> Session` ✅
  - [x] `send_message(session_id, content, user) -> Message` ✅
  - [x] `get_ai_response(session, user_message) -> Message` ✅
  - [x] `end_conversation(session_id, user) -> Session` ✅
  - [x] `_format_conversation_for_ai()` - Helper method ✅
  - [x] `_calculate_cost()` - Helper method ✅
- [x] Handle message flow for initial greeting (user input → AI response → storage) ✅
- [x] Automatic token counting and cost tracking via existing utilities ✅
- [x] Maintain conversation context (for ongoing messages) ✅
- [x] **Test**: 26 unit tests + 12 integration tests - ALL PASSING ✅

**Part 4: Rate Limiting**
- [ ] Add rate limiting utilities in `backend/utils/rate_limiter.py`
- [ ] Implement per-user limits (e.g., 10 messages/minute)
- [ ] Implement global limits (e.g., 1000 messages/hour)
- [ ] Use in-memory storage for MVP (prepare for Redis later)
- [ ] Add decorators for easy application
- [ ] **Test**: Rate limiting under various scenarios

**Part 5: Error Handling & Robustness**
- [ ] Add comprehensive error handling to anthropic_service
- [ ] Implement retry logic with exponential backoff
- [ ] User-friendly error messages for common failures
- [ ] Fallback responses for API outages
- [ ] Logging for debugging and monitoring
- [ ] Cost alerts when approaching limits
- [ ] **Test**: Error scenarios and recovery

#### Original Task List (for reference):
- [ ] Set up Anthropic API connection
- [ ] Create prompt generation from client profiles
- [ ] Implement token counting on all API calls
- [ ] Add rate limiting (per user and global)
- [ ] Create conversation handler service
- [ ] Test with various client personalities
- [ ] Add error handling and fallbacks

### Day 4-5: Streamlit Prototype
**Goal**: Minimal UI for testing conversations

#### Teacher Interface (`teacher_test.py`)
- [ ] Simple form to create/edit one client
- [ ] Test conversation with created client
- [ ] View conversation history
- [ ] See token usage/costs

#### Student Interface (`student_practice.py`)
- [ ] List available clients (from existing data)
- [ ] Start conversation button
- [ ] Chat interface with message history
- [ ] End session and save

#### Admin Dashboard (`admin_monitor.py`)
- [ ] Real-time token usage
- [ ] Cost tracking
- [ ] Active sessions monitor
- [ ] Error logs

### Day 6-7: Testing & Iteration
**Goal**: Get real feedback and iterate quickly

- [ ] Deploy to Railway when ready for external testers (~$10-20/month)
- [ ] Recruit 5-10 teachers for testing
- [ ] Create feedback form
- [ ] Monitor all conversations
- [ ] Track costs and performance
- [ ] Daily standup on findings
- [ ] Quick fixes based on feedback
- [ ] Document all learnings

## 🔧 Technical Decisions for MVP

### Architecture Choices
1. **Database**: SQLite for local development, PostgreSQL when deploying to Railway
2. **Messages**: Separate table from day 1 (no JSON blobs)
3. **API**: Use Anthropic Claude Haiku for testing ($0.003/conversation)
4. **UI**: Streamlit for rapid iteration
5. **Deployment**: Local development first, Railway when ready for external testing (~$10-20/month)

### What We're NOT Building Yet
- Complex session state management
- Assignment mode vs practice mode
- Rubric evaluation
- Teacher monitoring tools
- Student progress tracking
- Section management integration

### What We ARE Validating
- Conversation quality
- Client personality consistency
- API costs at scale
- Response time
- Basic user experience
- Technical feasibility

## 🧪 Testing Strategy

### Conversation Quality Tests
- Do clients stay in character?
- Are responses appropriate for educational context?
- Is the difficulty level right?
- Do students find it helpful?

### Technical Tests
- Message storage performance
- Token counting accuracy
- API error handling
- Concurrent user support

### User Experience Tests
- Time to start conversation
- Clarity of interface
- Mobile responsiveness
- Error message quality

## 📈 Daily Tracking

### Day 1 (Date: ______)
- [ ] Sessions created: ___
- [ ] Messages stored: ___
- [ ] Tokens used: ___
- [ ] Cost: $___
- [ ] Issues found: 

### Day 2 (Date: ______)
- [ ] Sessions created: ___
- [ ] Messages stored: ___
- [ ] Tokens used: ___
- [ ] Cost: $___
- [ ] Issues found:

[Continue for each day...]

## 🚀 Deployment Checklist

### Before Teacher Testing
- [ ] Anthropic API key configured
- [ ] Rate limiting tested
- [ ] Error messages user-friendly
- [ ] Feedback form ready
- [ ] Cost alerts set up

### Before Student Testing  
- [ ] Teacher approved client quality
- [ ] Performance tested
- [ ] Mobile tested
- [ ] Instructions clear
- [ ] Support contact provided

## 📝 Learnings Log

### Conversation Quality
- Learning 1:
- Learning 2:

### Technical Insights
- Learning 1:
- Learning 2:

### User Experience
- Learning 1:
- Learning 2:

## ✅ Definition of Done for Week 1
- [ ] 10+ conversations completed
- [ ] Feedback from 5+ teachers
- [ ] Cost per conversation calculated
- [ ] Performance metrics documented
- [ ] Clear list of Phase 2 requirements
- [ ] Go/no-go decision on approach
- [ ] All code committed (even if rough)
- [ ] Learnings documented

## 🔄 Next Steps (Phase 2 Preview)
Based on learnings, we'll either:
1. **Continue with validated approach** - Build production infrastructure
2. **Pivot based on feedback** - Adjust core assumptions
3. **Major rework needed** - Fundamental changes required

---

# Previous Sprint: Phase 1.5 Assignment Management ✅

Successfully completed assignment management system:
- Database models for assignments and assignment-clients
- Full CRUD operations with teacher isolation
- Publishing workflow (draft/published states)
- Student viewing with enrollment checks
- 77 tests added (300 total in project)
- Comprehensive documentation

See [`docs/completed/phase-1-5-assignment-management.md`](docs/completed/phase-1-5-assignment-management.md) for details.