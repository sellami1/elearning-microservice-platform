from sqlalchemy import Column, Float, Boolean, ForeignKey, DateTime, UniqueConstraint, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from datetime import datetime
import uuid

class Enrollment(BaseModel):
    __tablename__ = "enrollments"
    
    # User reference
    user_id = Column(String(255), nullable=False, index=True)  # Student user ID
    
    # Foreign keys
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)  # Enrolled course
    
    # Progress tracking
    completed = Column(Boolean, default=False)  # Course completion flag
    progress_percentage = Column(Float, default=0.0)  # Progress percentage (0-100)
    
    # Timestamps
    last_accessed_at = Column(DateTime, default=datetime.utcnow)  # Last access time
    completed_at = Column(DateTime, nullable=True)  # Completion timestamp
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")  # Enrolled course
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course'),  # One enrollment per user per course
    )