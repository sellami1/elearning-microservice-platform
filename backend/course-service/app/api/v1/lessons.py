from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
from sqlalchemy.orm import Session
import uuid

from ...database import get_db
from ...crud import lesson as crud_lesson
from ...crud import course as crud_course
from ...schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from ...core.security import get_current_user, get_current_instructor
from ...core.minio_client import minio_client

router = APIRouter()

@router.get("/course/{course_id}", response_model=List[LessonResponse])
def get_course_lessons(
    course_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all lessons for a course
    """
    # Check if course exists
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if user can access course
    # (This would require enrollment check in a real implementation)
    lessons = crud_lesson.lesson.get_by_course(db, course_id=course_id)
    return lessons

@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_in: LessonCreate,
    content_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Create a lesson (instructor only)
    """
    # Verify course exists and user owns it
    db_course = crud_course.course.get(db, course_id=lesson_in.course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add lessons to this course"
        )
    
    # If file is uploaded, upload to MinIO
    content_url = lesson_in.content_url
    if content_file:
        content_url = await minio_client.upload_file(
            content_file, 
            str(lesson_in.course_id),
            str(uuid.uuid4())  # Temporary lesson ID
        )
    
    # Create lesson in database
    lesson_data = lesson_in.dict(exclude={"content_url"})
    if content_url:
        lesson_data["content_url"] = content_url
    
    db_lesson = crud_lesson.lesson.create(db, obj_in=lesson_data)
    return db_lesson

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: uuid.UUID = Path(...),
    lesson_in: LessonUpdate = None,
    content_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Update a lesson (instructor only)
    """
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get course to check ownership
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lesson"
        )
    
    # Handle file upload if provided
    update_data = lesson_in.dict(exclude_unset=True) if lesson_in else {}
    
    if content_file:
        # Upload new file to MinIO
        content_url = await minio_client.upload_file(
            content_file,
            str(db_lesson.course_id),
            str(lesson_id)
        )
        update_data["content_url"] = content_url
    
    db_lesson = crud_lesson.lesson.update(
        db, db_obj=db_lesson, obj_in=update_data
    )
    return db_lesson

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: uuid.UUID = Path(...),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Delete a lesson (instructor only)
    """
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get course to check ownership
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lesson"
        )
    
    # Delete file from MinIO if exists
    if db_lesson.content_url:
        # Extract object name from URL
        # This is a simplified version
        pass
    
    crud_lesson.lesson.delete(db, lesson_id=lesson_id)
    return None

@router.post("/{lesson_id}/upload-content")
async def upload_lesson_content(
    lesson_id: uuid.UUID = Path(...),
    content_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Upload content file for a lesson
    """
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get course to check ownership
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload content for this lesson"
        )
    
    # Upload to MinIO
    content_url = await minio_client.upload_file(
        content_file,
        str(db_lesson.course_id),
        str(lesson_id)
    )
    
    # Update lesson with new content URL
    db_lesson.content_url = content_url
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    
    return {"content_url": content_url}