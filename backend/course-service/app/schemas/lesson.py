from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum
from fastapi import UploadFile
import re

class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    QUIZ = "quiz"
    AUDIO = "audio"
    IMAGE = "image"

class LessonBase(BaseModel):
    """Base lesson schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    duration_minutes: int = Field(0, ge=0)
    order_index: int = Field(0, ge=0)
    is_preview: bool = False
    is_published: bool = True
    
    @validator('title')
    def validate_title(cls, v):
        """Validate lesson title"""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        if len(v.strip()) > 255:
            raise ValueError('Title cannot exceed 255 characters')
        return v.strip()
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        """Validate duration is reasonable"""
        if v < 0:
            raise ValueError('Duration cannot be negative')
        if v > 1440:  # 24 hours max
            raise ValueError('Duration cannot exceed 24 hours (1440 minutes)')
        return v
    
    @validator('order_index')
    def validate_order_index(cls, v):
        """Validate order index"""
        if v < 0:
            raise ValueError('Order index cannot be negative')
        if v > 1000:  # Reasonable limit for lessons per course
            raise ValueError('Order index is too high')
        return v

class LessonCreateForm(LessonBase):
    """Schema for lesson creation via form data (multipart)"""
    course_id: uuid.UUID
    
    @validator('course_id')
    def validate_course_id(cls, v):
        """Validate course ID format"""
        if not v:
            raise ValueError('Course ID is required')
        return v

class LessonCreate(LessonCreateForm):
    """Schema for JSON-based lesson creation (backward compatibility)"""
    content_url: Optional[str] = None  # For direct URL upload

class LessonUpdate(BaseModel):
    """Schema for lesson updates"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None
    is_published: Optional[bool] = None

class LessonInDB(LessonBase):
    """Lesson schema as stored in database"""
    id: uuid.UUID
    course_id: uuid.UUID
    content_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LessonResponse(LessonInDB):
    """Lesson response schema"""
    pass

class LessonListResponse(BaseModel):
    """Response for listing lessons"""
    items: list[LessonResponse]
    total: int
    page: int
    size: int
    pages: int

class LessonUploadResponse(BaseModel):
    """Response for lesson upload"""
    lesson_id: uuid.UUID
    content_url: str
    message: str