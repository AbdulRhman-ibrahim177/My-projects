import streamlit as st
import pandas as pd
import os
import time

# Performance optimization: Cache data loading with TTL
@st.cache_data(ttl=1)  # Cache expires after 1 second
def load_courses():
    return pd.read_csv('Courses.csv')

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'action' not in st.session_state:
    st.session_state.action = "View Courses"

# Admin credentials (in a real app, these would be stored securely)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def save_courses(courses_df: pd.DataFrame):
    """Save courses and clear cache"""
    courses_df.to_csv('Courses.csv', index=False)
    # Clear the cache to force reload
    st.cache_data.clear()

def show_admin_login():
    st.title("Admin Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials!")

def show_admin_dashboard():
    st.title("Admin Dashboard - Knowledge Base Editor")
    
    try:
        # Load courses data using cached function
        courses_df = load_courses()
    except Exception as e:
        st.error(f"Error loading courses: {str(e)}")
        return
    
    # Sidebar navigation
    st.session_state.action = st.sidebar.radio("Select Action", ["View Courses", "Add Course", "Edit Course", "Delete Course"])
    
    if st.session_state.action == "View Courses":
        st.header("Current Courses")
        st.dataframe(courses_df)
        
        # Show success message if coming from edit
        if st.session_state.show_success:
            st.success("Course updated successfully!")
            # Reset the success flag after showing
            st.session_state.show_success = False
            time.sleep(1)  # Show the message for 1 second
            st.experimental_rerun()
        
    elif st.session_state.action == "Add Course":
        st.header("Add New Course")
        
        code = st.text_input("Course Code")
        name = st.text_input("Course Name")
        description = st.text_area("Description")
        prerequisites = st.text_input("Prerequisites (comma-separated)")
        corequisites = st.text_input("Co-requisites (comma-separated)")
        credit_hours = st.number_input("Credit Hours", min_value=1, max_value=4, value=3)
        semester = st.selectbox("Semester Offered", ["FALL", "SPRING", "BOTH"])
        
        if st.button("Add Course"):
            if not code or not name or not description:
                st.error("Please fill in all required fields!")
                return
                
            new_course = pd.DataFrame({
                'Code': [code],
                'Course Name': [name],
                'Description': [description],
                'prerequisite': [prerequisites],
                'Co-requisites': [corequisites],
                'CH': [credit_hours],
                'Semester Offered': [semester]
            })
            
            courses_df = pd.concat([courses_df, new_course], ignore_index=True)
            save_courses(courses_df)
            st.success("Course added successfully!")
            time.sleep(1)
            st.session_state.action = "View Courses"
            st.experimental_rerun()
            
    elif st.session_state.action == "Edit Course":
        st.header("Edit Course")
        
        course_to_edit = st.selectbox("Select Course to Edit", courses_df['Code'].tolist())
        if course_to_edit:
            course_data = courses_df[courses_df['Code'] == course_to_edit].iloc[0]
            
            name = st.text_input("Course Name", value=course_data['Course Name'])
            description = st.text_area("Description", value=course_data['Description'])
            prerequisites = st.text_input("Prerequisites", value=course_data['prerequisite'] if pd.notna(course_data['prerequisite']) else "")
            corequisites = st.text_input("Co-requisites", value=course_data['Co-requisites'] if pd.notna(course_data['Co-requisites']) else "")
            
            try:
                current_ch = int(float(course_data['CH']))
            except (ValueError, TypeError):
                current_ch = 3
                
            credit_hours = st.number_input("Credit Hours", min_value=1, max_value=4, value=current_ch)
            
            semester_options = ["FALL", "SPRING", "BOTH"]
            current_semester = course_data['Semester Offered']
            try:
                semester_index = semester_options.index(current_semester)
            except ValueError:
                semester_index = 0
                
            semester = st.selectbox("Semester Offered", semester_options, index=semester_index)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes"):
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'Course Name'] = name
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'Description'] = description
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'prerequisite'] = prerequisites
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'Co-requisites'] = corequisites
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'CH'] = credit_hours
                    courses_df.loc[courses_df['Code'] == course_to_edit, 'Semester Offered'] = semester
                    
                    save_courses(courses_df)
                    st.session_state.show_success = True
                    st.session_state.action = "View Courses"
                    st.experimental_rerun()
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.action = "View Courses"
                    st.experimental_rerun()
    
    elif st.session_state.action == "Delete Course":
        st.header("Delete Course")
        
        course_to_delete = st.selectbox("Select Course to Delete", courses_df['Code'].tolist())
        
        if st.button("Delete Course"):
            courses_df = courses_df[courses_df['Code'] != course_to_delete]
            save_courses(courses_df)
            st.success(f"Course {course_to_delete} deleted successfully!")
            time.sleep(1)
            st.session_state.action = "View Courses"
            st.experimental_rerun()
    
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.experimental_rerun()

def main():
    if not st.session_state.admin_logged_in:
        show_admin_login()
    else:
        show_admin_dashboard()

if __name__ == "__main__":
    main() 