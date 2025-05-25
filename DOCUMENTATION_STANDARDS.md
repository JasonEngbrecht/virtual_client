# Documentation Standards

This guide ensures consistent documentation as the project grows.

## 📋 When to Update What

### CURRENT_SPRINT.md
**Update when:**
- Starting a new task/phase part
- Completing a task (mark with ✅)
- Discovering blockers or important context
- Planning next immediate steps

**Keep it:**
- Focused on NOW (current sprint only)
- Task-oriented with checkboxes
- Under 200 lines
- Clear on what NOT to do

### PROJECT_ROADMAP.md
**Update when:**
- Completing a phase or major milestone
- Changing project timeline or scope
- Adding new phases or features
- Updating progress percentages

**Keep it:**
- Strategic and high-level
- Focused on the big picture
- Clear about dependencies
- Updated with actual vs estimated times

### PATTERNS.md
**Update when:**
- Establishing a new pattern used across multiple files
- Discovering a better way to implement something
- Adding a new service/route/model pattern

**Keep it:**
- Organized by category (use table of contents)
- Code-focused with examples
- Under 1000 lines
- Practical and actionable

**Don't include:**
- One-off implementations
- Phase-specific details
- Historical decisions

### DATA_MODELS.md (in docs/architecture/)
**Update when:**
- Adding new models to the system
- Changing model fields or relationships
- Moving models from planned to implemented
- Adding validation rules or constraints

**Keep it:**
- Complete reference for all models
- Clear about implemented vs planned
- Showing relationships and constraints
- Including example JSON representations

### .claude-context.md
**Update when:**
- Moving to a new phase or part
- Key files or patterns change
- Current task focus shifts

**Keep it:**
- Ultra-concise (under 50 lines)
- Focused on immediate task
- With critical patterns only
- Updated with current file references

### ENVIRONMENT.md
**Update when:**
- Development tools change
- New dependencies added
- Testing strategy evolves
- Common commands change

**Keep it:**
- Practical and command-focused
- Windows-specific where relevant
- With troubleshooting tips
- Under 300 lines

### COMPLETE_CHAT_PROMPT.md
**Update when:**
- Documentation workflow changes
- New documentation files added
- Checklist items need revision

**Keep it:**
- As a checklist format
- Action-oriented
- With clear examples
- Under 150 lines

### README.md
**Update when:**
- Major phase completes
- Project structure changes
- New key technologies added

**Keep it:**
- High-level overview only
- Clear navigation to other docs
- Under 100 lines

## 📁 Creating New Documentation

### During Development
1. **Work in progress** → Update CURRENT_SPRINT.md only
2. **New patterns** → Add to PATTERNS.md immediately
3. **Model changes** → Update DATA_MODELS.md
4. **Temporary notes** → Keep in CURRENT_SPRINT.md

### After Phase Completion
1. **Create summary** in `docs/completed/phase-X-X-name.md`
   - Overview of what was built
   - Key patterns established
   - Lessons learned
   - Time taken

2. **Move details** to `docs/completed/phase-X-X-parts/` if needed
   - Only if individual parts are complex
   - Name consistently: `part-N-description.md`

3. **Update PROJECT_ROADMAP.md**
   - Mark phase complete
   - Update actual time taken
   - Adjust future estimates if needed

4. **Update .claude-context.md**
   - Point to next task
   - Update key files
   - Refresh critical patterns

5. **Clean up:**
   - Remove completed tasks from CURRENT_SPRINT.md
   - Delete temporary test scripts
   - Archive old prompts

## 🚫 What NOT to Document

### Avoid Creating:
- Multiple files for the same topic
- Detailed implementation notes during development
- Duplicate information across files
- Files in root directory (except core docs)

### Don't Document:
- Every bug fix
- Minor refactors
- Obvious code patterns
- Detailed test descriptions

## 📝 Documentation Templates

### Phase Summary Template
```markdown
# Phase X.X: [Name]

**Completed**: [Duration] | **Status**: ✅ Complete

## Overview
[1-2 paragraphs of what was built]

## What Was Built
- Key components created
- Major features implemented
- Important patterns established

## Key Patterns Established
[Only if new patterns were created]

## Files Created/Modified
- List major files only

## Lessons Learned
[Optional - only if significant]
```

### CURRENT_SPRINT Update Template
```markdown
## 📍 Session Handoff
**Last Updated**: [Date/Time]
**Last Completed**: [What was just finished]
**Ready to Start**: [Next task]
**Tests Passing**: All tests passing ✅ / [List any failures]
**Notes for Next Session**: [Any important context]

## 📍 Where We Are in the Journey
- **Current Phase**: X.X [Name] (Parts Y complete)
- **Next Part**: [Description]
- **Next Phase**: X.X [Name]
- **Overall Progress**: X% of Phase 1 complete
- **See**: [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) for full context

## 🎯 Sprint Goal
[Clear, single objective]

## 📋 Tasks
- [ ] Task 1
- [ ] Task 2
- [x] Completed task

## ⚠️ Key Patterns to Follow
[Reference to PATTERNS.md sections]

## ❌ What NOT to Do
[Common pitfalls to avoid]

## ✅ Tests to Run
**After implementing [Part Name]**:
- `python -m pytest tests/[new_test].py -v` (new)
- `python -m pytest tests/[regression].py -v` (regression)
- `python test_quick.py` (smoke test)
```

## 🔄 Maintenance Schedule

### After Each Task:
- Update CURRENT_SPRINT.md checkboxes and Session Handoff
- Add new patterns to PATTERNS.md if needed
- Update DATA_MODELS.md if models change
- Update .claude-context.md if focus shifts

### After Each Phase Part:
- Consider if detailed docs are needed
- Update progress in PROJECT_ROADMAP.md
- Update "Where We Are" in CURRENT_SPRINT.md
- Refresh .claude-context.md for next part

### After Each Phase:
- Create phase summary
- Archive detailed implementation notes
- Clean up root directory
- Update NEXT_CHAT_PROMPT.md if needed

## 📏 Size Guidelines

| Document | Max Lines | Purpose |
|----------|-----------|---------|
| .claude-context.md | 50 | Quick task reference |
| CURRENT_SPRINT.md | 200 | Active work only |
| PATTERNS.md | 1000 | Quick reference (categorized) |
| PROJECT_ROADMAP.md | 500 | Strategic vision |
| DATA_MODELS.md | 800 | Model reference |
| ENVIRONMENT.md | 300 | Dev setup & commands |
| COMPLETE_CHAT_PROMPT.md | 150 | Session end checklist |
| README.md | 100 | Navigation & overview |
| Phase summaries | 300 | Historical record |

## 🎯 Goal

**Make it easy for Claude to:**
1. Get oriented quickly (.claude-context)
2. Find current task (CURRENT_SPRINT)
3. Apply established patterns (PATTERNS)
4. Understand project context (PROJECT_ROADMAP)
5. Reference data structures (DATA_MODELS)
6. Know the environment (ENVIRONMENT)
7. Close sessions properly (COMPLETE_CHAT_PROMPT)

**Remember**: If Claude has to read more than 3 files to start working, the documentation has failed its purpose.