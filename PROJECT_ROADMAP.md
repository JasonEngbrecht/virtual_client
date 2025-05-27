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

#### Day 3: Anthropic Integration ⚡ (75% complete)
- ✅ API connection and configuration (Part 1 complete - 28 tests)
- ✅ Prompt generation from client profiles (Part 2 complete - 24 tests)
- ✅ Conversation Handler Service (Part 3 complete - 38 tests)
  - All methods implemented: start_conversation, send_message, get_ai_response, end_conversation
  - Full conversation flow working with proper context management
  - Access control and error handling integrated
- ✅ Token counting and cost tracking (integrated throughout)
- 🔴 Rate limiting (Part 4 pending)
- 🔴 Advanced error handling with retries (Part 5 pending)
- 🔴 Message streaming support (future enhancement)

#### Day 4-5: Streamlit Prototype
- **Teacher Page**: Create/edit one client, test chat
- **Student Page**: Select client, have conversation
- **Admin Page**: Monitor token usage and costs
- Test locally first, deploy to Railway when ready for external users

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