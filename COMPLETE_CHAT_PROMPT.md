# Virtual Client - Complete Chat Session

## 🏁 Before Ending This Session

### 1. Update Documentation
Based on what was accomplished:

**CURRENT_SPRINT.md**:
- [ ] Mark completed tasks with ✅
- [ ] Update "Where We Are" section if moving to next part
- [ ] Add any discovered blockers or important context
- [ ] Update "Session Handoff" section for next session
- [ ] If sprint complete, prepare next sprint section

**PATTERNS.md** (if applicable):
- [ ] Add any new patterns discovered
- [ ] Update existing patterns if improved
- [ ] Ensure proper categorization

**PROJECT_ROADMAP.md** (if applicable):
- [ ] Update progress percentages
- [ ] Add actual time for completed parts
- [ ] Mark phases/parts as complete

**DATA_MODELS.md** (if applicable):
- [ ] Move models from planned to implemented
- [ ] Add any new models created
- [ ] Update relationships or constraints

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

## 🧪 Testing Documentation
Add to CURRENT_SPRINT.md for the next session:
```
## ✅ Tests to Run
**New tests created**:
- `test_[filename].py` - [what it tests]

**Regression tests to verify**:
- `python -m pytest tests/unit/test_[critical].py` - [why critical]
- `python -m pytest tests/integration/test_[critical].py` - [why critical]
```

## 📝 Final Checklist
- [ ] All new code has tests
- [ ] All tests are passing
- [ ] Documentation is updated
- [ ] Session handoff is complete
- [ ] No temporary files remain

Remember: The goal is to make the next session start smoothly!