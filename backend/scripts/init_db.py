"""
Database initialization script
Creates the SQLite database and tables from schema.sql
"""

import os
import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory (virtual_client)"""
    current_file = Path(__file__).resolve()
    # Go up from scripts -> backend -> virtual_client
    return current_file.parent.parent.parent


def init_database(db_path: str = None, schema_path: str = None) -> None:
    """
    Initialize the database with schema
    
    Args:
        db_path: Path to database file (optional, uses default if not provided)
        schema_path: Path to schema.sql file (optional, uses default if not provided)
    """
    project_root = get_project_root()
    
    # Use provided paths or defaults
    if db_path is None:
        db_path = project_root / "database" / "app.db"
    else:
        db_path = Path(db_path)
        
    if schema_path is None:
        schema_path = project_root / "database" / "schema.sql"
    else:
        schema_path = Path(schema_path)
    
    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing database at: {db_path}")
    logger.info(f"Using schema from: {schema_path}")
    
    # Check if schema file exists
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    # Read schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect to database and execute schema
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Execute the schema
        cursor.executescript(schema_sql)
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        logger.info("Created tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialization completed successfully!")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def verify_database(db_path: str = None) -> bool:
    """
    Verify that the database is properly initialized
    
    Args:
        db_path: Path to database file (optional, uses default if not provided)
        
    Returns:
        bool: True if database is properly initialized
    """
    project_root = get_project_root()
    
    if db_path is None:
        db_path = project_root / "database" / "app.db"
    else:
        db_path = Path(db_path)
    
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check for expected tables
        expected_tables = {
            'client_profiles',
            'evaluation_rubrics',
            'sessions',
            'evaluations'
        }
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = {row[0] for row in cursor.fetchall()}
        
        missing_tables = expected_tables - actual_tables
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False
        
        logger.info("Database verification passed!")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database verification error: {e}")
        return False
    finally:
        conn.close()


def add_sample_data(db_path: str = None) -> None:
    """
    Add sample data for development/testing
    
    Args:
        db_path: Path to database file (optional, uses default if not provided)
    """
    project_root = get_project_root()
    
    if db_path is None:
        db_path = project_root / "database" / "app.db"
    else:
        db_path = Path(db_path)
    
    logger.info("Adding sample data...")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Sample client profile
        cursor.execute("""
            INSERT INTO client_profiles (
                id, name, age, race, gender, socioeconomic_status,
                issues, background_story, personality_traits,
                communication_style, created_by
            ) VALUES (
                'sample-client-1',
                'Maria Rodriguez',
                35,
                'Hispanic',
                'Female',
                'Low income',
                '["housing_insecurity", "unemployment", "childcare_needs"]',
                'Maria is a single mother of two who recently lost her job...',
                '["anxious", "cooperative", "emotional"]',
                'indirect',
                'teacher-1'
            )
        """)
        
        # Sample rubric
        cursor.execute("""
            INSERT INTO evaluation_rubrics (
                id, name, description, criteria, total_weight, created_by
            ) VALUES (
                'sample-rubric-1',
                'Basic Empathy Assessment',
                'Evaluates student ability to demonstrate empathy and active listening',
                '[{"name": "Active Listening", "weight": 0.5, "description": "Student demonstrates active listening skills"}, {"name": "Empathetic Response", "weight": 0.5, "description": "Student responds with appropriate empathy"}]',
                1.0,
                'teacher-1'
            )
        """)
        
        conn.commit()
        logger.info("Sample data added successfully!")
        
    except sqlite3.IntegrityError:
        logger.info("Sample data already exists, skipping...")
    except sqlite3.Error as e:
        logger.error(f"Error adding sample data: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            # Just verify the database
            success = verify_database()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--sample-data":
            # Initialize and add sample data
            init_database()
            add_sample_data()
        elif sys.argv[1] == "--help":
            print("Usage: python init_db.py [options]")
            print("Options:")
            print("  --verify       Verify database is properly initialized")
            print("  --sample-data  Initialize database and add sample data")
            print("  --help         Show this help message")
            print("  (no options)   Initialize empty database")
            sys.exit(0)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: initialize empty database
        init_database()
        verify_database()
