"""
Database initialization script
Creates the SQLite database and tables based on the schema
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import models
sys.path.append(str(Path(__file__).parent.parent.parent))


def init_database():
    """Initialize the SQLite database with tables"""
    
    # Get the database path
    db_dir = Path(__file__).parent.parent.parent / "database"
    db_path = db_dir / "app.db"
    schema_path = db_dir / "schema.sql"
    
    # Ensure database directory exists
    db_dir.mkdir(exist_ok=True)
    
    print(f"Initializing database at: {db_path}")
    
    # Connect to database (creates it if doesn't exist)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
        
        conn.commit()
        print("✓ Database tables created successfully")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\nDatabase initialization complete!")
    print(f"Database location: {db_path.absolute()}")


if __name__ == "__main__":
    init_database()
