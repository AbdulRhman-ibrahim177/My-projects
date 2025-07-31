import streamlit as st
import pandas as pd
from PIL import Image
import json
import os
import base64
import requests
from inference_engine import get_course_recommendations
from knowledge_base import KnowledgeBase
from typing import List, Set

# Performance optimization: Cache data loading
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

@st.cache_data
def load_courses():
    return pd.read_csv('Courses.csv')

@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Initialize users if not exists
if not os.path.exists('users.json'):
    save_users({})

# Page config with improved performance settings
st.set_page_config(
    page_title="AIU CSE Course Advisor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Load and cache the CSS
css = """
    <style>
        /* Modern Color Palette */
        :root {
            --primary: #003366;
            --secondary: #8B0000;
            --accent: #E8C766;
            --background: #0A192F;
            --card-bg: rgba(255, 255, 255, 0.1);
            --text: #E2E8F0;
            --text-light: #94A3B8;
            --success: #2E7D32;
            --warning: #FF8F00;
        }

        /* Hide Deploy and menu */
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 0rem;}
        
        /* Animated Background */
        .stApp {
            background: linear-gradient(-45deg, #003366, #1B3B6F, #21284F);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            min-height: 100vh;
        }

        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* Glassmorphism Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px 0 rgba(0, 51, 102, 0.37);
            transition: all 0.3s ease;
        }

        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 51, 102, 0.47);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Typography */
        body {
            font-family: 'Poppins', sans-serif;
            color: var(--text);
            line-height: 1.7;
        }

        /* Modern Headings with Animation */
        h1 {
            color: white !important;
            font-size: 3rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin: 2rem 0 !important;
            position: relative;
            background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: titleAnimation 3s ease-in-out infinite;
        }

        @keyframes titleAnimation {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        h2, h3 {
            color: white !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
        }

        /* Floating Header */
        .header {
            background: rgba(0, 51, 102, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1rem 2rem;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            animation: slideDown 0.5s ease;
        }

        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }

        /* Animated Logo */
        .logo-left img {
            height: 50px;
            filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Modern Navigation */
        .tabs {
            display: flex;
            gap: 1.5rem;
        }

        .tabs a {
            text-decoration: none;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            background: rgba(0, 51, 102, 0.3);
        }

        .tabs a::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }

        .tabs a:hover::before {
            opacity: 1;
        }

        .tabs a:hover {
            transform: translateY(-3px);
            color: white;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }

        /* Animated Buttons */
        div.stButton > button {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }

        div.stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, var(--secondary), var(--accent));
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }

        div.stButton > button:hover::before {
            opacity: 1;
        }

        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        /* Modern Form Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            background: rgba(0, 51, 102, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(232, 199, 102, 0.2) !important;
            transform: translateY(-2px);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            background: rgba(0, 51, 102, 0.1);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(var(--primary), var(--secondary));
            border-radius: 5px;
        }

        /* Message Boxes */
        .warning-message, .success-message {
            background: rgba(0, 51, 102, 0.1);
            backdrop-filter: blur(5px);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .warning-message {
            border-color: var(--warning);
        }

        .success-message {
            border-color: var(--success);
        }

        /* Dataframe Styling */
        .dataframe {
            background: rgba(0, 51, 102, 0.1) !important;
            backdrop-filter: blur(5px);
            border-radius: 12px !important;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        .dataframe thead th {
            background: rgba(0, 51, 102, 0.3) !important;
            color: white !important;
            padding: 1rem !important;
            font-weight: 600;
        }

        .dataframe tbody tr {
            transition: all 0.3s ease;
        }

        .dataframe tbody tr:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.01);
        }

        /* Loading Animation */
        .stProgress > div > div > div {
            background: linear-gradient(45deg, var(--primary), var(--secondary)) !important;
        }

        /* Responsive Design */
        @media screen and (max-width: 768px) {
            .header {
                flex-direction: column;
                padding: 1rem;
            }

            .tabs {
                flex-wrap: wrap;
                justify-content: center;
                margin-top: 1rem;
            }

            .tabs a {
                width: calc(50% - 1rem);
                text-align: center;
            }

            h1 {
                font-size: 2rem !important;
            }

            .glass-card {
                padding: 1.5rem;
                margin: 1rem 0;
            }
        }

        /* Custom Animations */
        .fade-in {
            animation: fadeIn 1s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Card Grid Layout */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem 0;
        }

        /* Floating Elements Animation */
        .floating {
            animation: floating 3s ease-in-out infinite;
        }

        @keyframes floating {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
    </style>
"""

st.markdown(css, unsafe_allow_html=True)

def show_welcome_page():
    # Header with logo
    try:
        logo_path = "university_logo.png"
        logo_base64 = base64.b64encode(open(logo_path, "rb").read()).decode()
        
        st.markdown(f"""
            <div class="header">
                <div class="logo-left floating">
                    <img src="data:image/png;base64,{logo_base64}">
                </div>
                <div class="tabs">
                    <a href="#" class="fade-in">🏠 Home</a>
                    <a href="#" class="fade-in">ℹ️ About</a>
                    <a href="#" class="fade-in">⚙️ Settings</a>
                    <a href="#" class="fade-in">❓ Help</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("""
            <div class="header">
                <div class="tabs">
                    <a href="#" class="fade-in">🏠 Home</a>
                    <a href="#" class="fade-in">ℹ️ About</a>
                    <a href="#" class="fade-in">⚙️ Settings</a>
                    <a href="#" class="fade-in">❓ Help</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Add spacing for header
    st.markdown("<div style='padding-top: 100px;'></div>", unsafe_allow_html=True)
    
    # Welcome title
    st.markdown("<h1 class='fade-in'>Welcome to AIU CSE Course Advisor</h1>", unsafe_allow_html=True)
    
    # Feature Cards using Streamlit columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="glass-card fade-in" style="height: 100%;">
                <h3 style="color: white; text-align: center;">🎯 Smart Course Planning</h3>
                <p style="color: var(--text-light); text-align: center;">Get personalized course recommendations based on your academic history and goals.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card fade-in" style="height: 100%;">
                <h3 style="color: white; text-align: center;">📊 Progress Tracking</h3>
                <p style="color: var(--text-light); text-align: center;">Monitor your academic progress and stay on track with your degree requirements.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card fade-in" style="height: 100%;">
                <h3 style="color: white; text-align: center;">🤖 AI-Powered</h3>
                <p style="color: var(--text-light); text-align: center;">Advanced algorithms ensure optimal course selection for your academic success.</p>
            </div>
        """, unsafe_allow_html=True)

    # Lottie Animation
    with st.spinner('Loading animation...'):
        try:
            from streamlit_lottie import st_lottie
            lottie_url = "https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json"
            lottie_animation = load_lottie_url(lottie_url)
            if lottie_animation:
                st.markdown("""
                    <div class="glass-card fade-in" style="text-align: center; margin: 2rem 0;">
                """, unsafe_allow_html=True)
                st_lottie(lottie_animation, height=250)
                st.markdown("</div>", unsafe_allow_html=True)
        except:
            pass

    # Login/Signup Section
    st.markdown("""
        <div class="glass-card fade-in" style="text-align: center; padding: 2rem;">
            <h2 style="color: white; margin-bottom: 1.5rem;">Ready to Get Started?</h2>
        </div>
    """, unsafe_allow_html=True)

    # Login/Signup Buttons using Streamlit columns
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col2:
        if st.button("🔐 Login", key="login_btn", use_container_width=True):
            st.session_state.page = "login"
    
    with col3:
        if st.button("📝 Sign Up", key="signup_btn", use_container_width=True):
            st.session_state.page = "signup"

def show_advisor_interface():
    st.markdown("<div class='advisor-container'>", unsafe_allow_html=True)
    
    # Your existing advisor interface code here
    st.title("Course Advisor System")
    
    # Input fields
    st.markdown("<div class='data-input'>", unsafe_allow_html=True)
    semester = st.selectbox("Select Semester", ["FALL", "SPRING"])
    cgpa = st.number_input("Enter your CGPA", min_value=0.000, max_value=4.000, value=2.000, step=0.001, format="%.3f")
    
    # Get all courses for multiselect
    kb = KnowledgeBase()
    all_courses = kb.get_all_courses()
    course_codes = all_courses['Code'].tolist()
    
    passed_courses = st.multiselect("Select Passed Courses", course_codes)
    failed_courses = st.multiselect("Select Failed Courses", course_codes)
    
    if st.button("Get Recommendations"):
        recommendations, explanations, total_credits = get_course_recommendations(
            semester, cgpa, passed_courses, failed_courses
        )
        
        st.markdown("<div class='recommendation-box'>", unsafe_allow_html=True)
        st.subheader("Recommendations:")
        
        if not recommendations:
            st.warning("No courses recommended. This could be due to credit limits, prerequisites, or semester availability.")
        else:
            st.write(f"Total recommended credits: {total_credits}")
            st.write("Credit limit explanation:", explanations['credit_limit'])
            
            if failed_courses:
                st.markdown("<div class='warning-message'>", unsafe_allow_html=True)
                st.write("Failed courses summary:", explanations['failed_courses_summary'])
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("\nRecommended Courses:")
            for course in recommendations:
                st.write(f"\nCourse: {course}")
                course_explanations = explanations['courses'][course]
                
                if course_explanations['failed_priority']:
                    st.warning(course_explanations['failed_priority'])
                    
                st.write("Prerequisites:", course_explanations['prerequisites'])
                st.write("Co-requisites:", course_explanations['corequisites'])
                st.write("Semester:", course_explanations['semester'])
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_login():
    # Add spacing for header
    st.markdown("<div style='padding-top: 100px;'></div>", unsafe_allow_html=True)
    
    # Title
    st.markdown("<h1 class='fade-in'>Login to Your Account</h1>", unsafe_allow_html=True)
    
    # Create columns for centering the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome card
        st.markdown("""
            <div class="glass-card fade-in">
                <div style="text-align: center;">
                    <div class="floating">
                        <h2 style="color: white; margin-bottom: 1.5rem;">🔐 Welcome Back!</h2>
                        <p style="color: var(--text-light);">Please enter your credentials to continue</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.container():
            st.markdown("""
                <div class="glass-card fade-in" style="margin-top: 1rem;">
                    <div style="padding: 1rem;">
            """, unsafe_allow_html=True)
            
            student_id = st.text_input("Student ID", placeholder="Enter your student ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚪 Login", key="login_submit", use_container_width=True):
                    users = load_users()
                    if student_id in users and users[student_id]['password'] == password:
                        st.session_state.logged_in = True
                        st.session_state.student_id = student_id
                        st.session_state.page = 'dashboard'
                        st.markdown("""
                            <div class="success-message fade-in">
                                ✅ Login successful! Redirecting...
                            </div>
                        """, unsafe_allow_html=True)
                        st.experimental_rerun()
                    else:
                        st.markdown("""
                            <div class="warning-message fade-in">
                                ❌ Invalid credentials! Please try again.
                            </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🏠 Back", key="back_to_welcome", use_container_width=True):
                    st.session_state.page = 'welcome'
                    st.experimental_rerun()
            
            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Additional help text
            st.markdown("""
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="color: var(--text-light);">Don't have an account? 
                        <span style="color: var(--accent); cursor: pointer;" 
                              onclick="document.querySelector('#signup_btn').click()">
                            Sign up here
                        </span>
                    </p>
                </div>
            """, unsafe_allow_html=True)

def show_signup():
    # Add spacing for header
    st.markdown("<div style='padding-top: 100px;'></div>", unsafe_allow_html=True)
    
    # Title
    st.markdown("<h1 class='fade-in'>Create Your Account</h1>", unsafe_allow_html=True)
    
    # Create columns for centering the signup card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome card
        st.markdown("""
            <div class="glass-card fade-in">
                <div style="text-align: center;">
                    <div class="floating">
                        <h2 style="color: white; margin-bottom: 1.5rem;">📝 Join Us!</h2>
                        <p style="color: var(--text-light);">Create your account to get personalized course recommendations</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Signup form
        with st.container():
            st.markdown("""
                <div class="glass-card fade-in" style="margin-top: 1rem;">
                    <div style="padding: 1rem;">
            """, unsafe_allow_html=True)
            
            student_id = st.text_input("Student ID", placeholder="Enter your student ID")
            email = st.text_input("University Email", placeholder="Enter your AIU email address")
            password = st.text_input("Password", type="password", placeholder="Create a strong password")
            
            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ Sign Up", key="signup_submit", use_container_width=True):
                    if not student_id or not email or not password:
                        st.markdown("""
                            <div class="warning-message fade-in">
                                ❌ Please fill in all fields!
                            </div>
                        """, unsafe_allow_html=True)
                        return
                        
                    if not email.endswith('@aiu.edu.eg'):
                        st.markdown("""
                            <div class="warning-message fade-in">
                                ❌ Please use your AIU email address!
                            </div>
                        """, unsafe_allow_html=True)
                        return
                        
                    users = load_users()
                    if student_id in users:
                        st.markdown("""
                            <div class="warning-message fade-in">
                                ❌ Student ID already exists!
                            </div>
                        """, unsafe_allow_html=True)
                        return
                        
                    users[student_id] = {
                        'email': email,
                        'password': password
                    }
                    save_users(users)
                    st.markdown("""
                        <div class="success-message fade-in">
                            ✅ Registration successful! Please login.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.page = 'login'
                    st.experimental_rerun()
            
            with col2:
                if st.button("🏠 Back", key="back_to_welcome", use_container_width=True):
                    st.session_state.page = 'welcome'
                    st.experimental_rerun()
            
            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Additional help text
            st.markdown("""
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="color: var(--text-light);">Already have an account? 
                        <span style="color: var(--accent); cursor: pointer;" 
                              onclick="document.querySelector('#login_btn').click()">
                            Login here
                        </span>
                    </p>
                </div>
            """, unsafe_allow_html=True)

def show_course_details(course_code: str, course_data: dict, courses_df: pd.DataFrame):
    """Display detailed information about a course"""
    course = courses_df[courses_df['Code'] == course_code].iloc[0]
    
    with st.expander(f"📚 {course_code} - {course['Course Name']}"):
        st.write(f"**Description:** {course['Description']}")
        st.write(f"**Credit Hours:** {course['CH']}")
        
        # Display explanations
        if course_data['failed_priority']:
            st.warning(course_data['failed_priority'])
            
        st.write("**Prerequisites:**")
        st.write(course_data['prerequisites'])
        
        st.write("**Co-requisites:**")
        st.write(course_data['corequisites'])
        
        st.write("**Semester Availability:**")
        st.write(course_data['semester'])

def show_dashboard():
    st.title("Student Dashboard")
    
    # Load courses data
    courses_df = pd.read_csv('Courses.csv')
    
    # Input fields
    st.header("Enter Your Information")
    semester = st.selectbox("Current Semester", ["FALL", "SPRING"])
    cgpa = st.number_input("CGPA", min_value=0.000, max_value=4.000, value=2.000, step=0.001, format="%.3f")
    
    # Multi-select for passed and failed courses
    all_courses = courses_df['Code'].tolist()
    passed_courses = st.multiselect("Select Passed Courses", all_courses)
    failed_courses = st.multiselect("Select Failed Courses", all_courses)
    
    if st.button("Get Recommendations"):
        from inference_engine import get_course_recommendations
        
        recommendations, explanations, total_credits = get_course_recommendations(
            semester=semester,
            cgpa=cgpa,
            passed_courses=passed_courses,
            failed_courses=failed_courses
        )
        
        # Display credit limit explanation
        st.info(explanations['credit_limit'])
        
        if recommendations:
            st.header("Recommended Courses")
            
            # Create a DataFrame for recommended courses
            recommended_data = []
            for code in recommendations:
                course = courses_df[courses_df['Code'] == code].iloc[0]
                recommended_data.append({
                    'Code': code,
                    'Course Name': course['Course Name'],
                    'Credit Hours': course['CH']
                })
            
            recommendations_df = pd.DataFrame(recommended_data)
            st.dataframe(recommendations_df)
            
            st.write(f"**Total Credit Hours:** {total_credits}")
            
            # Display detailed explanations for each course
            st.header("Course Details and Explanations")
            for course_code in recommendations:
                show_course_details(course_code, explanations['courses'][course_code], courses_df)
                
        else:
            st.warning("No courses recommended. This could be due to credit limits, prerequisites, or semester availability.")
        
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = 'welcome'
        st.experimental_rerun()

# Main app logic
def main():
    if st.session_state.page == 'welcome':
        show_welcome_page()
    elif st.session_state.page == 'login':
        show_login()
    elif st.session_state.page == 'signup':
        show_signup()
    elif st.session_state.page == 'dashboard' and st.session_state.logged_in:
        show_dashboard()
    else:
        show_welcome_page()

if __name__ == "__main__":
    main() 