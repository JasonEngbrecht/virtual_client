# Virtual Client - Project Roadmap

## 🎯 Project Vision

An educational application designed to help social work students practice client interactions through AI-powered simulations. The app allows teachers to create virtual clients with specific demographics and issues, upload evaluation rubrics, and enables students to engage in realistic practice sessions with automated feedback.

### Core Value Proposition
- **For Teachers**: Create realistic virtual clients, design evaluation criteria, monitor student progress
- **For Students**: Practice difficult conversations safely, receive immediate feedback, build confidence
- **For Programs**: Standardize training quality, track outcomes, reduce resource needs

### Target Scale
- **Students**: 10,000-20,000 per semester
- **Conversations**: 10-20 per student (100,000-400,000 total)
- **Messages**: 30+ per conversation (6+ million messages per semester)

## 💰 API Cost Projections

### Anthropic Claude Pricing
Based on 150,000 conversations per semester (10,000 students × 15 conversations):

| Model | Cost per Conversation | Semester Total | Recommendation |
|-------|----------------------|----------------|----------------|
| Claude 3 Opus | $0.16 | $24,000 | Too expensive for scale |
| Claude 3 Sonnet | $0.03 | **$4,500** | **Production choice** |
| Claude 3 Haiku | $0.003 | $450 | Development/testing |

**Token Usage Assumptions**:
- System prompt (client personality): ~500 tokens
- Average conversation: 30 messages
- Input tokens per conversation: ~3,500
- Output tokens per conversation: ~1,500

## 🏗️ Architecture Overview

### Data Hierarchy
```
Teacher
├── Course Sections
│   ├── Enrolled Students
│   └── Assignments
│       └── Assignment Clients (Client + Rubric pairs)
├── Client Profiles (reusable across assignments)
└── Evaluation Rubrics (reusable across assignments)

Student
├── Course Enrollments
└── Sessions
    ├── Assignment Sessions (linked to specific assignment)
    └── Practice Sessions (free practice)
        └── Messages (individual conversation turns)
```

### Technical Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (for scale from the start)
- **LLM Integration**: Anthropic Claude (Sonnet for production)
- **Prototype UI**: Streamlit (rapid testing)
- **Production UI**: React (scalable, responsive)
- **Caching**: Redis (for active sessions)
- **Monitoring**: Built-in token/cost tracking

## 📊 Development Phases

### ✅ Foundation Work Completed (17.25 hours)

We've already built a solid foundation with full CRUD operations:

#### ✅ 1.1: Database Foundation (2.5 hours)
- Database initialization with verification
- Base service class with session management
- Generic BaseCRUD for reusable operations
- Comprehensive testing infrastructure

#### ✅ 1.2: ClientProfile CRUD (3.25 hours)
- Full CRUD API for virtual clients
- Teacher isolation and permissions
- Comprehensive error handling
- Mock authentication system

#### ✅ 1.3: EvaluationRubric CRUD (3 hours)
- Rubric management with criteria validation
- Weight sum validation with helpful errors
- Cascade protection for in-use rubrics
- Duplicate criterion prevention

#### ✅ 1.4: Course Section Management (4.5 hours)
- Complete section and enrollment management
- Teacher isolation at service layer
- Student access controls
- Soft delete with reactivation

#### ✅ 1.5: Assignment Management (4 hours)
- Assignment CRUD with publishing workflow
- Assignment-client relationships with rubrics
- Practice vs graded modes
- Date-based availability

### 🚀 New Development Phases (Starting Now)

## Phase 1: Minimum Viable Conversation (1 week)
**Goal**: Get teachers and students testing real AI conversations ASAP

### Week 1 Sprint

#### Day 1-2: Simplified Session & Message Models ✅ (100% complete)
- ✅ Create minimal session tracking
- ✅ Separate messages table (not JSON)
- ✅ Token counting from the start
- ✅ Basic session states
- ✅ Message operations (all parts complete)
- ✅ Token counting utility integrated
- ✅ Added 106 tests for models and services

```python
# Simplified models
Session: id, student_id, client_id, started_at, status
Message: id, session_id, role, content, timestamp, token_count
```

#### Day 3: Anthropic Integration ✅ (100% complete)
- ✅ API connection and configuration (Part 1 complete - 28 tests)
- ✅ Prompt generation from client profiles (Part 2 complete - 24 tests)
- ✅ Conversation Handler Service (Part 3 complete - 38 tests)
  - All methods implemented: start_conversation, send_message, get_ai_response, end_conversation
  - Full conversation flow working with proper context management
  - Access control and error handling integrated
- ✅ Rate limiting implementation (Part 4 complete - 29 tests)
  - Per-user and global rate limits
  - In-memory storage for MVP (Redis-ready)
  - Decorator pattern for easy application
- ✅ Error handling & robustness (Part 5 complete - 43 tests)
  - Circuit breaker pattern for API protection
  - Cost tracking with configurable alerts ($0.10/$0.50/$10)
  - Fallback responses for outages
  - Service health monitoring
- ✅ Token counting and cost tracking (integrated throughout)
- Total: 566 tests passing (comprehensive coverage)

#### Day 4-5: Streamlit Prototype 🏃 (90% complete - Part 9/11 done)
- ✅ **Part 1 Complete**: MVP Setup & Basic Infrastructure (~30 min)
  - Created mvp/ directory structure with all files
  - Implemented comprehensive utils.py with database, auth, UI helpers
  - Fixed SQLAlchemy and auth model compatibility issues
  - Added 19 tests for MVP utilities
- ✅ **Part 2 Complete**: Teacher Interface - Client Form (~1 hour)
  - Full client creation form with all fields
  - Form validation (name required, 2-5 personality traits)
  - Save functionality integrated with database
  - Display saved clients in grid with expandable details
  - Added 13 tests (7 integration, 6 business logic)
- ✅ **Part 3 Complete**: Teacher Interface - Test Conversation (~2 hours)
  - Full chat interface with real-time messaging
  - Token counting and cost tracking per message
  - Session management (start/end conversations)
  - Fixed AttributeError issues with service imports
  - Environment configuration pattern implemented
  - Added 22 tests (14 integration, 8 unit)
- ✅ **Part 4 Complete**: Teacher Interface - Metrics & History (~90 min)
  - Conversation history viewer with expandable details
  - 7 key metrics dashboard (costs, tokens, response times)
  - Export conversations as markdown
  - Simplified to 4 tests following MVP approach
- ✅ **Part 5 Complete**: Student Interface - Client Selection (~25 min)
  - Client grid display with cards showing key information
  - Session detection (Start vs Continue conversations)
  - Comprehensive field name fixes (learned to check models!)
  - Added 1 integration test following MVP approach
- ✅ **Part 6 Complete**: Student Interface - Conversation (~30 min)
  - Full conversation interface reusing teacher patterns
  - Session metrics (duration, tokens, cost) with real-time updates
  - Message history with proper formatting
  - End Session functionality with state management
  - Added 1 comprehensive conversation flow test
- ✅ **Part 7 Complete**: Admin Dashboard - Basic Metrics (~45 min)
  - Real-time metrics aggregation (active sessions, tokens today, cost today)
  - Session overview with active session details and duration tracking
  - Manual refresh functionality with proper database session management
  - Error handling for database connection issues
  - Added 1 integration test with 3 comprehensive scenarios
- ✅ **Part 8 Complete**: Admin Dashboard - Enhanced Monitoring (~45 min)
  - Auto-refresh functionality with 30-second intervals using session state
  - Usage graphs showing 24-hour token/cost trends with pandas DataFrames
  - Service health monitoring for both Anthropic API and database
  - Error log viewer with severity categorization and expandable details
  - Added 1 comprehensive integration test covering all new features
- ✅ **Part 9 Complete**: Polish & Integration Testing (~1 hour)
  - Enhanced error handling with user-friendly messages across all interfaces
  - Configuration warnings with setup instructions for missing API keys
  - Improved loading states with personalized messages ("💭 [Client Name] is thinking...")
  - Complete end-to-end integration test validating teacher→student→admin workflow
  - All three interfaces now work together seamlessly with consistent UX
  - Added 1 comprehensive workflow test (3 test methods)
- 🔄 **Part 10 Next**: Enhanced Teacher Features (~1-1.5 hours)
  - System prompt preview and editing capability
  - Model selection dropdown (Claude 4 Opus, Sonnet 4, 3.5 Sonnet, 3 Haiku)
  - Dynamic cost estimates based on selected model
  - Enhanced conversation start workflow
- **Teacher Page**: Create/edit one client, test chat
- **Student Page**: Select client, have conversation
- **Admin Page**: Monitor token usage and costs with enhanced features
- Test locally first, deploy to Railway when ready for external users
- **Detailed 11-part implementation plan** with:
  - Incremental development approach (~1-1.5 hours remaining)
  - Testing checkpoints after each part
  - Success metrics and go/no-go decisions
  - Natural break points for session management

#### Day 6-7: Initial Testing & Iteration
- Get 5-10 teachers testing
- Monitor conversation quality
- Track API costs
- Gather feedback on client responses
- Quick fixes and adjustments

### Deliverables
- Working conversation system
- Real teacher/student feedback
- Validated API cost model
- List of improvements needed

## Phase 2: Validated Foundation (2 weeks)
**Goal**: Build scalable infrastructure based on MVP learnings

### Week 1: Core Infrastructure

#### Enhanced Data Models
- Message indexing for 6M+ messages
- Session metadata and analytics
- Client profile versioning/snapshots
- Cost tracking per student/section
- Conversation state management

#### Scalable Architecture
- PostgreSQL optimization
- Redis caching for active sessions
- Queue system for async operations
- API rate limiting per user
- Monitoring and alerting

### Week 2: Refined Experience

#### Improved AI Integration
- Better prompt engineering based on feedback
- Personality consistency improvements
- Educational boundaries enforcement
- Context window management
- Fallback handling

#### Essential Features
- Basic rubric integration
- Simple evaluation prototype
- Session history viewing
- Bulk operations for teachers
- Cost control dashboard

### Deliverables
- Production-ready database
- Scalable message handling
- Refined AI conversations
- Cost control system

## Phase 3: Full Teacher Tools (2 weeks)
**Goal**: Complete teacher experience using existing foundation

### Week 1: Integration
- Connect existing rubric system
- Link assignment management
- Section rostering tools
- Client library management

### Week 2: Analytics & Control
- Student progress dashboard
- Conversation quality metrics
- Token usage reports
- Bulk operations interface
- Export capabilities

### Deliverables
- Complete teacher dashboard
- Analytics and reporting
- Integrated assignment system
- Quality control tools

## Phase 4: Production Student Experience (2 weeks)
**Goal**: Polished, scalable student interface

### Week 1: Core Experience
- React-based chat interface
- Mobile-responsive design
- Real-time message streaming
- Progress indicators
- Session management

### Week 2: Enhanced Features
- Practice vs assignment modes
- Attempt tracking
- Session history
- Progress visualization
- Help system

### Deliverables
- Production-ready student app
- Mobile support
- Performance at scale
- Complete user experience

## Phase 5: Automated Evaluation (1 week)
**Goal**: Close the feedback loop

### Evaluation System
- LLM-based analysis using rubrics
- Criterion-by-criterion scoring
- Specific feedback generation
- Teacher review interface
- Student feedback delivery

### Deliverables
- Automated scoring system
- Detailed feedback reports
- Teacher override capability
- Student progress tracking

## 🎯 Updated Timeline

### Immediate Path (8 weeks total)
- **Week 1**: MVP Conversation - Test core experience
- **Week 2-3**: Validated Foundation - Build for scale
- **Week 4-5**: Teacher Tools - Complete educator experience
- **Week 6-7**: Student Experience - Production UI
- **Week 8**: Evaluation - Close feedback loop

### Completed Foundation
- **17.25 hours** of infrastructure already built
- Database, authentication, CRUD operations ready
- Client profiles, rubrics, sections, assignments complete

## 🚀 Key Milestones

1. **Week 1**: First real teacher-student conversations
2. **Week 3**: Scalable architecture deployed
3. **Week 5**: Complete teacher experience
4. **Week 7**: Production student interface
5. **Week 8**: Automated feedback working

## 📈 Success Metrics

### Phase 1 Success (Week 1)
- 10+ test conversations completed
- <$0.01 per conversation cost
- 80%+ positive feedback on conversation quality
- Clear list of improvements

### Production Success (Week 8)
- Support 1,000 concurrent conversations
- <3 second response time
- 90%+ user satisfaction
- <$0.05 per conversation all-in cost

## 🔮 Future Enhancements (Post-MVP)

### Version 2.0 (Months 3-6)
- Voice interaction capabilities
- Group practice sessions
- Advanced analytics dashboard
- LMS integration (Canvas, Blackboard)
- Template marketplace

### Version 3.0 (Year 2)
- Custom AI fine-tuning
- Video avatar integration
- Multi-language support
- Peer review features
- Certification pathways

## 📝 Key Technical Decisions

### Revised Decisions
1. **PostgreSQL from Start**: Handle scale requirements
2. **Separate Messages Table**: Not JSON blob storage
3. **Anthropic Claude**: Better for nuanced educational conversations
4. **Streamlit First**: Validate before building complex UI
5. **Token Tracking Built-in**: Cost control from day one

### Maintained Decisions
1. **FastAPI**: Proven, fast, good for our needs
2. **Teacher Isolation**: Security and privacy
3. **Soft Delete**: Preserve history
4. **Pydantic Validation**: Type safety
5. **Section-Based Organization**: Mirrors academia

## 🎓 Educational Principles (Unchanged)

### Pedagogical Foundation
- **Safe Practice Environment**: Students can make mistakes without real consequences
- **Immediate Feedback**: Learning reinforced through timely evaluation
- **Realistic Scenarios**: Authentic client presentations and responses
- **Progressive Difficulty**: Start simple, increase complexity
- **Reflective Learning**: Review and analyze past performances

### Ethical Considerations
- **Representation**: Diverse, respectful client profiles
- **Privacy**: Secure handling of practice session data
- **Boundaries**: Clear educational context maintained
- **Sensitivity**: Appropriate handling of difficult topics
- **Oversight**: Teacher monitoring and intervention capabilities

---

*This roadmap reflects our pivot to validate the core experience quickly while maintaining our vision for a scalable, impactful educational tool.*