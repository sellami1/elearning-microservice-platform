from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.analytics import CourseDailyMetric
from ..schemas.analytics import DailyMetricResponse, TopCourseResponse
from ..auth import get_current_user

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/course/{course_id}", response_model=List[DailyMetricResponse])
def get_course_metrics(course_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    metrics = db.query(CourseDailyMetric).filter(
        CourseDailyMetric.course_id == course_id
    ).order_by(CourseDailyMetric.metric_date.desc()).all()
    return metrics

@router.get("/top-courses", response_model=List[TopCourseResponse])
def get_top_courses(limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    top_courses = db.query(
        CourseDailyMetric.course_id,
        func.sum(CourseDailyMetric.views_count).label("total_views"),
        func.sum(CourseDailyMetric.enrollments_count).label("total_enrollments")
    ).group_by(CourseDailyMetric.course_id).order_by(
        func.sum(CourseDailyMetric.views_count).desc()
    ).limit(limit).all()
    
    return [
        TopCourseResponse(
            course_id=row.course_id,
            total_views=row.total_views,
            total_enrollments=row.total_enrollments
        ) for row in top_courses
    ]
