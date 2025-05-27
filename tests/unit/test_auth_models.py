"""Test auth models."""

import pytest
from backend.models.auth import BaseUser, StudentAuth, TeacherAuth


def test_base_user():
    """Test BaseUser model."""
    user = BaseUser(id="user-123")
    assert user.id == "user-123"
    
    # Test model_dump
    data = user.model_dump()
    assert data == {"id": "user-123"}


def test_student_auth():
    """Test StudentAuth model."""
    student = StudentAuth(id="student-456", student_id="student-456")
    assert student.id == "student-456"
    assert student.student_id == "student-456"
    
    # Test model_dump
    data = student.model_dump()
    assert data == {"id": "student-456", "student_id": "student-456"}
    
    # Test with different IDs
    student2 = StudentAuth(id="auth-123", student_id="student-789")
    assert student2.id == "auth-123"
    assert student2.student_id == "student-789"


def test_teacher_auth():
    """Test TeacherAuth model."""
    teacher = TeacherAuth(id="teacher-789", teacher_id="teacher-789")
    assert teacher.id == "teacher-789"
    assert teacher.teacher_id == "teacher-789"
    
    # Test model_dump
    data = teacher.model_dump()
    assert data == {"id": "teacher-789", "teacher_id": "teacher-789"}
    
    # Test with different IDs
    teacher2 = TeacherAuth(id="auth-456", teacher_id="teacher-123")
    assert teacher2.id == "auth-456"
    assert teacher2.teacher_id == "teacher-123"


def test_auth_models_inheritance():
    """Test that auth models inherit from BaseUser correctly."""
    # Verify inheritance
    assert issubclass(StudentAuth, BaseUser)
    assert issubclass(TeacherAuth, BaseUser)
    
    # Verify they're different types
    student = StudentAuth(id="s1", student_id="s1")
    teacher = TeacherAuth(id="t1", teacher_id="t1")
    
    assert isinstance(student, StudentAuth)
    assert isinstance(student, BaseUser)
    assert not isinstance(student, TeacherAuth)
    
    assert isinstance(teacher, TeacherAuth)
    assert isinstance(teacher, BaseUser)
    assert not isinstance(teacher, StudentAuth)


if __name__ == "__main__":
    # Run the tests
    test_base_user()
    test_student_auth()
    test_teacher_auth()
    test_auth_models_inheritance()
    print("All auth model tests passed!")
