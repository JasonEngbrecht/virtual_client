# PyCharm Quick Setup Guide

This guide is specifically for PyCharm users working on the Virtual Client project.

## Opening the Project

1. **File > Open** → Navigate to `C:\Users\engbrech\Python\virtual_client`
2. PyCharm should automatically detect the project structure

## Virtual Environment Setup

PyCharm typically handles this automatically:

- If prompted to create a virtual environment, click **Create**
- If not prompted:
  - **File > Settings > Project > Python Interpreter**
  - Click gear icon ⚙️ > **Add > New Environment**
  - Leave default location as `venv`

## Installing Dependencies

### Option 1: PyCharm Terminal (Recommended)
1. **View > Tool Windows > Terminal**
2. Terminal should show `(venv)` prefix
3. Run: `pip install -r requirements.txt`

### Option 2: PyCharm UI
- If you see banner "Package requirements not satisfied" → Click **Install requirements**
- Or manually: **Settings > Project > Python Interpreter** → Click **+** to add packages

## Environment Variables

1. Right-click project root → **New > File** → Name it `.env`
2. Copy contents from `.env.example`
3. Add your API keys:
   - OpenAI: Get from https://platform.openai.com/api-keys
   - Anthropic: Get from https://console.anthropic.com/

## Database Initialization

In PyCharm Terminal:
```bash
python -m backend.scripts.init_db
```

## Run Configuration

1. **Run > Edit Configurations**
2. Click **+** > **Python**
3. Configure:
   - **Name**: FastAPI Server
   - **Script path**: `backend/app.py`
   - **Working directory**: Project root (auto-filled)
4. Click **OK**

## Running the Application

1. Select "FastAPI Server" from dropdown (top-right toolbar)
2. Click green Run button ▶️
3. API available at: http://localhost:8000
4. API docs at: http://localhost:8000/docs

## PyCharm Tips

### Useful Shortcuts
- `Shift+F10`: Run current configuration
- `Ctrl+Space`: Code completion
- `Ctrl+Click`: Go to definition
- `Ctrl+Alt+L`: Reformat code
- `Alt+Enter`: Quick fixes (yellow bulb 💡)

### Project Structure
- Mark `backend` as **Sources Root** if imports aren't recognized
- Use **TODO** comments to track tasks
- **Database** tool window can browse SQLite files

### Troubleshooting
- **"No interpreter"**: Settings > Project > Python Interpreter
- **Import errors**: File > Invalidate Caches and Restart
- **Terminal issues**: Ensure Settings > Tools > Terminal uses cmd.exe or PowerShell

## Development Workflow

1. Always work with PyCharm (auto-activates venv)
2. Use integrated Terminal for commands
3. Use integrated Git for version control
4. Set breakpoints by clicking in the gutter
5. Use Debug mode for troubleshooting
