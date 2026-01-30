from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from ..models.analytics import EventType, UserRole

class EventCreate(BaseModel):
    course_id: UUID

class EventResponse(BaseModel):
    id: UUID
    event_type: EventType
    user_id: Optional[str]
    course_id: UUID
    user_role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class DailyMetricResponse(BaseModel):
    course_id: UUID
    metric_date: date
    views_count: int
    enrollments_count: int

    class Config:
        from_attributes = True

class TopCourseResponse(BaseModel):
    course_id: UUID
    total_views: int
    total_enrollments: int
