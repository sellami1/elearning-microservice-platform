from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"


# User DTO - Data Transfer Object from User Microservice
class UserDTO(BaseModel):
    """User Data Transfer Object (from User microservice)"""
    id: int
    email: EmailStr
    role: UserRole
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True


# Course Schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(default=0.0, ge=0)


class CourseCreate(CourseBase):
    instructor_id: int


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)


class Course(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseWithLessonsAndFeedbacks(Course):
    lessons: Optional[list["Lesson"]] = []
    feedbacks: Optional[list["Feedback"]] = []
    enrollment_count: Optional[int] = 0


# Lesson Schemas
class LessonBase(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    position: int = Field(default=0, ge=0)


class LessonCreate(LessonBase):
    course_id: int


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    position: Optional[int] = Field(default=None, ge=0)


class Lesson(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    user_id: int
    course_id: int


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None


class Feedback(FeedbackBase):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithUser(Feedback):
    user: Optional[UserDTO] = None


# Enrollment Schemas
class EnrollmentBase(BaseModel):
    completion_percentage: float = Field(default=0.0, ge=0, le=100)


class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int


class EnrollmentUpdate(BaseModel):
    completion_percentage: Optional[float] = Field(default=None, ge=0, le=100)


class Enrollment(EnrollmentBase):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EnrollmentWithCourseAndUser(Enrollment):
    course: Optional[Course] = None
    user: Optional[UserDTO] = None


# Update forward references
UserDTO.model_rebuild()
