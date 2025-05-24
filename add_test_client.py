"""
Add a test client for teacher-123
Run this to create test data for the GET /clients endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.database import DatabaseService
from backend.services.client_service import client_service
from backend.models.client_profile import ClientProfileCreate

def add_test_client():
    """Add a test client for teacher-123"""
    print("=" * 60)
    print("Adding test client for teacher-123")
    print("=" * 60)
    
    # Initialize database service
    db_service = DatabaseService()
    
    # Create a test client
    client_data = ClientProfileCreate(
        name="John Doe",
        age=35,
        race="Caucasian",
        gender="Male",
        socioeconomic_status="Low income",
        issues=["housing_insecurity", "unemployment"],
        background_story="John has been struggling with unemployment for 6 months...",
        personality_traits=["anxious", "cooperative"],
        communication_style="direct"
    )
    
    # Add the client
    with db_service.get_db() as db:
        client = client_service.create_client_for_teacher(
            db,
            client_data,
            teacher_id="teacher-123"
        )
        print(f"\nCreated client: {client.name} (ID: {client.id})")
        print(f"Created by: {client.created_by}")
        print("\nYou can now test the GET /api/teacher/clients endpoint!")

if __name__ == "__main__":
    add_test_client()
