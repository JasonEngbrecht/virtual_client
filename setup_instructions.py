"""
Virtual Client Project Setup Instructions - PyCharm IDE

These instructions are specifically for PyCharm users.
PyCharm handles virtual environments automatically, making setup much easier!
"""

print("""
=== Virtual Client Project Setup in PyCharm ===

📁 STEP 1: Open Project in PyCharm
   - If PyCharm is open: File > Open
   - Navigate to: C:\\Users\\engbrech\\Python\\virtual_client
   - Click OK

🐍 STEP 2: Set Up Virtual Environment (PyCharm handles this!)
   
   Option A - If PyCharm asks about creating a virtual environment:
   - Click "OK" or "Create" when PyCharm offers to create venv
   - PyCharm will create it automatically
   
   Option B - If you need to create it manually:
   - File > Settings (or PyCharm > Preferences on Mac)
   - Project: virtual_client > Python Interpreter
   - Click the gear icon ⚙️ > Add
   - Choose "New Environment"
   - Location should be: C:\\Users\\engbrech\\Python\\virtual_client\\venv
   - Base interpreter: Select your Python 3.9+ installation
   - Click OK

📦 STEP 3: Install Dependencies in PyCharm
   
   Method 1 - Using PyCharm's Terminal (Recommended):
   - Open Terminal in PyCharm (View > Tool Windows > Terminal)
   - The terminal should show: (venv) at the start of the prompt
   - If not, PyCharm should activate it automatically
   - Run: pip install -r requirements.txt
   
   Method 2 - Using PyCharm's UI:
   - PyCharm might show a banner: "Package requirements not satisfied"
   - Click "Install requirements" in the banner
   - Or: File > Settings > Project > Python Interpreter
   - Click the + button, search and install packages

🔑 STEP 4: Set Up Environment Variables
   
   Method 1 - Create .env file (Recommended):
   - In PyCharm's Project view, right-click on project root
   - New > File
   - Name it: .env
   - Copy contents from .env and fill in your API keys:
     * OpenAI API key from: https://platform.openai.com/api-keys
     * Anthropic API key from: https://console.anthropic.com/
   
   Method 2 - PyCharm Run Configuration:
   - Can also set environment variables in run configurations (see Step 6)

💾 STEP 5: Initialize the Database
   - In PyCharm's Terminal (should show (venv)):
   - Run: python -m backend.scripts.init_db
   - You should see "Database initialization complete!"

▶️ STEP 6: Create Run Configuration for FastAPI
   - Run > Edit Configurations
   - Click + > Python
   - Configure as follows:
     * Name: FastAPI Server
     * Script path: Click folder icon and select backend/app.py
     * Working directory: Should auto-fill to project root
     * Environment variables: Click ... and add any if needed
     * Python interpreter: Should show "Project Default (Python 3.x venv)"
   - Click OK

🚀 STEP 7: Run the Application
   - Select "FastAPI Server" from the run configuration dropdown (top right)
   - Click the green Run button ▶️
   - The Run window should show: "Uvicorn running on http://0.0.0.0:8000"
   - Ctrl+Click the URL to open in browser
   - API docs available at: http://localhost:8000/docs

=== PyCharm Pro Tips ===

🔧 Integrated Tools:
   - Terminal: Always uses virtual environment automatically
   - Python Console: Interactive Python with your project imports
   - Database: View > Tool Windows > Database (can browse SQLite)
   - Git: VCS operations integrated in IDE

⌨️ Useful Shortcuts:
   - Shift+F10: Run current configuration
   - Ctrl+Shift+F10: Run current file
   - Alt+Shift+E: Execute selected code in Python Console
   - Ctrl+Alt+L: Reformat code
   - Ctrl+Space: Code completion
   - Ctrl+Click: Go to definition

📝 Code Helpers:
   - PyCharm will auto-import packages as you type
   - Yellow bulb 💡 icons offer quick fixes
   - Right-click > "Generate" for boilerplate code
   - TODO comments are tracked in View > Tool Windows > TODO

🐛 Debugging:
   - Click in the gutter to set breakpoints
   - Use Debug instead of Run to start debugger
   - Evaluate expressions while debugging

=== Common PyCharm Issues ===

❌ "No Python interpreter configured"
   - File > Settings > Project > Python Interpreter
   - Select the venv interpreter

❌ "Module not found" in editor (but code runs)
   - File > Invalidate Caches and Restart
   - Mark backend folder as Sources Root (right-click > Mark Directory as)

❌ Terminal doesn't show (venv)
   - Settings > Tools > Terminal
   - Shell path should be "cmd.exe" or "powershell.exe"
   - Restart terminal

=== Next Steps ===

Your PyCharm project is now ready! The IDE will:
✓ Automatically activate the virtual environment
✓ Provide code completion for all packages
✓ Show inline documentation
✓ Highlight any errors in real-time

Check the README.md for the development roadmap.
""")
