"""
API Dependencies
Provides common dependencies for FastAPI endpoints
"""

from typing import Dict

# For now, we'll use a simple dict for the teacher
# In production, this would be a proper User/Teacher model
Teacher = Dict[str, str]


async def get_current_teacher() -> Teacher:
    """
    Placeholder for authentication.
    Returns a mock teacher for development.
    
    In production, this would:
    - Extract and verify JWT token from request headers
    - Query the database for the teacher
    - Return the teacher object or raise 401 Unauthorized
    
    Returns:
        Dict containing teacher information
    """
    # TODO: Implement real authentication
    # This would typically:
    # 1. Get token from Authorization header
    # 2. Verify JWT token
    # 3. Extract teacher_id from token
    # 4. Fetch teacher from database
    # 5. Return teacher object
    
    return {
        "id": "teacher-123",
        "name": "Test Teacher",
        "email": "teacher@example.com",
        "role": "teacher"
    }


# Future dependencies can be added here:
# - get_current_student()
# - get_current_admin()
# - check_permissions()
# - rate_limit_check()
