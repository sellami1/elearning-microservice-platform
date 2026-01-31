from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .lesson import Lesson
    from .feedback import Feedback


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


# Rebuild models with forward references
CourseWithLessonsAndFeedbacks.model_rebuild()