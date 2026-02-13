from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
import uuid

from ...database import get_db
from ...crud import enrollment as crud_enrollment
from ...crud import course as crud_course
from ...crud import lesson as crud_lesson
from ...schemas.enrollment import (
    EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse,
    EnrollmentWithCourse, EnrollmentListResponse, EnrollmentStats
)
from ...core.auth import get_current_student, get_current_instructor

router = APIRouter()

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    enrollment_in: EnrollmentCreate,
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Enroll current user in a course
    
    - Student can enroll in published courses
    - Cannot enroll twice in same course
    - Returns enrollment details
    """
    # Check if course exists and is published
    db_course = crud_course.course.get(db, course_id=enrollment_in.course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Only published courses can be enrolled in by students
    if not db_course.published and current_user["role"] not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course is not published"
        )
    
    # Check if already enrolled
    existing_enrollment = crud_enrollment.enrollment.get_by_user_and_course(
        db, user_id=current_user["user_id"], course_id=enrollment_in.course_id
    )
    
    if existing_enrollment:
        return existing_enrollment
    
    # Create enrollment
    try:
        db_enrollment = crud_enrollment.enrollment.create(
            db,
            user_id=current_user["user_id"],
            course_id=enrollment_in.course_id
        )
        return db_enrollment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enroll in course: {str(e)}"
        )

@router.get("/me", response_model=EnrollmentListResponse)
def get_my_enrollments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search in course titles/descriptions"),
    current_user: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Get current user's enrollments with course details
    
    - Returns paginated list of enrollments
    - Includes course information
    - Can filter by completion status
    - Can search in course content
    """
    # Build filters
    filters = {}
    if completed is not None:
        filters["completed"] = completed
    if search:
        filters["search"] = search
    
    # Get enrollments
    enrollments = crud_enrollment.enrollment.get_user_enrollments(
        db,
        user_id=current_user["user_id"],
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    # Convert to response with course details
    items = []
    for enroll in enrollments:
        course = crud_course.course.get(db, course_id=enroll.course_id)
        if course:
            # Get progress summary
            total_lessons = crud_lesson.lesson.count_by_course(
                db, course_id=course.id, published_only=True
            )
            
            completed_lessons = len([
                lp for lp in enroll.lesson_progresses 
                if lp.completed
            ]) if hasattr(enroll, 'lesson_progresses') else 0
            
            items.append(EnrollmentWithCourse(
                **enroll.to_dict(),
                course_title=course.title,
                course_thumbnail=course.thumbnail_url,
                course_instructor=course.instructor_id,  # Would fetch from User Service in production
                total_lessons=total_lessons,
                completed_lessons=completed_lessons
            ))
    
    # Get total count
    total = crud_enrollment.enrollment.count_user_enrollments(
        db, user_id=current_user["user_id"], filters=filters
    )
    
    # Get stats
    stats_data = crud_enrollment.enrollment.get_user_stats(db, current_user["user_id"])
    stats = EnrollmentStats(**stats_data)
    
    return EnrollmentListResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        stats=stats
    )

@router.get("/course/{course_id}/enrollments", response_model=dict)
def get_course_enrollments(
    course_id: uuid.UUID = Path(..., description="Course ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Get all enrollments for a course (instructor/admin only)
    
    - Returns enrollment list with user progress
    - Only course instructor or admin can access
    """
    # Check if course exists
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check ownership
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view enrollments for this course"
        )
    
    # Get enrollments
    enrollments = crud_enrollment.enrollment.get_course_enrollments(
        db, course_id=course_id, skip=skip, limit=limit
    )
    
    # Format response
    items = []
    for enroll in enrollments:
        items.append({
            "enrollment_id": enroll.id,
            "user_id": enroll.user_id,
            "enrolled_at": enroll.enrolled_at,
            "progress_percentage": enroll.progress_percentage,
            "completed": enroll.completed,
            "total_time_spent_minutes": enroll.total_time_spent_minutes,
            "last_accessed_at": enroll.last_accessed_at,
            "last_lesson_id": enroll.last_lesson_id
        })
    
    total = crud_enrollment.enrollment.count_course_enrollments(db, course_id)
    
    return {
        "course_id": course_id,
        "course_title": db_course.title,
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/instructor", response_model=dict)
def get_instructor_course_enrollments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Get all enrollments for all courses of the current instructor.
    
    Returns enrollments grouped by course with pagination.
    Only accessible by instructors and admins.
    
    Response format:
    {
        "enrolls": [
            {
                "course_id": "uuid",
                "course_title": "Course Title",
                "items": [
                    {
                        "enrollment_id": "uuid",
                        "user_id": "string",
                        "enrolled_at": "datetime",
                        "progress_percentage": float,
                        "completed": boolean,
                        "total_time_spent_minutes": int,
                        "last_accessed_at": "datetime",
                        "last_lesson_id": "uuid|null"
                    }
                ]
            }
        ],
        "total": int,
        "page": int,
        "size": int,
        "pages": int
    }
    """
    enrolls, total = crud_enrollment.enrollment.get_instructor_enrollments(
        db,
        instructor_id=current_user["user_id"],
        skip=skip,
        limit=limit
    )
    
    # Calculate pagination metadata
    pages = (total + limit - 1) // limit if total > 0 else 0
    current_page = skip // limit + 1
    
    return {
        "enrolls": enrolls,
        "total": total,
        "page": current_page,
        "size": limit,
        "pages": pages
    }