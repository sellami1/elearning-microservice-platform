from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Course(Base):
    """Course model"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    instructor_id = Column(Integer, nullable=False)  # Reference to User microservice
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Lesson model"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    video_url = Column(String(255), nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")


class Feedback(Base):
    """Course feedback model"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Reference to User microservice
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="feedbacks")


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
