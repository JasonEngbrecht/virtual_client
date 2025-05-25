"""
Verify that course section tables are created in test database
"""

from backend.services.database import Base, DatabaseService
# Import all models to ensure they're registered
from backend.models import (
    ClientProfileDB, 
    EvaluationRubricDB, 
    SessionDB, 
    EvaluationDB,
    CourseSectionDB,
    SectionEnrollmentDB
)

# Create in-memory database
db_service = DatabaseService("sqlite:///:memory:")

# Create all tables
print("Creating tables...")
Base.metadata.create_all(bind=db_service.engine)

# List all tables
with db_service.engine.connect() as conn:
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in result]
    
print("\nTables created:")
for table in tables:
    print(f"  - {table}")

# Check if course section tables exist
required_tables = ['course_sections', 'section_enrollments']
missing_tables = [t for t in required_tables if t not in tables]

if missing_tables:
    print(f"\nERROR: Missing tables: {missing_tables}")
else:
    print("\n✅ All course section tables created successfully!")

# Test creating a section
print("\nTesting section creation...")
from sqlalchemy.orm import Session
with Session(db_service.engine) as session:
    section = CourseSectionDB(
        teacher_id="teacher-123",
        name="Test Section",
        description="Test",
        is_active=True
    )
    session.add(section)
    session.commit()
    print(f"✅ Created section with ID: {section.id}")
    
    # Test creating enrollment
    enrollment = SectionEnrollmentDB(
        section_id=section.id,
        student_id="student-123",
        is_active=True,
        role="student"
    )
    session.add(enrollment)
    session.commit()
    print(f"✅ Created enrollment with ID: {enrollment.id}")

print("\n✅ Database test completed successfully!")
