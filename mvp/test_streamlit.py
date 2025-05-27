"""
Test Streamlit app to verify MVP setup is working correctly

This is a minimal app that tests:
- Streamlit is installed and working
- Database connection is functional
- Mock authentication is available
- Basic UI utilities work
"""

import streamlit as st
from utils import (
    setup_page_config,
    get_database_connection,
    get_mock_teacher,
    get_mock_student,
    check_database_connection,
    show_success_message,
    show_error_message,
    show_info_message,
    format_cost,
    format_tokens,
    initialize_session_state
)


def main():
    # Configure page
    setup_page_config(
        page_title="MVP Setup Test",
        page_icon="🧪"
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.title("🧪 Virtual Client MVP - Setup Test")
    st.write("This page verifies that all MVP components are working correctly.")
    
    st.divider()
    
    # Test 1: Streamlit
    st.header("1. Streamlit Check")
    show_success_message("Streamlit is working! You're seeing this page.")
    
    # Test 2: Database Connection
    st.header("2. Database Connection")
    if check_database_connection():
        show_success_message("Database connection successful!")
        
        # Try to get some data
        try:
            db = get_database_connection()
            # Check if tables exist
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM client_profiles"))
            count = result.scalar()
            show_info_message(f"Found {count} client profiles in database")
            db.close()
        except Exception as e:
            show_error_message(f"Error querying database: {str(e)}")
    else:
        show_error_message("Database connection failed!")
    
    # Test 3: Mock Authentication
    st.header("3. Mock Authentication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Teacher Auth")
        teacher = get_mock_teacher()
        st.write(f"**ID:** {teacher.id}")
        st.write(f"**Teacher ID:** {teacher.teacher_id}")
        show_success_message("Teacher auth ready!")
    
    with col2:
        st.subheader("Student Auth")
        student = get_mock_student()
        st.write(f"**ID:** {student.id}")
        st.write(f"**Student ID:** {student.student_id}")
        show_success_message("Student auth ready!")
    
    # Test 4: Utility Functions
    st.header("4. Utility Functions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Cost Formatting")
        costs = [0.0001, 0.0045, 0.123, 1.50, 10.00]
        for cost in costs:
            st.write(f"{cost} → {format_cost(cost)}")
    
    with col2:
        st.subheader("Token Formatting")
        tokens = [50, 500, 1500, 15000, 150000]
        for token in tokens:
            st.write(f"{token} → {format_tokens(token)}")
    
    with col3:
        st.subheader("Session State")
        st.write(f"**Initialized:** {st.session_state.initialized}")
        st.write(f"**Session ID:** {st.session_state.current_session_id}")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
    
    # Test 5: Interactive Elements
    st.header("5. Interactive Elements Test")
    
    if st.button("Test Success Message"):
        show_success_message("This is a success message!")
    
    if st.button("Test Error Message"):
        show_error_message("This is an error message!")
    
    if st.button("Test Info Message"):
        show_info_message("This is an info message!")
    
    # Summary
    st.divider()
    st.header("📊 Setup Summary")
    
    all_good = check_database_connection()
    
    if all_good:
        st.balloons()
        show_success_message("All systems are GO! MVP setup is complete and working. 🚀")
        
        st.info("""
        **Next Steps:**
        1. Run `streamlit run mvp/teacher_test.py` for the teacher interface
        2. Run `streamlit run mvp/student_practice.py` for the student interface  
        3. Run `streamlit run mvp/admin_monitor.py` for the admin dashboard
        """)
    else:
        show_error_message("Some components are not working. Please check the errors above.")


if __name__ == "__main__":
    main()
