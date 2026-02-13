from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class EnrollmentBase(BaseModel):
    """Base enrollment schema"""
    course_id: uuid.UUID
    user_id: str  # String representation of MongoDB ObjectId from User Service
    completed: bool = False
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID format (MongoDB ObjectId string)"""
        if not v:
            raise ValueError('User ID is required')
        # MongoDB ObjectId is 24 hex characters
        if not isinstance(v, str) or len(v) != 24:
            raise ValueError('Invalid User ID format. Expected 24-character MongoDB ObjectId')
        return v
    
    @validator('progress_percentage')
    def validate_progress(cls, v):
        """Validate progress percentage"""
        if not 0.0 <= v <= 100.0:
            raise ValueError('Progress must be between 0 and 100')
        return round(v, 2)

class EnrollmentCreate(BaseModel):
    """Schema for enrollment creation"""
    course_id: uuid.UUID
    
    class Config:
        # Example of what a request might look like
        json_schema_extra = {
            "example": {
                "course_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class EnrollmentUpdate(BaseModel):
    """Schema for enrollment updates"""
    completed: Optional[bool] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    last_accessed_at: Optional[datetime] = None
    
    @validator('progress_percentage')
    def validate_progress(cls, v):
        """Validate progress percentage on update"""
        if v is not None:
            if not 0.0 <= v <= 100.0:
                raise ValueError('Progress must be between 0 and 100')
            return round(v, 2)
        return v

class EnrollmentInDB(EnrollmentBase):
    """Enrollment schema as stored in database"""
    id: uuid.UUID
    enrolled_at: datetime
    last_accessed_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EnrollmentResponse(EnrollmentInDB):
    """Enrollment response schema"""
    pass

class EnrollmentWithCourse(EnrollmentResponse):
    """Enrollment with course details"""
    course_title: str
    course_thumbnail: Optional[str]
    course_instructor: str
    total_lessons: int = 0
    completed_lessons: int = 0
    
    class Config:
        from_attributes = True

class EnrollmentStats(BaseModel):
    """Enrollment statistics"""
    total_enrollments: int = 0
    active_enrollments: int = 0  # Not completed
    completed_enrollments: int = 0
    average_progress: float = 0.0
    total_courses_enrolled: int = 0

class EnrollmentListResponse(BaseModel):
    """Response for listing enrollments"""
    items: List[EnrollmentWithCourse]
    total: int
    page: int
    size: int
    pages: int
    stats: Optional[EnrollmentStats] = None

class LessonProgressUpdate(BaseModel):
    """Schema for updating lesson progress"""
    lesson_id: uuid.UUID
    completed: bool = True
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_id": "123e4567-e89b-12d3-a456-426614174000",
                "completed": True,
                "time_spent_minutes": 30
            }
        }