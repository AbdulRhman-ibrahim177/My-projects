from typing import List, Dict, Set
from knowledge_base import KnowledgeBase

class ExplanationSystem:
    def __init__(self):
        self.kb = KnowledgeBase()
        
    def get_credit_limit_explanation(self, cgpa: float, credit_limit: int) -> str:
        """Generate explanation for credit hour limit based on CGPA"""
        if cgpa < 2.00:
            return f"Based on your CGPA of {cgpa:.2f}, you are limited to taking a maximum of {credit_limit} credit hours per semester according to university policy."
        elif 2.00 <= cgpa < 3.00:
            return f"With your CGPA of {cgpa:.2f}, you can take up to {credit_limit} credit hours per semester according to university policy."
        else:  # cgpa >= 3.00
            return f"With your excellent CGPA of {cgpa:.2f}, you are eligible to take up to {credit_limit} credit hours per semester according to university policy."
            
    def get_prerequisites_explanation(self, course_code: str, prerequisites: list, passed_courses: set) -> str:
        """Generate explanation for prerequisites"""
        if not prerequisites:
            return "This course has no prerequisites."
            
        met_prereqs = [p for p in prerequisites if p in passed_courses]
        unmet_prereqs = [p for p in prerequisites if p not in passed_courses]
        
        explanation = f"Prerequisites for {course_code}:\n"
        if met_prereqs:
            explanation += f"✓ Met prerequisites: {', '.join(met_prereqs)}\n"
        if unmet_prereqs:
            explanation += f"✗ Missing prerequisites: {', '.join(unmet_prereqs)}"
        return explanation.strip()
        
    def get_corequisites_explanation(self, course_code: str, corequisites: list, 
                                   passed_courses: set, current_courses: set) -> str:
        """Generate explanation for co-requisites"""
        if not corequisites:
            return "This course has no co-requisites."
            
        met_coreqs = [c for c in corequisites if c in passed_courses or c in current_courses]
        unmet_coreqs = [c for c in corequisites if c not in passed_courses and c not in current_courses]
        
        explanation = f"Co-requisites for {course_code}:\n"
        if met_coreqs:
            explanation += f"✓ Met co-requisites: {', '.join(met_coreqs)}\n"
        if unmet_coreqs:
            explanation += f"✗ Missing co-requisites: {', '.join(unmet_coreqs)}"
        return explanation.strip()
        
    def get_semester_explanation(self, course_code: str, semester: str, course_semester: str) -> str:
        """Generate explanation for semester availability"""
        if course_semester == 'BOTH':
            return f"{course_code} is offered in both FALL and SPRING semesters."
        elif course_semester == semester:
            return f"{course_code} is offered in the {semester} semester."
        else:
            return f"{course_code} is only offered in the {course_semester} semester, not in {semester}."
            
    def get_failed_priority_explanation(self, course_code: str) -> str:
        """Generate explanation for failed course priority"""
        return f"⚠️ IMPORTANT: {course_code} is a HIGH PRIORITY recommendation because you previously failed this course. It is strongly recommended to retake this course as soon as possible to improve your academic standing and ensure timely graduation."
        
    def get_detailed_recommendations_explanation(self, recommended_courses: list,
                                              semester: str, cgpa: float,
                                              passed_courses: set,
                                              failed_courses: set,
                                              current_courses: set) -> dict:
        """Generate detailed explanations for course recommendations"""
        explanations = {
            'credit_limit': self.get_credit_limit_explanation(cgpa, self.kb.get_credit_limit(cgpa)),
            'failed_courses_summary': self._get_failed_courses_summary(failed_courses),
            'courses': {}
        }
        
        # Sort courses to show failed courses first
        sorted_courses = sorted(recommended_courses, 
                              key=lambda x: (x not in failed_courses, x))
        
        for course in sorted_courses:
            course_explanations = {
                'failed_priority': self.get_failed_priority_explanation(course) if course in failed_courses else "",
                'prerequisites': self.get_prerequisites_explanation(
                    course, self.kb.get_prerequisites(course), passed_courses
                ),
                'corequisites': self.get_corequisites_explanation(
                    course, self.kb.get_corequisites(course), passed_courses, current_courses
                ),
                'semester': self.get_semester_explanation(
                    course, semester, self.kb.get_semester_offered(course)
                )
            }
            explanations['courses'][course] = course_explanations
            
        return explanations
        
    def _get_failed_courses_summary(self, failed_courses: set) -> str:
        """Generate a summary of failed courses"""
        if not failed_courses:
            return "You have no failed courses to retake."
            
        return f"⚠️ ATTENTION: You have {len(failed_courses)} failed course(s) that need to be retaken: {', '.join(sorted(failed_courses))}. These courses have been given priority in your recommendations." 