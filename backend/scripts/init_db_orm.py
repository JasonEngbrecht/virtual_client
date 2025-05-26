"""
Database initialization using SQLAlchemy ORM
Creates all tables from the defined models
"""

import os
import logging
from pathlib import Path
import sys

# Add project root to path so we can import backend modules
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.services.database import db_service, Base
from backend.models import (
    ClientProfileDB,
    EvaluationRubricDB,
    SessionDB,
    MessageDB,
    EvaluationDB,
    CourseSectionDB,
    SectionEnrollmentDB,
    AssignmentDB,
    AssignmentClientDB
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_database_orm():
    """Initialize database using SQLAlchemy ORM models"""
    logger.info("Initializing database using SQLAlchemy ORM...")
    
    # Import all models to ensure they're registered with Base
    # (imports above handle this)
    
    # Create all tables
    try:
        db_service.create_tables()
        logger.info("All tables created successfully!")
        
        # Verify tables were created
        with db_service.get_db() as db:
            # Check what tables exist
            if "sqlite" in db_service.database_url:
                result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
            else:
                # PostgreSQL
                result = db.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
            
            logger.info(f"Created {len(tables)} tables:")
            for table in sorted(tables):
                logger.info(f"  - {table}")
            
            # Verify key tables exist
            expected_tables = {
                'client_profiles',
                'evaluation_rubrics', 
                'sessions',
                'messages',  # New table
                'evaluations',
                'course_sections',
                'section_enrollments',
                'assignments',
                'assignment_clients'
            }
            
            tables_set = set(tables)
            missing = expected_tables - tables_set
            if missing:
                logger.warning(f"Missing expected tables: {missing}")
            else:
                logger.info("All expected tables present!")
                
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False


def add_sample_data():
    """Add sample data for testing"""
    logger.info("Adding sample data...")
    
    try:
        with db_service.get_db() as db:
            # Check if sample data already exists
            existing = db.query(ClientProfileDB).filter_by(id='sample-client-1').first()
            if existing:
                logger.info("Sample data already exists, skipping...")
                return
            
            # Create sample client profile
            client = ClientProfileDB(
                id='sample-client-1',
                name='Maria Rodriguez',
                age=35,
                race='Hispanic',
                gender='Female',
                socioeconomic_status='Low income',
                issues=['housing_insecurity', 'unemployment', 'childcare_needs'],
                background_story='Maria is a single mother of two who recently lost her job...',
                personality_traits=['anxious', 'cooperative', 'emotional'],
                communication_style='indirect',
                created_by='teacher-1'
            )
            db.add(client)
            
            # Create sample rubric
            rubric = EvaluationRubricDB(
                id='sample-rubric-1',
                name='Basic Empathy Assessment',
                description='Evaluates student ability to demonstrate empathy and active listening',
                criteria=[
                    {
                        "name": "Active Listening",
                        "weight": 0.5,
                        "description": "Student demonstrates active listening skills"
                    },
                    {
                        "name": "Empathetic Response", 
                        "weight": 0.5,
                        "description": "Student responds with appropriate empathy"
                    }
                ],
                total_weight=1.0,
                created_by='teacher-1'
            )
            db.add(rubric)
            
            # Create sample session
            session = SessionDB(
                id='sample-session-1',
                student_id='student-1',
                client_profile_id='sample-client-1',
                status='completed',
                total_tokens=150,
                estimated_cost=0.0045  # ~$0.003 per 1000 tokens for Haiku
            )
            db.add(session)
            
            # Create sample messages
            messages = [
                MessageDB(
                    id='msg-1',
                    session_id='sample-session-1',
                    role='user',
                    content='Hello Maria, how are you doing today?',
                    token_count=10,
                    sequence_number=1
                ),
                MessageDB(
                    id='msg-2',
                    session_id='sample-session-1',
                    role='assistant',
                    content='I\'m... I\'m not doing so good. I lost my job last week and I don\'t know how I\'m going to pay rent.',
                    token_count=25,
                    sequence_number=2
                ),
                MessageDB(
                    id='msg-3',
                    session_id='sample-session-1',
                    role='user',
                    content='I\'m so sorry to hear that. That must be really stressful for you. Can you tell me more about what happened?',
                    token_count=25,
                    sequence_number=3
                )
            ]
            
            for msg in messages:
                db.add(msg)
            
            db.commit()
            logger.info("Sample data added successfully!")
            
    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        raise


def verify_database_orm():
    """Verify database structure using ORM"""
    logger.info("Verifying database structure...")
    
    try:
        with db_service.get_db() as db:
            # Test each model with a simple query
            models_to_test = [
                (ClientProfileDB, "client_profiles"),
                (EvaluationRubricDB, "evaluation_rubrics"),
                (SessionDB, "sessions"),
                (MessageDB, "messages"),
                (EvaluationDB, "evaluations"),
                (CourseSectionDB, "course_sections"),
                (SectionEnrollmentDB, "section_enrollments"),
                (AssignmentDB, "assignments"),
                (AssignmentClientDB, "assignment_clients")
            ]
            
            all_good = True
            for model, table_name in models_to_test:
                try:
                    count = db.query(model).count()
                    logger.info(f"✓ {table_name}: {count} records")
                except Exception as e:
                    logger.error(f"✗ {table_name}: {e}")
                    all_good = False
            
            # Test foreign key relationship (messages -> sessions)
            if all_good:
                try:
                    # This query tests the relationship
                    result = db.query(MessageDB).join(SessionDB).first()
                    logger.info("✓ Foreign key relationship (messages -> sessions) working")
                except Exception as e:
                    logger.warning(f"Foreign key test: {e}")
                    # This is expected in SQLite without foreign_keys pragma
                    if "sqlite" in db_service.database_url:
                        logger.info("Note: Foreign keys may not be enforced in SQLite without pragma")
            
            return all_good
            
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize database using SQLAlchemy ORM")
    parser.add_argument("--sample-data", action="store_true", help="Add sample data after initialization")
    parser.add_argument("--verify", action="store_true", help="Only verify existing database")
    
    args = parser.parse_args()
    
    if args.verify:
        # Just verify
        success = verify_database_orm()
        sys.exit(0 if success else 1)
    else:
        # Initialize database
        success = init_database_orm()
        
        if success and args.sample_data:
            add_sample_data()
            
        if success:
            verify_database_orm()
            
        sys.exit(0 if success else 1)
