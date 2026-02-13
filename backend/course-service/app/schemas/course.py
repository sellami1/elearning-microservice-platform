from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum
import re

class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# Base schema for common course fields
class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: float = Field(0.0, ge=0.0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    level: CourseLevel = CourseLevel.BEGINNER
    duration_hours: int = Field(0, ge=0)
    published: bool = False
    is_featured: bool = False

class CourseCreateForm(CourseBase):
    """Schema for course creation via form data (multipart)"""
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is reasonable"""
        if v < 0:
            raise ValueError('Price cannot be negative')
        if v > 10000:  # Reasonable maximum
            raise ValueError('Price cannot exceed $10,000')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title has no special characters that could cause issues"""
        if not re.match(r'^[a-zA-Z0-9\s\-_,.!?\'"()&]+$', v):
            raise ValueError('Title contains invalid characters')
        return v.strip()

class CourseUpdateForm(BaseModel):
    """Schema for course updates via form data (multipart)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0.0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    level: Optional[CourseLevel] = None
    duration_hours: Optional[int] = Field(None, ge=0)
    published: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is reasonable"""
        if v is not None:
            if v < 0:
                raise ValueError('Price cannot be negative')
            if v > 10000:  # Reasonable maximum
                raise ValueError('Price cannot exceed $10,000')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title has no special characters that could cause issues"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\s\-_,.!?\'"()&]+$', v):
                raise ValueError('Title contains invalid characters')
            return v.strip()
        return v

class CourseInDB(CourseBase):
    id: uuid.UUID
    instructor_id: str
    thumbnail_url: Optional[str]
    rating: float
    total_ratings: int
    total_enrollments: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CourseUpdateResponse(CourseInDB):
    """Response schema for course update"""
    thumbnail_updated: bool = False
    
    class Config:
        from_attributes = True


class CourseResponse(CourseInDB):
    pass

class CourseListResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    size: int
    pages: int