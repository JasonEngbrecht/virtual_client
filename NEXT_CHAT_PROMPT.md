# Virtual Client - Continue Development

## 🛍️ STOP: Read This First
**I work at YOUR pace. I will:**
- Show you my approach BEFORE coding
- Wait for your approval at each step
- Run tests and wait for confirmation before updating docs
- Never rush ahead without your input

## 🎯 Start Here:
1. **Read `.claude-context.md`** - Quick overview of current task
2. **Read `CURRENT_SPRINT.md`** - Detailed task requirements
3. **Check "Session Handoff" section** in CURRENT_SPRINT - Any notes from last session
4. **Check `PATTERNS.md`** - If you need implementation patterns
5. **Check `DATA_MODELS.md`** - If working with models/services
6. **Check `tests/TESTING_GUIDE.md`** - IMPORTANT: For writing and running tests
7. **Check `PROJECT_ROADMAP.md`** - If you need project context
8. **Check `ENVIRONMENT.md`** - For system/IDE details
9. **Only look at docs/** - If CURRENT_SPRINT explicitly references it
10. **Ignore everything else** - Unless specifically directed

## 📍 Project Location:
`C:\Users\engbrech\Python\virtual_client`

## 💻 Environment:
- **OS**: Windows  
- **IDE**: PyCharm Professional
- **Python**: 3.12 with virtual environment
- See [`ENVIRONMENT.md`](ENVIRONMENT.md) for details

## 🤝 Working Style:
- **ALWAYS ASK BEFORE IMPLEMENTING** - Show your approach and wait for approval
- **Small, incremental changes** - One feature at a time
- **Test as you go** - Run tests after each change
- **Get confirmation before proceeding** - Don't rush ahead
- **Documentation comes LAST** - Only after all tests pass

## ✍️ Documentation Rules:
When completing work:
1. **Update CURRENT_SPRINT.md** - Mark tasks complete
2. **Add to PATTERNS.md** - If you establish new patterns
3. **Follow DOCUMENTATION_STANDARDS.md** - For update guidelines
4. **Create phase summary** - Only after ALL parts complete
5. **Keep it focused** - Less is more

## 🧪 After Implementation:
1. **Write tests** for new functionality (see `tests/TESTING_GUIDE.md`)
2. **Run tests** listed in "Tests to Run" section of CURRENT_SPRINT
3. **Fix any failures** before proceeding
4. **STOP AND CONFIRM** - Show test results and wait for approval
5. **Only then** proceed to documentation updates

## 🏁 Session End (ONLY after tests pass and you confirm):
1. **WAIT FOR CONFIRMATION** that all tests are passing
2. **Then read COMPLETE_CHAT_PROMPT.md** for documentation updates
3. **Update all relevant documentation**
4. **Prepare handoff** for next session
5. **Clean up** any temporary files

## 🚫 What to Ignore:
- `/docs/completed/` - Historical reference only
- Old test scripts in root - Use `run_tests.py`
- Detailed phase documentation - Unless debugging specific issue

## ⚡ Quick Commands:
```bash
# Start server
python start_server.py

# Run tests
python run_tests.py

# Quick test
python test_quick.py
```

## 🔄 Session Handoff:
Before ending session:
1. Commit any changes
2. Update CURRENT_SPRINT.md with progress
3. Note any blockers or questions
4. **DELETE ANY TEMPORARY FILES** created during the session (cleanup_*.py, verify_*.py, check_*.py, status_*.py, etc.)

## 📚 Key Documentation Reference:
- **PATTERNS.md** - Established patterns (check before implementing)
- **DATA_MODELS.md** - Model definitions and relationships
- **tests/TESTING_GUIDE.md** - How to write and run tests correctly
- **DOCUMENTATION_STANDARDS.md** - How to update docs properly
- **.claude-ignore.md** - What to skip during development

## 🔄 Expected Workflow:
1. **Analyze** - Read the task and understand requirements
2. **Propose** - "I'll implement X by doing Y. Should I proceed?"
3. **Wait** - For your approval before coding
4. **Implement** - Code the approved approach
5. **Test** - Run tests and show results
6. **Wait** - For confirmation that tests look good
7. **Document** - Only after you confirm tests pass

## 🚨 CRITICAL - DO NOT CREATE TEST SCRIPTS! 🚨
**STOP! DO NOT CREATE ANY TEST RUNNER SCRIPTS!**
- **NEVER** create files like `test_xyz.py`, `verify_xyz.py`, `check_xyz.py` in the root directory
- **ALWAYS USE EXISTING TEST RUNNERS**:
  - `python run_tests.py` - Full test suite with coverage
  - `python run_tests.py tests/unit/test_assignment.py` - Specific test file
  - `python test_quick.py` - Quick database test
  - `python -m pytest [options]` - Direct pytest command
- **Creating new test scripts wastes time and clutters the project**
- **This is a HARD RULE - NO EXCEPTIONS**

## ⚠️ IMPORTANT REMINDERS:
- **ASK BEFORE CODING** - Always show your approach first
- **ONE STEP AT A TIME** - Don't implement multiple features at once
- **TESTS MUST PASS** - Before any documentation updates
- **WAIT FOR APPROVAL** - At each major step

**Remember**: Focus on CURRENT_SPRINT.md. Everything else is supporting documentation.