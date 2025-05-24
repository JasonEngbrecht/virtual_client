@echo off
REM Quick setup script for Virtual Client project in PyCharm

echo ========================================
echo Virtual Client - Quick PyCharm Setup
echo ========================================
echo.
echo This script will help set up your project.
echo Make sure PyCharm is closed before running this.
echo.
pause

echo.
echo Step 1: Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo.
echo Step 2: Creating virtual environment...
if exist venv (
    echo Virtual environment already exists!
) else (
    echo Creating new virtual environment...
    python -m venv venv
    echo Virtual environment created successfully!
)

echo.
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 4: Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

echo.
echo Step 5: Creating .env file from template...
if exist .env (
    echo .env file already exists! Skipping...
) else (
    copy .env.example .env
    echo .env file created! 
    echo.
    echo IMPORTANT: Edit .env file to add your API keys:
    echo - OpenAI API key
    echo - Anthropic API key
)

echo.
echo Step 6: Initializing database...
python -m backend.scripts.init_db

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open this project in PyCharm
echo 2. PyCharm should automatically detect the venv
echo 3. Edit the .env file to add your API keys
echo 4. Create a run configuration for backend/app.py
echo 5. Run the FastAPI server!
echo.
echo For detailed instructions, see:
echo - PYCHARM_SETUP.md
echo - setup_instructions.py
echo.
pause
