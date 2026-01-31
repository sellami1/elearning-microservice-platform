from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Enrollment(Base):
    """Student enrollment model"""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Reference to User microservice
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    completion_percentage = Column(Float, nullable=False, default=0.0)  # 0-100%
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")