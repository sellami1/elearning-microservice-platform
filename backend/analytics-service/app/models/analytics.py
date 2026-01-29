import enum
import uuid
from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..database import Base

SCHEMA_NAME = "public"

class EventType(str, enum.Enum):
    course_view = "course_view"
    course_enroll = "course_enroll"

class UserRole(str, enum.Enum):
    learner = "learner"
    instructor = "instructor"

class AnalyticsEvent(Base):
    """
    Stores raw events for every course view or enrollment.
    """
    __tablename__ = "analytics_events"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(Enum(EventType, name="event_type_enum", schema=SCHEMA_NAME), nullable=False)
    user_id = Column(String(24), nullable=True)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(Enum(UserRole, name="user_role_enum", schema=SCHEMA_NAME), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CourseDailyMetric(Base):
    __tablename__ = "course_daily_metrics"
    __table_args__ = (
        UniqueConstraint('course_id', 'metric_date', name='uix_course_metric_date'),
        {"schema": SCHEMA_NAME}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    metric_date = Column(Date, nullable=False)
    
    views_count = Column(Integer, default=0)
    enrollments_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
