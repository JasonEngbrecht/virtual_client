"""
Railway Database Initialization
Handles database setup for Railway deployment
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_railway_database():
    """Initialize database for Railway deployment"""
    logger.info("🚂 Initializing Railway database...")
    
    try:
        # Import after path setup
        from backend.services.database import db_service
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
        
        # Log database URL (without credentials)
        db_url = db_service.database_url
        if "postgresql" in db_url:
            # Hide password in logs
            safe_url = db_url.split('@')[1] if '@' in db_url else db_url
            logger.info(f"🗄️ Connecting to PostgreSQL: {safe_url}")
        else:
            logger.info(f"🗄️ Database URL: {db_url}")
        
        # Create all tables
        logger.info("🔧 Creating database tables...")
        db_service.create_tables()
        logger.info("✅ Database tables created successfully!")
        
        # Verify tables exist
        with db_service.get_db() as db:
            from sqlalchemy import text
            
            # Check tables based on database type
            if "postgresql" in db_url:
                result = db.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
            else:
                # SQLite fallback
                result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                
            tables = [row[0] for row in result]
            logger.info(f"📋 Created {len(tables)} tables: {', '.join(sorted(tables))}")
            
            # Verify key tables exist
            expected_tables = {
                'client_profiles', 'evaluation_rubrics', 'sessions', 'messages', 
                'evaluations', 'course_sections', 'section_enrollments', 
                'assignments', 'assignment_clients'
            }
            
            missing = expected_tables - set(tables)
            if missing:
                logger.warning(f"⚠️ Missing tables: {missing}")
            else:
                logger.info("✅ All expected tables created!")
        
        # Add sample data for testing
        add_railway_sample_data()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error("This is expected on first deployment - Railway will retry")
        return False


def add_railway_sample_data():
    """Add sample data for Railway deployment testing"""
    logger.info("📝 Adding sample data...")
    
    try:
        from backend.services.database import db_service
        from backend.models import ClientProfileDB, SessionDB, MessageDB
        
        with db_service.get_db() as db:
            # Check if sample data already exists
            existing = db.query(ClientProfileDB).filter_by(id='railway-sample-1').first()
            if existing:
                logger.info("📋 Sample data already exists, skipping...")
                return
            
            # Create Railway sample client
            client = ClientProfileDB(
                id='railway-sample-1',
                name='Alex Chen',
                age=28,
                race='Asian',
                gender='Non-binary',
                socioeconomic_status='Middle income',
                issues=['workplace_harassment', 'housing_discrimination'],
                background_story='Alex recently moved to a new city for work and is experiencing discrimination in both housing and workplace settings. They are seeking support and resources.',
                personality_traits=['analytical', 'cautious', 'articulate'],
                communication_style='direct',
                created_by='railway-teacher-1'
            )
            db.add(client)
            
            # Create sample session
            session = SessionDB(
                id='railway-session-1',
                student_id='railway-student-1',
                client_profile_id='railway-sample-1',
                status='completed',
                total_tokens=200,
                estimated_cost=0.006  # Sample cost
            )
            db.add(session)
            
            # Create sample messages
            messages = [
                MessageDB(
                    id='railway-msg-1',
                    session_id='railway-session-1',
                    role='user',
                    content='Hi Alex, I understand you wanted to speak with someone today. How are you feeling?',
                    token_count=20,
                    sequence_number=1
                ),
                MessageDB(
                    id='railway-msg-2',
                    session_id='railway-session-1',
                    role='assistant',
                    content='Hi, thank you for meeting with me. I\'m feeling pretty overwhelmed, to be honest. There\'s a lot going on with work and finding a place to live.',
                    token_count=30,
                    sequence_number=2
                )
            ]
            
            for msg in messages:
                db.add(msg)
            
            db.commit()
            logger.info("✅ Railway sample data added successfully!")
            
    except Exception as e:
        logger.warning(f"⚠️ Sample data creation failed: {e}")
        # This is non-critical, don't fail the entire initialization


def verify_railway_database():
    """Verify Railway database is working correctly"""
    logger.info("🔍 Verifying Railway database...")
    
    try:
        from backend.services.database import db_service
        from backend.models import ClientProfileDB, SessionDB, MessageDB
        
        with db_service.get_db() as db:
            # Test basic queries
            client_count = db.query(ClientProfileDB).count()
            session_count = db.query(SessionDB).count()
            message_count = db.query(MessageDB).count()
            
            logger.info(f"📊 Database contents:")
            logger.info(f"  - Clients: {client_count}")
            logger.info(f"  - Sessions: {session_count}")
            logger.info(f"  - Messages: {message_count}")
            
            # Test a join query
            result = db.query(MessageDB).join(SessionDB).first()
            if result:
                logger.info("✅ Database relationships working")
            else:
                logger.info("📝 No data for relationship test")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False


if __name__ == "__main__":
    # For manual testing
    success = init_railway_database()
    if success:
        verify_railway_database()
    sys.exit(0 if success else 1)
