# AIU CSE Course Registration Advisor

A Knowledge-Based System (KBS) for assisting Computer Science and Engineering (CSE) students at Alamein International University (AIU) in selecting courses for registration.

## Features

- Student registration and login system
- Course recommendation based on:
  - Current semester
  - CGPA
  - Passed courses
  - Failed courses
- Admin dashboard for managing course data
- Intelligent inference engine using Experta
- Clear explanations for course recommendations

## Setup Instructions

1. Install Python 3.8 or higher if not already installed

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the student application:
   ```bash
   streamlit run app.py
   ```

4. Run the admin dashboard in a separate terminal:
   ```bash
   streamlit run admin_app.py
   ```

## Admin Access

Default admin credentials:
- Username: admin
- Password: admin123

## Project Structure

- `app.py`: Main student application
- `admin_app.py`: Admin dashboard for managing courses
- `knowledge_base.py`: Course data and rules management
- `inference_engine.py`: Experta-based recommendation engine
- `Courses.csv`: Course database
- `requirements.txt`: Project dependencies

## Usage

1. Student Application:
   - Register with your AIU email (@aiu.edu.eg)
   - Login with your credentials
   - Enter your academic information
   - Get personalized course recommendations

2. Admin Dashboard:
   - View all courses
   - Add new courses
   - Edit existing courses
   - Delete courses

## Notes

- The system uses a simple JSON file for user management (not suitable for production)
- Course recommendations follow AIU's credit hour and prerequisite policies
- Failed courses are prioritized in recommendations
- The system ensures compliance with semester availability and prerequisites 