from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from ..models.analytics import AnalyticsEvent, CourseDailyMetric, EventType
from ..schemas.analytics import EventCreate, EventResponse
from ..auth import get_current_user
from ..core.redis import delete_cache
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/view", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def record_view(event: EventCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return record_event(event, EventType.course_view, db, current_user)

@router.post("/enroll", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def record_enroll(event: EventCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return record_event(event, EventType.course_enroll, db, current_user)

def record_event(event_in: EventCreate, event_type: EventType, db: Session, current_user: dict):
    # 1. Record the raw granular event for auditing and deep analysis
    db_event = AnalyticsEvent(
        event_type=event_type,
        user_id=current_user["user_id"],
        course_id=event_in.course_id,
        user_role=current_user["role"]
    )
    db.add(db_event)
    
    # 2. Update the summarized Daily Metrics table (Performance optimization)
    # This avoids expensive 'COUNT(*)' queries on the raw events table
    today = date.today()
    metric = db.query(CourseDailyMetric).filter(
        CourseDailyMetric.course_id == event_in.course_id,
        CourseDailyMetric.metric_date == today
    ).first()
    
    # If no metric exists for today, create the day's record (Upsert logic)
    if not metric:
        metric = CourseDailyMetric(
            course_id=event_in.course_id,
            metric_date=today,
            views_count=0,
            enrollments_count=0
        )
        db.add(metric)
    
    # Increment the specific metric based on event type
    if event_type == EventType.course_view:
        metric.views_count += 1
    elif event_type == EventType.course_enroll:
        metric.enrollments_count += 1
        
    db.commit()
    logger.info(f"Recorded {event_type} for course {event_in.course_id} by user {current_user['user_id']}")
    
    # Cache Invalidation: Delete relevant analytics keys
    delete_cache("top_courses")
    delete_cache(f"course_metrics:{event_in.course_id}")
    logger.info(f"Invalidated cache for course {event_in.course_id}")
    
    db.refresh(db_event)
    return db_event
