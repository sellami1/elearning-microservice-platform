from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import Course, CourseCreate, CourseUpdate
from app.services.course_service import (
    create_course, get_course_by_id, get_courses, update_course, delete_course
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_new_course(
    course: CourseCreate,
    instructor_id: int,
    db: Session = Depends(get_db)
):
    """Create a new course"""
    return create_course(db, course, instructor_id)


@router.get("/", response_model=list[Course])
def list_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all courses"""
    return get_courses(db, skip, limit)


@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course by ID"""
    course = get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


@router.put("/{course_id}", response_model=Course)
def update_existing_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db)
):
    """Update a course"""
    course = update_course(db, course_id, course_update)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course"""
    course = delete_course(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
