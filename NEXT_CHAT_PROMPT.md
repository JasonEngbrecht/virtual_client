# Virtual Client - Continue Development

## 🎯 Start Here:
1. **Read `.claude-context.md`** - Quick overview of current task
2. **Read `CURRENT_SPRINT.md`** - Detailed task requirements
3. **Check "Session Handoff" section** in CURRENT_SPRINT - Any notes from last session
4. **Check `PATTERNS.md`** - If you need implementation patterns
5. **Check `PROJECT_ROADMAP.md`** - If you need project context
6. **Check `ENVIRONMENT.md`** - For system/IDE details
7. **Only look at docs/** - If CURRENT_SPRINT explicitly references it
8. **Ignore everything else** - Unless specifically directed

## 📍 Project Location:
`C:\Users\engbrech\Python\virtual_client`

## 💻 Environment:
- **OS**: Windows  
- **IDE**: PyCharm Professional
- **Python**: 3.12 with virtual environment
- See [`ENVIRONMENT.md`](ENVIRONMENT.md) for details

## 🤝 Working Style:
- **Small, incremental changes** - One feature at a time
- **Ask before implementing** - Confirm understanding first
- **Test as you go** - Run tests after each change
- **Update docs as you work** - Don't leave it for later

## ✍️ Documentation Rules:
When completing work:
1. **Update CURRENT_SPRINT.md** - Mark tasks complete
2. **Add to PATTERNS.md** - If you establish new patterns
3. **Create phase summary** - Only after ALL parts complete
4. **Keep it focused** - Less is more

## 🧪 After Implementation:
1. **Write tests** for new functionality
2. **Run tests** listed in "Tests to Run" section of CURRENT_SPRINT
3. **Fix any failures** before proceeding
4. **Document results** in Session Handoff section

## 🏁 Session End:
1. **Read COMPLETE_CHAT_PROMPT.md** for documentation updates
2. **Update all relevant documentation**
3. **Prepare handoff** for next session
4. **Clean up** any temporary files

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

**Remember**: Focus on CURRENT_SPRINT.md. Everything else is supporting documentation.