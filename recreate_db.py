"""
Quick script to recreate the database with the new session fields.
Run this if you encounter issues with missing system_prompt or model_name fields.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.services.database import db_service

def recreate_database():
    """Recreate the database with current schema"""
    try:
        # Remove existing database if it exists
        db_path = "virtual_client.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Create new database with current schema
        db_service.create_tables()
        print("✅ Database recreated with updated schema")
        print("New session fields added:")
        print("  - system_prompt: Store custom system prompts")
        print("  - model_name: Store selected AI model")
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Recreating database with Part 10 enhancements...")
    success = recreate_database()
    
    if success:
        print("\n🚀 Ready to test enhanced teacher features!")
        print("Run: streamlit run mvp/teacher_test.py")
    else:
        print("\n❌ Database recreation failed. Check error messages above.")
