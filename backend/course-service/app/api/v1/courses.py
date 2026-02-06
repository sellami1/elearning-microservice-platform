from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Form, File, UploadFile
from sqlalchemy.orm import Session
import uuid

from ...database import get_db
from ...crud import course as crud_course
from ...schemas.course import (
    CourseBase, CourseCreate, CourseUpdate, CourseResponse, 
    CourseListResponse, CourseLevel, CourseCreateForm
)
from ...core.security import get_current_user, get_current_instructor
from ...core.minio_client import minio_client

router = APIRouter()

@router.get("/", response_model=CourseListResponse)
def get_courses(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    published: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    level: Optional[CourseLevel] = Query(None),
    is_featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    instructor_id: Optional[str] = Query(None),
    # Add current_user parameter to include user context if needed
    current_user: dict = Depends(get_current_user),
):
    """
    Get all courses with optional filtering
    """
    filters = {}
    if published is not None:
        filters["published"] = published
    if category:
        filters["category"] = category
    if level:
        filters["level"] = level
    if is_featured is not None:
        filters["is_featured"] = is_featured
    if search:
        filters["search"] = search
    if instructor_id:
        filters["instructor_id"] = instructor_id
    
    courses = crud_course.course.get_multi(
        db, skip=skip, limit=limit, filters=filters
    )
    total = crud_course.course.count(db, filters=filters)
    
    return CourseListResponse(
        items=courses,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
):
    """
    Get course by ID
    """
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Only return published courses to non-owners
    # (Check for ownership is done in separate endpoints)
    return db_course

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    title: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None, max_length=500),
    price: float = Form(0.0, ge=0.0),
    category: Optional[str] = Form(None, max_length=100),
    subcategory: Optional[str] = Form(None, max_length=100),
    level: CourseLevel = Form(CourseLevel.BEGINNER),
    duration_hours: int = Form(0, ge=0),
    published: bool = Form(False),
    is_featured: bool = Form(False),
    thumbnail_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Create a new course with optional thumbnail upload (Multipart Form Data)
    
    - **title**: Course title (required)
    - **description**: Full course description (optional)
    - **short_description**: Brief summary (optional, max 500 chars)
    - **price**: Course price (default: 0.0 = free)
    - **category**: Main category (e.g., Programming, Design)
    - **subcategory**: Subcategory (e.g., Python, Web Development)
    - **level**: Difficulty level (beginner|intermediate|advanced)
    - **duration_hours**: Estimated total duration in hours
    - **published**: Whether course is publicly visible
    - **is_featured**: Whether course is featured on homepage
    - **thumbnail_file**: Thumbnail image file (jpg, png, gif, webp, svg - max 5MB)
    """
    try:
        # Create CourseCreateForm object for validation
        course_form = CourseCreateForm(
            title=title,
            description=description,
            short_description=short_description,
            price=price,
            category=category,
            subcategory=subcategory,
            level=level,
            duration_hours=duration_hours,
            published=published,
            is_featured=is_featured
        )
        
        # Create course in database (without thumbnail)
        db_course = crud_course.course.create_from_form(
            db, obj_in=course_form, instructor_id=current_user["user_id"]
        )
        
        # Upload thumbnail if provided
        thumbnail_url = None
        if thumbnail_file and thumbnail_file.filename:
            thumbnail_url = await minio_client.upload_thumbnail(
                thumbnail_file, str(db_course.id)
            )
            
            # Update course with thumbnail URL
            db_course = crud_course.course.update_thumbnail(
                db, course_id=db_course.id, thumbnail_url=thumbnail_url
            )
        
        return db_course
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        # Rollback course creation if thumbnail upload fails
        if 'db_course' in locals():
            crud_course.course.delete(db, course_id=db_course.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Course creation failed: {str(e)}"
        )

@router.post("/{course_id}/upload-thumbnail", response_model=CourseResponse)
async def upload_course_thumbnail(
    course_id: uuid.UUID = Path(...),
    thumbnail_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Upload/update thumbnail for an existing course
    """
    # Check if course exists and user owns it
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if db_course.instructor_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    # Upload thumbnail
    thumbnail_url = await minio_client.upload_thumbnail(
        thumbnail_file, str(course_id)
    )
    
    # Update course with new thumbnail URL
    db_course = crud_course.course.update_thumbnail(
        db, course_id=course_id, thumbnail_url=thumbnail_url
    )
    
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: uuid.UUID = Path(...),
    course_in: CourseUpdate = None,
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Update a course (instructor or admin only)
    """
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check ownership (admin can update any course)
    if current_user["role"] != "admin" and db_course.instructor_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    db_course = crud_course.course.update(
        db, db_obj=db_course, obj_in=course_in
    )
    return db_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: uuid.UUID = Path(...),
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    """
    Delete a course (instructor or admin only)
    """
    db_course = crud_course.course.get(db, course_id=course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check ownership (admin can delete any course)
    if current_user["role"] != "admin" and db_course.instructor_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    crud_course.course.delete(db, course_id=course_id)
    return None

@router.get("/instructor/mine", response_model=List[CourseResponse])
def get_my_courses(
    current_user: dict = Depends(get_current_instructor),
    db: Session = Depends(get_db),
    published: Optional[bool] = Query(None),
):
    """
    Get courses created by the current instructor
    """
    filters = {"instructor_id": current_user["user_id"]}
    if published is not None:
        filters["published"] = published
    
    courses = crud_course.course.get_multi(db, filters=filters)
    return courses