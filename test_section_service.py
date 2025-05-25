"""
Test script for Phase 1.4 Part 2 - Section Service
Run this to verify the section service implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.section_service import section_service, SectionService
from backend.models.course_section import CourseSectionCreate
from backend.services.database import db_service
from sqlalchemy.exc import SQLAlchemyError


def test_section_service():
    """Test the section service implementation"""
    print("=== Testing Section Service Implementation ===\n")
    
    # Test 1: Service instantiation
    print("1. Testing service instantiation...")
    try:
        service = SectionService()
        assert service is not None
        assert section_service is not None
        print("✅ Service instantiation successful")
    except Exception as e:
        print(f"❌ Service instantiation failed: {e}")
        return
    
    # Test 2: Create sections for a teacher
    print("\n2. Testing section creation...")
    with db_service.get_db() as db:
        try:
            # Create test sections
            teacher_id = "teacher-test-123"
            
            section_data1 = CourseSectionCreate(
                name="Social Work Practice I - Fall 2025",
                description="Introduction to social work practice",
                course_code="SW101",
                term="Fall 2025"
            )
            
            section_data2 = CourseSectionCreate(
                name="Social Work Ethics - Fall 2025",
                description="Ethical principles in social work",
                course_code="SW102",
                term="Fall 2025"
            )
            
            section1 = section_service.create_section_for_teacher(db, section_data1, teacher_id)
            section2 = section_service.create_section_for_teacher(db, section_data2, teacher_id)
            
            print(f"✅ Created section 1: {section1.name} (ID: {section1.id})")
            print(f"✅ Created section 2: {section2.name} (ID: {section2.id})")
            
            # Test 3: Get teacher sections
            print("\n3. Testing get_teacher_sections...")
            sections = section_service.get_teacher_sections(db, teacher_id)
            print(f"✅ Found {len(sections)} sections for teacher {teacher_id}")
            for section in sections:
                print(f"   - {section.name} ({section.course_code})")
            
            # Test 4: Permission checks
            print("\n4. Testing permission checks...")
            
            # Should return True for owner
            can_update_own = section_service.can_update(db, section1.id, teacher_id)
            can_delete_own = section_service.can_delete(db, section1.id, teacher_id)
            print(f"✅ Owner can update: {can_update_own}")
            print(f"✅ Owner can delete: {can_delete_own}")
            
            # Should return False for different teacher
            other_teacher_id = "teacher-other-456"
            can_update_other = section_service.can_update(db, section1.id, other_teacher_id)
            can_delete_other = section_service.can_delete(db, section1.id, other_teacher_id)
            print(f"✅ Other teacher can update: {can_update_other}")
            print(f"✅ Other teacher can delete: {can_delete_other}")
            
            # Test 5: Update section
            print("\n5. Testing section update...")
            updated_section = section_service.update(
                db, 
                section1.id,
                description="Updated description for the course"
            )
            print(f"✅ Updated section description: {updated_section.description}")
            
            # Test 6: Clean up - delete test sections
            print("\n6. Cleaning up test data...")
            section_service.delete(db, section1.id)
            section_service.delete(db, section2.id)
            print("✅ Test sections deleted")
            
        except SQLAlchemyError as e:
            print(f"❌ Database error: {e}")
            db.rollback()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== Section Service Test Complete ===")


if __name__ == "__main__":
    # Ensure database is initialized
    db_service.create_tables()
    test_section_service()
