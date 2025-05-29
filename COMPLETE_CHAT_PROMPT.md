# Virtual Client - Complete Chat Session df

## 🏁 Before Ending This Session

### 1. Update Documentation
Based on what was accomplished:

**CURRENT_SPRINT.md** (always):
- [ ] Mark completed tasks with ✅
- [ ] Update "Session Handoff" section for next session
- [ ] Update "Where We Are" section if moving to next part
- [ ] Add any discovered blockers or important context
- [ ] If sprint complete, prepare next sprint section

**.claude-context.md** (if moving to next task):
- [ ] Update "Current Task" section
- [ ] Update "Key Files" list
- [ ] Refresh "Critical Patterns"
- [ ] Update "Implementation Checklist"

**PATTERNS.md** (if new patterns):
- [ ] Add any new patterns discovered
- [ ] Update existing patterns if improved
- [ ] Ensure proper categorization
- [ ] Check size (split at 800 lines per DOCUMENTATION_STANDARDS.md)

**tests/TESTING_GUIDE.md** (if test issues or learnings):
- [ ] Add any new test patterns discovered
- [ ] Update troubleshooting section if new issues found
- [ ] Add new fixtures if created
- [ ] Update best practices if learned something new

**PROJECT_ROADMAP.md** (if phase part complete):
- [ ] Update progress percentages
- [ ] Add actual time for completed parts
- [ ] Mark phases/parts as complete

**DATA_MODELS.md** (if models touched):
- [ ] Move models from planned to implemented
- [ ] Add any new models created
- [ ] Update relationships or constraints
- **Location**: `docs/architecture/DATA_MODELS.md`

**ENVIRONMENT.md** (if environment changed):
- [ ] Add new dependencies
- [ ] Update commands
- [ ] Add troubleshooting tips

### 2. Clean Up
- [ ] Delete any temporary test files created during debugging
- [ ] Ensure all tests are passing
- [ ] Remove any console.log or print statements used for debugging
- [ ] Close any test database connections

### 3. Prepare Next Session
Update the top of CURRENT_SPRINT.md with:
```
## 📍 Session Handoff
**Last Updated**: [Date/Time]
**Last Completed**: [What was just finished]
**Ready to Start**: [Next task]
**Tests Passing**: All tests passing ✅ / [List any failures]
**Notes for Next Session**: [Any important context]
```

### 4. Commit Message Template
```
Phase X.X Part Y: [Brief description]

- Implemented [main features]
- Added [number] tests, all passing
- Updated [which documentation]
- Next: [what comes next]
```

## 📋 Documentation Update Checklist

After implementation, ask yourself:
1. Did I establish any new patterns? → Update PATTERNS.md
2. Did I complete a phase part? → Update PROJECT_ROADMAP.md progress
3. Did I discover anything unexpected? → Note in CURRENT_SPRINT.md
4. Are all tests documented? → Update testing section in CURRENT_SPRINT.md
5. Did I create new files? → Update .claude-context.md if needed
6. Did I learn anything new about testing? → Update tests/TESTING_GUIDE.md

## 🧪 Test Results Documentation
Ensure CURRENT_SPRINT.md includes:
- Which tests were created (already listed in Tasks)
- Any regression tests that should be run next time
- Any flaky tests or known issues

Update the "Tests to Run" section in CURRENT_SPRINT.md:
- List new test files created
- Identify critical regression tests
- Note any special test commands
- Flag any tests that are slow or need special setup

### If Completing a Sprint/Part:
- [ ] Clear completed tasks from CURRENT_SPRINT.md
- [ ] Set up next sprint section with template
- [ ] Update .claude-context.md for next task
- [ ] Consider if phase summary needed (see DOCUMENTATION_STANDARDS.md)

## 📝 Final Checklist
- [ ] All new code has tests
- [ ] All tests are passing
- [ ] Documentation is updated
- [ ] Session handoff is complete
- [ ] No temporary files remain

Remember: The goal is to make the next session start smoothly!