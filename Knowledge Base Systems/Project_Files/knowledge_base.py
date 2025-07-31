import pandas as pd
from typing import List, Dict, Set

class KnowledgeBase:
    def __init__(self, courses_file: str = 'Courses.csv'):
        self.courses_df = pd.read_csv(courses_file)
        self.courses_df.fillna('', inplace=True)
        
    def get_all_courses(self) -> pd.DataFrame:
        return self.courses_df
        
    def get_course_by_code(self, code: str) -> Dict:
        course = self.courses_df[self.courses_df['Code'] == code]
        if len(course) == 0:
            return None
        return course.iloc[0].to_dict()
        
    def get_prerequisites(self, course_code: str) -> List[str]:
        course = self.courses_df[self.courses_df['Code'] == course_code]
        if course.empty or pd.isna(course.iloc[0]['prerequisite']):
            return []
        prereqs = course.iloc[0]['prerequisite']
        if isinstance(prereqs, str):
            return [p.strip() for p in prereqs.split(',') if p.strip()]
        return []
        
    def get_corequisites(self, course_code: str) -> List[str]:
        course = self.courses_df[self.courses_df['Code'] == course_code]
        if course.empty or pd.isna(course.iloc[0]['Co-requisites']):
            return []
        coreqs = course.iloc[0]['Co-requisites']
        if isinstance(coreqs, str):
            return [c.strip() for c in coreqs.split(',') if c.strip()]
        return []
        
    def get_credit_hours(self, course_code: str) -> int:
        course = self.courses_df[self.courses_df['Code'] == course_code]
        if not course.empty:
            try:
                return int(float(course.iloc[0]['CH']))
            except (ValueError, TypeError):
                return 3  # Default to 3 if conversion fails
        return 3
        
    def get_semester_offered(self, course_code: str) -> str:
        course = self.courses_df[self.courses_df['Code'] == course_code]
        return course.iloc[0]['Semester Offered'] if not course.empty else None
        
    def get_available_courses(self, semester: str, failed_courses: Set[str] = None) -> List[str]:
        """Get available courses, prioritizing failed courses if provided"""
        available_courses = []
        
        # Always add failed courses first, regardless of semester
        if failed_courses:
            available_courses.extend(list(failed_courses))
            
        # Then add semester-specific courses
        semester_mask = (self.courses_df['Semester Offered'] == semester) | (self.courses_df['Semester Offered'] == 'BOTH')
        semester_courses = self.courses_df[semester_mask]['Code'].tolist()
        
        # Add semester courses that aren't failed courses
        available_courses.extend([c for c in semester_courses if c not in available_courses])
        
        return available_courses
        
    def get_credit_limit(self, cgpa: float) -> int:
        """Get maximum allowed credit hours based on CGPA"""
        if cgpa < 2.00:
            return 12
        elif 2.00 <= cgpa < 3.00:
            return 20  # Strict limit for CGPA between 2.00 and 3.00
        else:  # cgpa >= 3.00
            return 22
            
    def check_prerequisites_met(self, course_code: str, passed_courses: Set[str]) -> bool:
        prerequisites = self.get_prerequisites(course_code)
        if not prerequisites:
            return True
        return all(prereq in passed_courses for prereq in prerequisites)
        
    def check_corequisites_available(self, course_code: str, passed_courses: Set[str], current_courses: Set[str]) -> bool:
        corequisites = self.get_corequisites(course_code)
        if not corequisites:
            return True
        return all(coreq in passed_courses or coreq in current_courses for coreq in corequisites)
        
    def is_course_available(self, course_code: str, semester: str, passed_courses: Set[str], current_courses: Set[str], is_failed_course: bool = False) -> bool:
        """Check if a course is available to take"""
        course = self.courses_df[self.courses_df['Code'] == course_code]
        if not course.empty:
            # For failed courses, ignore semester restrictions and be lenient with prerequisites
            if is_failed_course:
                return True  # Always allow failed courses to be retaken
            
            # For regular courses, apply normal restrictions
            semester_offered = course.iloc[0]['Semester Offered']
            if semester_offered not in [semester, 'BOTH']:
                return False
            
            prereqs_met = self.check_prerequisites_met(course_code, passed_courses)
            coreqs_available = self.check_corequisites_available(course_code, passed_courses, current_courses)
            
            return prereqs_met and coreqs_available
        return False 