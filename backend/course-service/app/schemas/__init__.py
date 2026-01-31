"""Schemas module initialization"""
from app.schemas.user import UserRole, UserDTO
from app.schemas.course import CourseBase, CourseCreate, CourseUpdate, Course, CourseWithLessonsAndFeedbacks
from app.schemas.lesson import LessonBase, LessonCreate, LessonUpdate, Lesson
from app.schemas.feedback import FeedbackBase, FeedbackCreate, FeedbackUpdate, Feedback, FeedbackWithUser
from app.schemas.enrollment import EnrollmentBase, EnrollmentCreate, EnrollmentUpdate, Enrollment, EnrollmentWithCourseAndUser

__all__ = [
    "UserRole",
    "UserDTO",
    "CourseBase", "CourseCreate", "CourseUpdate", "Course", "CourseWithLessonsAndFeedbacks",
    "LessonBase", "LessonCreate", "LessonUpdate", "Lesson",
    "FeedbackBase", "FeedbackCreate", "FeedbackUpdate", "Feedback", "FeedbackWithUser",
    "EnrollmentBase", "EnrollmentCreate", "EnrollmentUpdate", "Enrollment", "EnrollmentWithCourseAndUser",
]
