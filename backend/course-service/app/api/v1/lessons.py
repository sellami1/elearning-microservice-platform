from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Form, File, UploadFile, Body
from sqlalchemy.orm import Session
import uuid

from ...database import get_db
from ...crud import lesson as crud_lesson
from ...crud import course as crud_course
from ...schemas.lesson import (
    LessonCreateForm, LessonUpdate, LessonResponse, 
    LessonListResponse, ContentType, LessonUploadResponse
)
from ...core.auth import get_current_user, get_current_instructor, get_current_student, get_current_user_optional
from ...core.minio_client import minio_client

router = APIRouter()

@router.get("/course/{course_id}", response_model=LessonListResponse)
def get_course_lessons(
    course_id: uuid.UUID = Path(..., description="Course ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Get all lessons for a course with pagination.
    
    Access control:
    - Current instructor (course owner): sees all lessons (published + unpublished)
    - Other users (students, other instructors, guests): see only published lessons from published courses
    
    - **course_id**: UUID of the course
    - Returns paginated list of lessons
    """
    # Check if course exists
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Determine if user is the course owner (instructor)
    is_course_owner = (
        current_user and 
        current_user.get("role") == "instructor" and 
        db_course.instructor_id == current_user["user_id"]
    )
    
    # Access control logic
    if is_course_owner:
        # Course owner sees all lessons (published and unpublished)
        published_only = False
    else:
        # For non-owners, course must be published
        if not db_course.published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        # Non-owners only see published lessons
        published_only = True
    
    # Get lessons
    lessons = crud_lesson.lesson.get_by_course_paginated(
        db, 
        course_id=course_id,
        skip=skip,
        limit=limit,
        published_only=published_only
    )
    
    total = crud_lesson.lesson.count_by_course(
        db, course_id=course_id, published_only=published_only
    )
    
    return LessonListResponse(
        items=lessons,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    title: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    content_type: ContentType = Form(...),
    duration_minutes: int = Form(0, ge=0),
    order_index: Optional[int] = Form(None, ge=0),
    is_preview: bool = Form(False),
    is_published: bool = Form(True),
    course_id: uuid.UUID = Form(...),
    content_file: Optional[UploadFile] = File(None),
    content_url: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Create a new lesson with optional content upload (Multipart Form Data)
    
    - **title**: Lesson title (required, 1-255 chars)
    - **description**: Lesson description (optional)
    - **content_type**: Type of content (video|text|pdf|quiz|audio|image)
    - **duration_minutes**: Estimated duration in minutes (default: 0)
    - **order_index**: Position in course sequence (auto-calculated if not provided)
    - **is_preview**: Whether this is a free preview lesson (default: False)
    - **is_published**: Whether lesson is published (default: True)
    - **course_id**: Parent course ID (required)
    - **content_file**: Content file (required for video/pdf/image/audio types)
    - **content_url**: Direct URL to content (alternative to file upload)
    """
    
    try:
        # Check if course exists and user owns it
        db_course = crud_course.course.get(db, course_id=course_id)
        if not db_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Verify ownership
        if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add lessons to this course"
            )
        
        # Validate file presence based on content type
        if content_type in [ContentType.VIDEO, ContentType.PDF, ContentType.IMAGE, ContentType.AUDIO]:
            if not content_file and not content_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Content file or URL is required for {content_type} lessons"
                )
        
        # Auto-calculate order_index if not provided
        if order_index is None:
            order_index = crud_lesson.lesson.get_next_order_index(db, course_id)
        
        # Create LessonCreateForm object
        lesson_form = LessonCreateForm(
            title=title,
            description=description,
            content_type=content_type,
            duration_minutes=duration_minutes,
            order_index=order_index,
            is_preview=is_preview,
            is_published=is_published,
            course_id=course_id
        )
        
        # Upload file if provided
        final_content_url = content_url
        if content_file and content_file.filename:
            final_content_url = await minio_client.upload_lesson_content(
                content_file, 
                str(course_id),
                str(uuid.uuid4()),  # Temporary lesson ID
                # content_type.value
            )
            print(f"final_content_url: {final_content_url}")
        
        # Create lesson in database
        db_lesson = crud_lesson.lesson.create_from_form(
            db, obj_in=lesson_form, content_url=final_content_url
        )
        
        return db_lesson
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # Rollback if needed (though SQLAlchemy will rollback on exception)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lesson creation failed: {str(e)}"
        )

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: uuid.UUID = Path(..., description="Lesson ID"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Get lesson details by ID.
    
    Access control:
    - Current instructor (course owner): sees all lessons (published + unpublished)
    - Other users (students, other instructors, guests): see only published lessons from published courses
    
    - **lesson_id**: UUID of the lesson
    - Returns detailed lesson information
    """
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if user can access this lesson
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    
    # Determine if user is the course owner (instructor)
    is_course_owner = (
        current_user and 
        current_user.get("role") == "instructor" and 
        db_course.instructor_id == current_user["user_id"]
    )
    
    # Access control logic
    if not is_course_owner:
        # For non-owners, course must be published
        if not db_course.published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Lesson must be published for non-owners
        if not db_lesson.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
    
    return db_lesson

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: uuid.UUID = Path(..., description="Lesson ID"),
    title: Optional[str] = Form(None, min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    content_type: Optional[ContentType] = Form(None),
    content_url: Optional[str] = Form(None),
    duration_minutes: Optional[int] = Form(None, ge=0),
    order_index: Optional[int] = Form(None, ge=0),
    is_preview: Optional[bool] = Form(None),
    is_published: Optional[bool] = Form(None),
    content_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Update a lesson (Multipart Form Data)
    
    - **lesson_id**: UUID of the lesson to update
    - All other fields are optional - only provided fields will be updated
    - Can update content by providing new file or URL
    """
    # Check if lesson exists
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check ownership
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lesson"
        )
    
    # Prepare update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if content_type is not None:
        update_data["content_type"] = content_type
    if duration_minutes is not None:
        update_data["duration_minutes"] = duration_minutes
    if order_index is not None:
        update_data["order_index"] = order_index
    if is_preview is not None:
        update_data["is_preview"] = is_preview
    if is_published is not None:
        update_data["is_published"] = is_published
    
    # Handle file upload if provided
    if content_file and content_file.filename:
        # Delete old content file from MinIO if it exists
        if db_lesson.content_url:
            old_object_name = minio_client.extract_object_name(db_lesson.content_url)
            if old_object_name:
                minio_client.delete_file(old_object_name)
        
        # Upload new file
        new_content_url = await minio_client.upload_lesson_content(
            content_file,
            str(db_lesson.course_id),
            str(lesson_id),
            # update_data.get("content_type", db_lesson.content_type).value
        )
        update_data["content_url"] = new_content_url
    elif content_url is not None:
        # If changing to a different URL, delete old content file from MinIO
        if db_lesson.content_url and db_lesson.content_url != content_url:
            old_object_name = minio_client.extract_object_name(db_lesson.content_url)
            if old_object_name:
                minio_client.delete_file(old_object_name)
        
        update_data["content_url"] = content_url
    
    # Create update object
    lesson_update = LessonUpdate(**update_data)
    
    # Update lesson
    db_lesson = crud_lesson.lesson.update(
        db, db_obj=db_lesson, obj_in=lesson_update
    )
    
    return db_lesson

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: uuid.UUID = Path(..., description="Lesson ID"),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Delete a lesson
    
    - **lesson_id**: UUID of the lesson to delete
    - Returns 204 No Content on success
    """
    db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check ownership
    db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lesson"
        )
    
    # Delete content file from MinIO if exists
    if db_lesson.content_url:
        old_object_name = minio_client.extract_object_name(db_lesson.content_url)
        if old_object_name:
            minio_client.delete_file(old_object_name)
    
    # Delete lesson from database
    crud_lesson.lesson.delete(db, lesson_id=lesson_id)
    
    return None

# @router.post("/{lesson_id}/upload-content", response_model=LessonUploadResponse)
# async def upload_lesson_content(
#     lesson_id: uuid.UUID = Path(..., description="Lesson ID"),
#     content_file: UploadFile = File(..., description="Content file to upload"),
#     current_user: dict = Depends(get_current_instructor),
#     db: Session = Depends(get_db),
# ):
#     """
#     Upload content file for a lesson (replaces existing content)
    
#     - **lesson_id**: UUID of the lesson
#     - **content_file**: Content file (required)
#     - Returns upload confirmation with content URL
#     """
#     db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
#     if not db_lesson:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Lesson not found"
#         )
    
#     # Check ownership
#     db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
#     if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to upload content for this lesson"
#         )
    
#     # Delete old file if exists
#     if db_lesson.content_url:
#         minio_client.delete_file(db_lesson.content_url)
    
#     # Upload new file
#     content_url = await minio_client.upload_lesson_content(
#         content_file,
#         str(db_lesson.course_id),
#         str(lesson_id),
#         db_lesson.content_type.value
#     )
    
#     # Update lesson with new content URL
#     db_lesson = crud_lesson.lesson.update_content_url(
#         db, lesson_id=lesson_id, content_url=content_url
#     )
    
#     return LessonUploadResponse(
#         lesson_id=lesson_id,
#         content_url=content_url,
#         message="Content uploaded successfully"
#     )

# @router.put("/{lesson_id}/publish", response_model=LessonResponse)
# def publish_lesson(
#     lesson_id: uuid.UUID = Path(..., description="Lesson ID"),
#     publish: bool = Query(True, description="True to publish, False to unpublish"),
#     current_user: dict = Depends(get_current_instructor),
#     db: Session = Depends(get_db),
# ):
#     """
#     Publish or unpublish a lesson
    
#     - **lesson_id**: UUID of the lesson
#     - **publish**: True to publish, False to unpublish
#     - Returns updated lesson
#     """
#     db_lesson = crud_lesson.lesson.get(db, lesson_id=lesson_id)
#     if not db_lesson:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Lesson not found"
#         )
    
#     # Check ownership
#     db_course = crud_course.course.get(db, course_id=db_lesson.course_id)
#     if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to modify this lesson"
#         )
    
#     # Update published status
#     db_lesson.is_published = publish
#     db.add(db_lesson)
#     db.commit()
#     db.refresh(db_lesson)
    
#     return db_lesson

# @router.post("/reorder", response_model=List[LessonResponse])
# def reorder_lessons(
#     course_id: uuid.UUID = Body(..., embed=True, description="Course ID"),
#     new_order: List[uuid.UUID] = Body(..., embed=True, description="New order of lesson IDs"),
#     current_user: dict = Depends(get_current_instructor),
#     db: Session = Depends(get_db),
# ):
#     """
#     Reorder lessons in a course
    
#     - **course_id**: UUID of the course
#     - **new_order**: List of lesson IDs in new order
#     - Returns reordered list of lessons
#     """
#     # Check if course exists and user owns it
#     db_course = crud_course.course.get(db, course_id=course_id)
#     if not db_course:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Course not found"
#         )
    
#     if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to reorder lessons in this course"
#         )
    
#     # Reorder lessons
#     lessons = crud_lesson.lesson.reorder_lessons(
#         db, course_id=course_id, new_order=new_order
#     )
    
#     return lessons