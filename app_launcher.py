#!/usr/bin/env python3
"""
Railway App Launcher - Single entry point for all Virtual Client services
"""
import os
import sys
import subprocess
import signal
import time
from threading import Thread

def run_fastapi():
    """Run the FastAPI server"""
    import uvicorn
    from backend.api.main import app
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

def run_streamlit_app(app_name):
    """Run a specific Streamlit app"""
    port = int(os.environ.get("PORT", 8501))
    
    app_files = {
        "teacher": "mvp/teacher_test.py",
        "student": "mvp/student_practice.py", 
        "admin": "mvp/admin_monitor.py",
        "test": "mvp/test_streamlit.py"
    }
    
    if app_name not in app_files:
        print(f"Unknown app: {app_name}. Available: {list(app_files.keys())}")
        sys.exit(1)
    
    # Run streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        app_files[app_name],
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    subprocess.run(cmd)

def run_multi_service():
    """Run multiple services (FastAPI + main Streamlit app)"""
    # This is for local development - Railway will run single service
    import threading
    import uvicorn
    from backend.api.main import app as fastapi_app
    
    # Start FastAPI in background thread
    api_thread = threading.Thread(
        target=lambda: uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
    )
    api_thread.daemon = True
    api_thread.start()
    
    # Run teacher interface as main service
    time.sleep(2)  # Let API start first
    run_streamlit_app("teacher")

def main():
    """Main launcher logic"""
    # Initialize database first
    print("🔧 Initializing database...")
    try:
        from railway_init import init_railway_database
        init_railway_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    # Determine which service to run
    service = os.environ.get("RAILWAY_SERVICE", "teacher")
    
    print(f"🚀 Starting Virtual Client - Service: {service}")
    
    if service == "api":
        print("📡 Starting FastAPI server...")
        run_fastapi()
    elif service == "multi":
        print("🔀 Starting multi-service mode...")
        run_multi_service()
    elif service in ["teacher", "student", "admin", "test"]:
        print(f"🎓 Starting {service} interface...")
        run_streamlit_app(service)
    else:
        print(f"❌ Unknown service: {service}")
        print("Available services: api, teacher, student, admin, test, multi")
        sys.exit(1)

if __name__ == "__main__":
    main()
