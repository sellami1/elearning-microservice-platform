from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class Course(BaseModel):
    __tablename__ = "courses"
    
    # Course information
    title = Column(String(255), nullable=False, index=True)  # Course title
    description = Column(Text, nullable=True)  # Full description
    short_description = Column(String(500), nullable=True)  # Short summary
    price = Column(Float, default=0.0, nullable=False)  # Price (0.0 = free)
    
    # User reference (from User Service)
    instructor_id = Column(String(255), nullable=False, index=True)  # Instructor user ID
    
    # Course metadata
    category = Column(String(100), nullable=True, index=True)  # Main category
    subcategory = Column(String(100), nullable=True)  # Subcategory
    level = Column(String(50), default="beginner")  # Difficulty level
    duration_hours = Column(Integer, default=0)  # Estimated hours
    
    # Media
    thumbnail_url = Column(String(500), nullable=True)  # Thumbnail image URL
    
    # Status flags
    published = Column(Boolean, default=False, index=True)  # Published status
    is_featured = Column(Boolean, default=False)  # Featured flag
    
    # Statistics
    rating = Column(Float, default=0.0)  # Average rating
    total_ratings = Column(Integer, default=0)  # Number of ratings
    total_enrollments = Column(Integer, default=0)  # Number of enrollments
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")  # Course lessons
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")  # Student enrollments
    feedbacks = relationship("Feedback", back_populates="course", cascade="all, delete-orphan")  # Course feedbacks