from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class Feedback(BaseModel):
    __tablename__ = "feedbacks"
    
    # User reference
    user_id = Column(String(255), nullable=False, index=True)  # Reviewer user ID
    
    # Foreign keys
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)  # Reviewed course
    
    # Feedback content
    rating = Column(Integer, nullable=False)  # Rating (1-5)
    comment = Column(Text, nullable=True)  # Review comment
    
    # Status flags
    is_verified = Column(Boolean, default=False)  # Verified enrollment flag
    is_processed = Column(Boolean, default=False)  # Processed by n8n flag
    
    # Relationships
    course = relationship("Course", back_populates="feedbacks")  # Reviewed course
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course_feedback'),  # One feedback per user per course
    )