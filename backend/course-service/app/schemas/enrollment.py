from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .course import Course
    from .user import UserDTO


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
    course: Optional["Course"] = None
    user: Optional["UserDTO"] = None


# Rebuild models with forward references
EnrollmentWithCourseAndUser.model_rebuild()