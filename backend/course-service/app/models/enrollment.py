from sqlalchemy import Column, String, Boolean, Float, ForeignKey, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import BaseModel
import uuid
from datetime import datetime

class Enrollment(BaseModel):
    __tablename__ = "enrollments"
    
    user_id = Column(
        String(24),
        nullable=False,
        index=True
    )
    
    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    enrolled_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    completed = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    progress_percentage = Column(
        Float,
        default=0.0,
        nullable=False
    )
    
    last_accessed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    completed_at = Column(
        DateTime,
        nullable=True
    )
    
    total_time_spent_minutes = Column(
        Integer,
        default=0,
        nullable=False
    )
    
    last_lesson_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    course = relationship(
        "Course",
        back_populates="enrollments",
        lazy="select"
    )
    
    lesson_progresses = relationship(
        "LessonProgress",
        back_populates="enrollment",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'course_id',
            name='unique_user_course_enrollment'
        ),
    )
    
    def __repr__(self):
        return f"<Enrollment User:{self.user_id} Course:{self.course_id}>"
    
    def update_progress(self, db_session, total_lessons, completed_lessons):
        if total_lessons > 0:
            self.progress_percentage = round((completed_lessons / total_lessons) * 100, 2)
            
            if self.progress_percentage >= 100.0:
                self.completed = True
                self.completed_at = datetime.utcnow()
            else:
                self.completed = False
                self.completed_at = None
            
            db_session.add(self)
            return True
        return False

class LessonProgress(BaseModel):
    __tablename__ = "lesson_progress"
    
    enrollment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    lesson_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    completed = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    time_spent_minutes = Column(
        Integer,
        default=0,
        nullable=False
    )
    
    last_accessed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    completed_at = Column(
        DateTime,
        nullable=True
    )
    
    enrollment = relationship(
        "Enrollment",
        back_populates="lesson_progresses",
        lazy="select"
    )
    
    __table_args__ = (
        UniqueConstraint(
            'enrollment_id',
            'lesson_id',
            name='unique_enrollment_lesson_progress'
        ),
    )
    
    def __repr__(self):
        status = "completed" if self.completed else "in progress"
        return f"<LessonProgress Lesson:{self.lesson_id} {status}>"