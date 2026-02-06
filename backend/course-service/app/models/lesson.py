from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class Lesson(BaseModel):
    __tablename__ = "lessons"
    
    # Foreign keys
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)  # Parent course
    
    # Lesson content
    title = Column(String(255), nullable=False)  # Lesson title
    description = Column(Text, nullable=True)  # Lesson description
    content_type = Column(String(50), nullable=False)  # Type: video, text, pdf, quiz
    content_url = Column(String(500), nullable=True)  # Content file URL
    duration_minutes = Column(Integer, default=0)  # Duration in minutes
    
    # Ordering and visibility
    order_index = Column(Integer, nullable=False, default=0)  # Position in course
    is_preview = Column(Boolean, default=False)  # Free preview flag
    is_published = Column(Boolean, default=True)  # Published flag
    
    # Relationships
    course = relationship("Course", back_populates="lessons")  # Parent course