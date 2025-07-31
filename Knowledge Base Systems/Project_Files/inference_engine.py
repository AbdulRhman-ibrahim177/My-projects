from experta import *
from knowledge_base import KnowledgeBase
from explanation_system import ExplanationSystem
from typing import List, Set, Dict, Tuple
import pandas as pd

class Student(Fact):
    """Student information"""
    pass

class Course(Fact):
    """Course information"""
    pass

class Recommendation(Fact):
    """Course recommendation"""
    pass

class CourseAdvisor(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.kb = KnowledgeBase()
        self.explanation_system = ExplanationSystem()
        self.failed_recommendations = []  # Separate list for failed courses
        self.regular_recommendations = []  # Separate list for regular courses
        self.current_courses = set()
        self.failed_courses_recommended = set()
        
    @DefFacts()
    def _initial_facts(self):
        yield Fact(engine_started=True)
        
    @Rule(Fact(engine_started=True),
          Student(semester=MATCH.semester,
                 cgpa=MATCH.cgpa,
                 passed_courses=MATCH.passed,
                 failed_courses=MATCH.failed))
    def initialize_recommendations(self, semester, cgpa, passed, failed):
        """Initialize the recommendation process"""
        self.credit_limit = self.kb.get_credit_limit(cgpa)
        self.current_credits = 0
        self.current_courses = set()
        self.failed_courses_recommended = set()
        
        # Store student info for explanations
        self.student_info = {
            'semester': semester,
            'cgpa': cgpa,
            'passed_courses': set(passed),
            'failed_courses': set(failed)
        }
        
        # First process all failed courses
        for course in failed:
            self.declare(Course(code=course, type='failed', priority=1))
            
        # Then process available courses
        available_courses = self.kb.get_available_courses(semester)
        for course in available_courses:
            if course not in passed and course not in failed:
                self.declare(Course(code=course, type='available', priority=2))
                
    @Rule(Course(code=MATCH.code, type='failed', priority=1))
    def process_failed_courses(self, code):
        """Rule to process failed courses first"""
        if code not in self.failed_courses_recommended:
            # Add to failed recommendations list without checking credits yet
            self.failed_recommendations.append(code)
            self.failed_courses_recommended.add(code)
                
    @Rule(Course(code=MATCH.code, type='available', priority=2))
    def process_available_courses(self, code):
        """Rule to process regular courses"""
        if code not in self.current_courses and code not in self.student_info['failed_courses']:
            # Add to regular recommendations list without checking credits yet
            self.regular_recommendations.append(code)

def get_course_recommendations(semester: str, cgpa: float, 
                             passed_courses: List[str], 
                             failed_courses: List[str]) -> Tuple[List[str], Dict, int]:
    """
    Get course recommendations based on student information
    
    Returns:
        Tuple containing:
        - List of recommended course codes
        - Dictionary of explanations
        - Total credit hours
    """
    engine = CourseAdvisor()
    engine.reset()
    engine.declare(Student(semester=semester,
                         cgpa=cgpa,
                         passed_courses=passed_courses,
                         failed_courses=failed_courses))
    engine.run()
    
    recommended_courses = []
    total_credits = 0
    credit_limit = engine.kb.get_credit_limit(cgpa)
    
    # First, try to add ALL failed courses that fit within credit limit
    for code in engine.failed_recommendations:
        course_credits = engine.kb.get_credit_hours(code)
        if total_credits + course_credits <= credit_limit:
            recommended_courses.append(code)
            total_credits += course_credits
            engine.current_courses.add(code)
    
    # Only if there are credits remaining, consider regular courses
    if total_credits < credit_limit:
        for code in engine.regular_recommendations:
            course_credits = engine.kb.get_credit_hours(code)
            # Check credit limit and course availability
            if (total_credits + course_credits <= credit_limit and
                engine.kb.is_course_available(code, semester, 
                                           set(passed_courses), 
                                           engine.current_courses)):
                recommended_courses.append(code)
                total_credits += course_credits
                engine.current_courses.add(code)
    
    # Generate detailed explanations
    explanations = engine.explanation_system.get_detailed_recommendations_explanation(
        recommended_courses,
        semester,
        cgpa,
        set(passed_courses),
        set(failed_courses),
        engine.current_courses
    )
            
    return recommended_courses, explanations, total_credits