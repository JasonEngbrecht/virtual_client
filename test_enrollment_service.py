"""
Test Enrollment Service - Manual Testing Script
Tests the enrollment service functionality manually
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.database import db_service
from backend.services.enrollment_service import enrollment_service
from backend.services.section_service import section_service
from backend.models.course_section import CourseSectionDB, CourseSectionCreate
from uuid import uuid4


def test_enrollment_service():
    """Test enrollment service operations"""
    print("Testing Enrollment Service Operations...")
    print("=" * 50)
    
    with db_service.get_db() as db:
        # Clean up any existing test data
        print("Cleaning up existing test data...")
        db.query(CourseSectionDB).filter(
            CourseSectionDB.name.like("Test Section%")
        ).delete(synchronize_session=False)
        db.commit()
        
        # Create test sections
        print("\n1. Creating test sections...")
        section1 = section_service.create_section_for_teacher(
            db,
            CourseSectionCreate(
                name="Test Section - Math 101",
                description="Test section for enrollment demo",
                course_code="MATH101",
                term="Spring 2025"
            ),
            teacher_id="teacher-123"
        )
        print(f"   Created section: {section1.name} (ID: {section1.id})")
        
        section2 = section_service.create_section_for_teacher(
            db,
            CourseSectionCreate(
                name="Test Section - English 201",
                description="Another test section",
                course_code="ENG201",
                term="Spring 2025"
            ),
            teacher_id="teacher-123"
        )
        print(f"   Created section: {section2.name} (ID: {section2.id})")
        
        # Test student IDs
        student1_id = "student-alice"
        student2_id = "student-bob"
        student3_id = "student-charlie"
        
        # Test enrollment
        print("\n2. Testing student enrollment...")
        enrollment1 = enrollment_service.enroll_student(
            db, section1.id, student1_id
        )
        if enrollment1:
            print(f"   ✓ Enrolled {student1_id} in {section1.name}")
            print(f"     Enrollment ID: {enrollment1.id}")
            print(f"     Enrolled at: {enrollment1.enrolled_at}")
        
        # Test duplicate enrollment
        print("\n3. Testing duplicate enrollment (should return existing)...")
        enrollment2 = enrollment_service.enroll_student(
            db, section1.id, student1_id
        )
        if enrollment2:
            print(f"   ✓ Duplicate enrollment handled correctly")
            print(f"     Same enrollment ID: {enrollment1.id == enrollment2.id}")
        
        # Enroll more students
        print("\n4. Enrolling additional students...")
        enrollment_service.enroll_student(db, section1.id, student2_id)
        print(f"   ✓ Enrolled {student2_id} in {section1.name}")
        
        enrollment_service.enroll_student(db, section1.id, student3_id, role="ta")
        print(f"   ✓ Enrolled {student3_id} in {section1.name} as TA")
        
        enrollment_service.enroll_student(db, section2.id, student1_id)
        print(f"   ✓ Enrolled {student1_id} in {section2.name}")
        
        # Test roster retrieval
        print("\n5. Getting section roster...")
        roster = enrollment_service.get_section_roster(db, section1.id)
        print(f"   Section 1 roster ({len(roster)} students):")
        for e in roster:
            print(f"     - {e.student_id} ({e.role})")
        
        # Test enrollment check
        print("\n6. Checking enrollment status...")
        is_enrolled = enrollment_service.is_student_enrolled(
            db, section1.id, student1_id
        )
        print(f"   Is {student1_id} enrolled in section 1? {is_enrolled}")
        
        is_enrolled = enrollment_service.is_student_enrolled(
            db, section1.id, "student-not-enrolled"
        )
        print(f"   Is student-not-enrolled in section 1? {is_enrolled}")
        
        # Test student sections
        print("\n7. Getting student's sections...")
        sections = enrollment_service.get_student_sections(db, student1_id)
        print(f"   {student1_id} is enrolled in {len(sections)} sections:")
        for s in sections:
            print(f"     - {s.name} ({s.course_code})")
        
        # Test unenrollment
        print("\n8. Testing unenrollment...")
        success = enrollment_service.unenroll_student(
            db, section1.id, student2_id
        )
        print(f"   Unenrolled {student2_id} from section 1: {success}")
        
        # Check roster after unenrollment
        roster = enrollment_service.get_section_roster(db, section1.id)
        print(f"   Updated roster ({len(roster)} active students):")
        for e in roster:
            print(f"     - {e.student_id} ({e.role})")
        
        # Check with inactive included
        roster_all = enrollment_service.get_section_roster(
            db, section1.id, include_inactive=True
        )
        print(f"   Total roster including inactive ({len(roster_all)} total):")
        for e in roster_all:
            status = "active" if e.is_active else "inactive"
            print(f"     - {e.student_id} ({e.role}) - {status}")
        
        # Test re-enrollment
        print("\n9. Testing re-enrollment of unenrolled student...")
        reenroll = enrollment_service.enroll_student(
            db, section1.id, student2_id
        )
        if reenroll:
            print(f"   ✓ Re-enrolled {student2_id} successfully")
            print(f"     Reactivated existing enrollment: {reenroll.is_active}")
        
        # Test invalid section enrollment
        print("\n10. Testing enrollment in non-existent section...")
        invalid = enrollment_service.enroll_student(
            db, "invalid-section-id", student1_id
        )
        print(f"   Enrollment in invalid section: {invalid}")
        
        # Clean up
        print("\n11. Cleaning up test data...")
        db.query(CourseSectionDB).filter(
            CourseSectionDB.id.in_([section1.id, section2.id])
        ).delete(synchronize_session=False)
        db.commit()
        print("   ✓ Test data cleaned up")
        
        print("\n" + "=" * 50)
        print("Enrollment Service Tests Complete!")


if __name__ == "__main__":
    test_enrollment_service()
