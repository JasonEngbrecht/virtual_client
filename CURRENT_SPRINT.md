# Current Sprint: MVP - Minimum Viable Conversation

## 📍 Session Handoff
**Last Updated**: 2025-01-27 19:00
**Last Completed**: Major documentation pivot to MVP approach
**Ready to Start**: MVP Week 1 - Day 1 (Session & Message Models)
**Tests Passing**: All foundation tests passing ✅ (300 total tests)
**Pivot Rationale**: Building infrastructure without validating core conversation experience
**Notes for Next Session**: 
- Foundation CRUD complete (17.25 hours of solid infrastructure)
- Successfully pivoted all documentation to MVP approach
- Created comprehensive MVP tracking and patterns
- Target scale clarified: 10-20k students, 6M+ messages/semester
- API costs projected: ~$4,500/semester with Claude Sonnet
- Ready to implement simplified session/message models
- Focus: Get to real conversations ASAP

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

- [ ] Create simplified session model
  ```python
  # Simple but ready to scale
  Session: id, student_id, client_profile_id, started_at, ended_at, status
  ```
- [ ] Create proper messages table (NOT JSON blob)
  ```python
  # Built for 6M+ messages from start
  Message: id, session_id, role, content, timestamp, token_count, sequence_number
  ```
- [ ] Add token counting to models
- [ ] Create session service with basic operations
- [ ] Write minimal tests for new models
- [ ] Set up PostgreSQL (or decide on SQLite for MVP)

### Day 3: Anthropic Integration
**Goal**: Connect AI and start generating responses

- [ ] Set up Anthropic API connection
- [ ] Create prompt generation from client profiles
  ```python
  def generate_system_prompt(client: ClientProfile) -> str:
      # Convert profile to personality prompt
  ```
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

- [ ] Deploy to Streamlit Cloud (or chosen platform)
- [ ] Recruit 5-10 teachers for testing
- [ ] Create feedback form
- [ ] Monitor all conversations
- [ ] Track costs and performance
- [ ] Daily standup on findings
- [ ] Quick fixes based on feedback
- [ ] Document all learnings

## 🔧 Technical Decisions for MVP

### Architecture Choices
1. **Database**: PostgreSQL preferred (but SQLite acceptable for week 1)
2. **Messages**: Separate table from day 1 (no JSON blobs)
3. **API**: Use Anthropic Claude Haiku for testing ($0.003/conversation)
4. **UI**: Streamlit for rapid iteration
5. **Deployment**: Streamlit Cloud (free tier)

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