from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    QUIZ = "quiz"

class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    duration_minutes: int = Field(0, ge=0)
    order_index: int = Field(0, ge=0)
    is_preview: bool = False
    is_published: bool = True

class LessonCreate(LessonBase):
    course_id: uuid.UUID
    content_url: Optional[str] = None  # For direct URL upload

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None
    is_published: Optional[bool] = None

class LessonInDB(LessonBase):
    id: uuid.UUID
    course_id: uuid.UUID
    content_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LessonResponse(LessonInDB):
    pass