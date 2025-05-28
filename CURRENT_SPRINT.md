# Current Sprint: MVP - Minimum Viable Conversation

## 📍 Session Handoff
**Last Updated**: 2025-05-28 (~1:30 PM CST)
**Last Completed**: Part 10 - Enhanced Teacher Features ✅
**Ready to Start**: Railway Deployment (Priority) → Part 11 - Documentation & Handoff
**Tests Passing**: All tests passing ✅ (1 comprehensive integration test created for Part 10)
**Notes for Next Session**: 

**🚂 PRIORITY: Railway Deployment Plan Created**
- **Goal**: Deploy MVP to Railway for external testing (~$15-20/month)
- **Strategy**: Single service deployment (all Streamlit apps + FastAPI together)
- **Deployment Questions Answered**:
  - Cost approved: ~$15-20/month ✅
  - Option 1 (single service) selected ✅ 
  - User will handle Railway account setup ✅
  - Railway default domain for MVP ✅
  - Quick deployment prioritized ✅
- **Git Workflow Confirmed**: Manual deployments, local development continues on dev branch
- **Implementation Plan**: 45-60 minutes total (30 min prep files + 15-30 min deploy)

**Railway Deployment Implementation Tasks**:
1. **Phase 1: Prepare Deployment Files** (~30 min)
   - Update requirements.txt (add Streamlit + PostgreSQL)
   - Create Procfile for Railway startup
   - Create app_launcher.py to run all interfaces
   - Create railway_init.py for database setup
   - Create railway.json configuration
   - Update environment handling for Railway
2. **Phase 2: Railway Setup & Deploy** (~15-30 min)
   - Guide through Railway project creation
   - Configure PostgreSQL addon
   - Set environment variables
   - Deploy and test
3. **Phase 3: Testing & Handoff** (~15 min)
   - Test all functionality on Railway
   - Create deployment documentation
   - Share URLs for external testers

**Part 10 Completion Notes**:
- System prompt preview/editing and model selection fully implemented
- Successfully added custom system prompt capability with text area editing interface
- Implemented model selection dropdown with Claude 3 Haiku, Claude 3.5 Sonnet, Claude 3 Sonnet, and Claude 3 Opus
- Updated conversation service to accept `custom_system_prompt` and `model` parameters
- Enhanced UI flow: Select Client → Preview/Edit Prompt → Choose Model → Start Conversation
- Added real-time cost estimation based on selected model
- Model selection disabled during active conversations, reset when conversation ends
- Created comprehensive integration test `test_part10_enhanced_teacher_features.py` with 3 test scenarios
- Updated pricing structure to include Claude 3 Opus ($15/$75 per 1M tokens)
- Time taken: ~1.5 hours (as estimated)

**Part 11 Implementation Plan**:
1. **Create Quick Start Guide** - Simple setup instructions for new users
2. **Document Known Issues** - List any edge cases or limitations discovered
3. **Prepare Feedback Form** - Template for collecting user feedback
4. **Update All Documentation** - Ensure all docs are current and accurate
5. **Clean Up Project** - Remove temporary files, ensure tests pass
6. **Estimated Time**: ~30 minutes total

**Documentation Updated This Session**:
- CURRENT_SPRINT.md - Marked Part 10 complete, set up Part 11
- backend/services/conversation_service.py - Added custom_system_prompt and model parameters
- backend/services/anthropic_service.py - Enhanced model selection and cost tracking
- backend/utils/token_counter.py - Added Claude 3 Opus pricing structure
- mvp/teacher_test.py - Added prompt editing interface and model selection
- tests/integration/test_part10_enhanced_teacher_features.py - Comprehensive integration test

**Tests Created**:
- `test_part10_enhanced_teacher_features.py` - 3 comprehensive integration tests:
  - `test_custom_system_prompt_and_model_selection_workflow` - Complete prompt editing and model selection workflow
  - `test_default_vs_custom_prompt_behavior` - Validates custom prompts override default prompts
  - `test_model_selection_pricing_logic` - Tests all available models work correctly

**Tests to Run for Regression**:
```bash
# Run Part 10 integration test
python run_tests.py tests/integration/test_part10_enhanced_teacher_features.py -v

# Run all MVP tests
python run_tests.py tests/integration/test_mvp_setup.py -v
python run_tests.py tests/integration/test_teacher_interface_integration.py -v
python run_tests.py tests/integration/test_student_interface_integration.py -v
python run_tests.py tests/integration/test_admin_dashboard_integration.py -v
python run_tests.py tests/integration/test_part9_complete_workflow.py -v

# Run core service tests
python run_tests.py tests/unit/test_conversation_service.py -v
python run_tests.py tests/unit/test_session_service.py -v
python run_tests.py tests/unit/test_anthropic_service.py -v
```

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

**Part 4: Rate Limiting** ✅ Complete
- [x] Add rate limiting utilities in `backend/utils/rate_limiter.py`
- [x] Implement per-user limits (e.g., 10 messages/minute)
- [x] Implement global limits (e.g., 1000 messages/hour)
- [x] Use in-memory storage for MVP (prepare for Redis later)
- [x] Add decorators for easy application
- [x] **Test**: Rate limiting under various scenarios (22 unit tests + 7 integration tests)

**Part 5: Error Handling & Robustness** ✅ Complete
- [x] Add comprehensive error handling to anthropic_service
- [x] Implement retry logic with exponential backoff (enhanced existing)
- [x] User-friendly error messages for common failures
- [x] Fallback responses for API outages
- [x] Logging for debugging and monitoring
- [x] Cost alerts when approaching limits
- [x] **Test**: Error scenarios and recovery (43 tests created)

**Additional work completed**:
- Implemented circuit breaker pattern to prevent cascading failures
- Created comprehensive error categorization (Authentication, RateLimit, Connection, Timeout, etc.)
- Added cost tracking per session and daily totals with configurable thresholds
- Created fallback response system with multiple templates
- Enhanced service status monitoring (Healthy/Degraded/Unavailable)
- Added environment variable configuration for all thresholds
- Integrated cost tracking with conversation service
- All error types return appropriate user-friendly messages

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

**🚨 NEW TESTING APPROACH FOR MVP**:
- **Manual testing first** - Run the app and verify it works
- **Minimal automated tests** - Max 1 test per part
- **Focus on shipping** - Get user feedback, not test coverage
- **Document edge cases** - Note them, don't fix them all
- **Move fast** - If it demos well, it's good enough for MVP

#### Implementation Plan (10 Parts)

**Part 1: MVP Setup & Basic Infrastructure** ⏱️ (~30 min) ✅ COMPLETE
- [x] Create `mvp/` directory structure
- [x] Create `utils.py` with basic helpers:
  - Database connection function
  - Mock authentication (teacher_id="teacher-1", student_id="student-1")
  - Streamlit page config settings
  - UI helper functions (message display, formatting, etc.)
- [x] Create minimal `test_streamlit.py` to verify setup
- [x] **Test**: Run basic Streamlit app, verify it opens in browser
- [x] **Additional**: Created skeleton files for all interfaces
- [x] **Additional**: Added 19 tests for MVP utilities

**Part 2: Teacher Interface - Client Form** ⏱️ (~1 hour) ✅ COMPLETE
- [x] Create `teacher_test.py` with client form:
  - Text inputs: name, age, background
  - Selectboxes: personality traits
  - Text areas: scenario, challenges
- [x] Add "Save Client" functionality
- [x] Display saved client details
- [x] **Test**: Create a client, verify it saves to database

**Additional work completed**:
- Implemented comprehensive client form with all fields from ClientProfile model
- Added form validation (name required, 2-5 personality traits)
- Integrated with client_service for database operations
- Created grid display of saved clients with expandable details
- Added "Test Conversation" button (placeholder for Part 3)
- Created 7 integration tests covering full functionality
- Created 6 business logic unit tests
- All 13 tests passing

**Part 3: Teacher Interface - Test Conversation** ⏱️ (~2 hours actual) ✅ COMPLETE
- [x] Add "Start Test Conversation" button
- [x] Create chat interface:
  - Message input field
  - Send button  
  - Message history display
- [x] Integrate with conversation service
- [x] Show token count per message
- [x] **Test**: Have a conversation, verify messages save

**Additional work completed**:
- Added dotenv loading to automatically use .env file throughout project
- Improved error handling with user-friendly messages for API issues
- Created session state management for conversations
- Integrated real-time cost and token tracking
- Added "End Conversation" functionality
- Fixed AttributeError issues with session_service access
- Created 22 comprehensive tests (14 integration, 8 unit)
- Added fallback responses for invalid API keys
- Created helper scripts: check_api_key.py, create_mock_conversation.py
- Updated documentation with setup instructions

**Tests Created**:
- `test_teacher_interface_integration.py`: Added TestTeacherConversationIntegration class with 8 tests
- `test_teacher_interface_logic.py`: Added TestConversationLogic class with 9 tests
- Added TestConversationUILogic class with 5 tests for UI logic without API

**Tests to Run**:
```bash
# Run all teacher interface tests
python run_tests.py tests/integration/test_teacher_interface_integration.py
python run_tests.py tests/unit/test_teacher_interface_logic.py

# Run specific conversation tests
python run_tests.py tests/integration/test_teacher_interface_integration.py::TestTeacherConversationIntegration
python run_tests.py tests/unit/test_teacher_interface_logic.py::TestConversationLogic

# Run UI logic tests (no API required)
python run_tests.py tests/integration/test_teacher_interface_integration.py::TestConversationUILogic
```

**Tests Created**:
- `test_teacher_interface_integration.py`: Added TestTeacherHistoryIntegration class with 8 tests
- `test_teacher_interface_logic.py`: Added TestConversationHistoryLogic class with 10 tests

**Tests to Run**:
```bash
# Run all teacher history tests
python run_tests.py tests/integration/test_teacher_interface_integration.py::TestTeacherHistoryIntegration
python run_tests.py tests/unit/test_teacher_interface_logic.py::TestConversationHistoryLogic

# Fix failing unit tests
python apply_test_fixes.py
python run_tests.py tests/unit/test_teacher_interface_logic.py
```

**Part 4: Teacher Interface - Metrics & History** ⏱️ (~45 min actual: ~90 min) ✅ COMPLETE
- [x] Add conversation history viewer - Shows all past conversations with expandable details
- [x] Show total tokens and cost - 7 key metrics displayed in dashboard
- [x] Add "Export Conversation" button - Exports as markdown with full details
- [x] Create metrics summary (avg response time, total cost) - Comprehensive metrics
- [x] **Test**: Complete full teacher workflow - 18 tests created (15 passing, 3 failing)

**Part 5: Student Interface - Client Selection** ⏱️ (~45 min actual: ~25 min) ✅ COMPLETE
- [x] Create `student_practice.py` - Grid layout with client cards
- [x] List available clients:
  - Client cards with name/description - Shows all key info
  - "Start Conversation" button per client - Integrated with ConversationService
- [x] Check for existing active sessions - Shows "Continue Conversation" for active sessions
- [x] **Manual Test**: Run locally, verify clients appear and sessions start - Setup script created
- [x] **Optional**: One integration test for happy path if time permits - Comprehensive test created

**Part 6: Student Interface - Conversation** ⏱️ (~1 hour actual: ~30 min) ✅ COMPLETE
- [x] Create chat interface (reuse teacher patterns) - Full conversation UI implemented
- [x] Add message history - Messages display with proper formatting
- [x] Implement "End Session" button - Properly ends session and clears state
- [x] Show session duration - Real-time duration tracking
- [x] **Manual Test**: Have a full conversation, verify messages save - Working perfectly
- [x] **Test Created**: `test_student_conversation_flow` - Comprehensive test with mocking

**Part 7: Admin Dashboard - Basic Metrics** ⏱️ (~45 min actual: ~45 min) ✅ COMPLETE
- [x] Create `admin_monitor.py` - Full implementation with real-time metrics
- [x] Add basic metrics:
  - Total active sessions - Count of sessions with status="active"
  - Tokens used today - Aggregated from sessions started today
  - Total cost today - Aggregated estimated costs from today's sessions
- [x] Add refresh button (manual for now) - Working refresh functionality
- [x] **Manual Test**: Run while using other interfaces, verify metrics display - Tested successfully
- [x] **Test Created**: `test_admin_dashboard_integration` - Comprehensive test with 3 scenarios

**Additional work completed**:
- Implemented proper date filtering for "today" metrics (midnight to now)
- Added session overview showing active sessions with details
- Used exact field names from SessionDB model (started_at, total_tokens, estimated_cost)
- Added error handling for database connection issues
- Created analysis metrics (cost per 1K tokens, completion rate)
- Followed existing UI patterns from teacher/student interfaces

**Part 8: Admin Dashboard - Enhanced Monitoring** ⏱️ (~45 min actual: ~45 min) ✅ COMPLETE
- [x] Add auto-refresh (every 30 seconds) - Auto-refresh checkbox now functional with session state
- [x] Create usage graph (tokens over time) - 24-hour timeline with hourly token/cost charts
- [x] Add error log viewer - Recent issues display with severity levels and expandable details
- [x] Show service health status - API and database health with status indicators
- [x] **Manual Test**: Monitor while using other interfaces - Tested successfully
- [x] **Test Created**: `test_enhanced_admin_features_integration` - Comprehensive test with usage timeline, service health, and error logging

**Additional work completed**:
- Implemented auto-refresh with 30-second intervals using session state management
- Created usage timeline showing 24 hours of hourly token and cost data
- Added side-by-side line charts for token and cost trends with summary metrics
- Implemented service health monitoring for both Anthropic API and database
- Added color-coded status indicators (🟢 Healthy, 🟡 Degraded, 🔴 Unavailable)
- Created error log viewer showing recent issues with severity categorization
- Enhanced admin interface with 4 new major sections beyond basic metrics
- Used pandas DataFrame for structured usage data with proper time bucketing

**Part 9: Polish & Integration Testing** ⏱️ (~1 hour actual: ~1 hour) ✅ COMPLETE
- [x] Add error handling to all interfaces - Enhanced with `handle_api_error()` function 
- [x] Improve UI styling and layout - Better loading states, configuration warnings
- [x] Add loading states - Personalized loading messages with client names
- [x] Test all three interfaces together - Comprehensive integration test created
- [x] **Manual Test**: Full workflow with multiple users - Validated teacher→student→admin flow
- [x] **One E2E Test**: Basic flow from client creation to conversation - `test_part9_complete_workflow.py`

**Part 10: Enhanced Teacher Features** ⏱️ (~1.5 hours actual) ✅ COMPLETE
- [x] Add system prompt preview and editing capability - Full text area editing with default/custom tabs
- [x] Add model selection dropdown (Claude 3 Opus, Claude 3.5 Sonnet, Claude 3 Sonnet, Claude 3 Haiku) - Complete with pricing display
- [x] Modify conversation service to accept custom prompts and model selection - Enhanced with new parameters
- [x] Update UI flow: Select Client → Preview/Edit Prompt → Choose Model → Start Conversation - Fully implemented
- [x] Update cost estimates based on selected model - Real-time cost estimation added
- [x] Disable model selection during active conversations - Settings locked during conversation, reset on end
- [x] **Manual Test**: Test all model options and prompt editing - All models working, prompt editing functional
- [x] **One Integration Test**: Validate prompt editing and model selection workflow - `test_part10_enhanced_teacher_features.py` created

**Additional work completed**:
- Added Claude 3 Opus pricing ($15/$75 per 1M tokens) to token counter utility
- Enhanced conversation service to pass custom prompts through entire message flow
- Updated anthropic service to handle dynamic model selection with proper cost tracking
- Created comprehensive setup interface with model comparison and cost estimation
- Implemented tabs for default vs custom prompt editing
- Added prompt reset and save functionality
- Enhanced UI with expandable current settings display
- All functionality working with 3 comprehensive integration tests

**Part 11: Documentation & Handoff** ⏱️ (~30 min)
- [ ] Create quick start guide
- [ ] Document known issues
- [ ] Prepare feedback form
- [ ] Update CURRENT_SPRINT.md
- [ ] **Manual Test**: Fresh install verification
- [ ] **List**: Edge cases to handle post-MVP

#### Testing Checkpoints
- **After Each Part**: Run interface, verify feature, check database, note issues
- **Part 4**: Full teacher workflow
- **Part 6**: Full student workflow
- **Part 8**: Admin monitoring both
- **Part 10**: New user experience

#### Success Metrics Per Part
| Part | Success Criteria |
|------|------------------|
| 1 | Streamlit app opens in browser |
| 2 | Client saved to database |
| 3 | Messages appear in chat |
| 4 | Costs calculated correctly |
| 5 | Students see clients |
| 6 | Student conversations work |
| 7 | Metrics display accurately |
| 8 | Auto-refresh works |
| 9 | No errors in typical use |
| 10 | New user can start in 5 min |

#### Go/No-Go Decisions
- **After Part 3**: Core conversation functionality works? → Proceed or fix
- **After Part 6**: Both teacher and student flows work? → Add admin or polish
- **After Part 9**: Ready for external users? → Deploy or fix issues

#### Time Estimates
- **Total**: ~8-10 hours of focused work
- **Natural break points**: After Parts 4, 6, and 8

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