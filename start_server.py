"""
Quick server test for Part 3
Starts the server and opens browser to test endpoints
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import subprocess
import time
import webbrowser
import sys

def test_server():
    """Start server and open browser to test endpoints"""
    print("=" * 60)
    print("Testing FastAPI Server - Part 3")
    print("=" * 60)
    
    print("\nStarting server...")
    print("Press Ctrl+C to stop the server\n")
    
    # Open browser to test endpoints
    time.sleep(1)
    webbrowser.open("http://localhost:8000/docs")
    
    # Start server
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--reload"]
    subprocess.run(cmd)

if __name__ == "__main__":
    test_server()
