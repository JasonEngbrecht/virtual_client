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

### PATTERNS.md
**Update when:**
- Establishing a new pattern used across multiple files
- Discovering a better way to implement something
- Adding a new service/route/model pattern

**Don't include:**
- One-off implementations
- Phase-specific details
- Historical decisions

### README.md
**Update when:**
- Major phase completes
- Project structure changes
- New key technologies added

**Keep it:**
- High-level overview only
- Clear navigation to other docs
- Under 200 lines

## 📁 Creating New Documentation

### During Development
1. **Work in progress** → Update CURRENT_SPRINT.md only
2. **New patterns** → Add to PATTERNS.md immediately
3. **Temporary notes** → Keep in CURRENT_SPRINT.md

### After Phase Completion
1. **Create summary** in `docs/completed/phase-X-X-name.md`
   - Overview of what was built
   - Key patterns established
   - Lessons learned
   - Time taken

2. **Move details** to `docs/completed/phase-X-X-parts/` if needed
   - Only if individual parts are complex
   - Name consistently: `part-N-description.md`

3. **Update README.md** progress section

4. **Clean up:**
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
```

## 🔄 Maintenance Schedule

### After Each Task:
- Update CURRENT_SPRINT.md checkboxes
- Add new patterns to PATTERNS.md if needed

### After Each Phase Part:
- Consider if detailed docs are needed
- Update progress in README.md

### After Each Phase:
- Create phase summary
- Archive detailed implementation notes
- Clean up root directory
- Update NEXT_CHAT_PROMPT.md if needed

## 📏 Size Guidelines

| Document | Max Lines | Purpose |
|----------|-----------|---------|
| CURRENT_SPRINT.md | 200 | Active work only |
| PATTERNS.md | 500 | Quick reference |
| README.md | 200 | Navigation & overview |
| Phase summaries | 300 | Historical record |

## 🎯 Goal

**Make it easy for Claude to:**
1. Find current task quickly
2. Apply established patterns
3. Ignore irrelevant history
4. Update docs consistently

**Remember**: If Claude has to read more than 3 files to start working, the documentation has failed its purpose.