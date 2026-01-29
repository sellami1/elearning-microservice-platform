from sqlalchemy.orm import Session
from app.models import Course, Module, Lesson
from app.schemas import CourseCreate, CourseUpdate


def create_course(db: Session, course: CourseCreate, instructor_id: int):
    """Create a new course"""
    db_course = Course(
        title=course.title,
        description=course.description,
        instructor_id=instructor_id,
        is_published=course.is_published,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_course_by_id(db: Session, course_id: int):
    """Get course by ID"""
    return db.query(Course).filter(Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 10):
    """Get all courses"""
    return db.query(Course).offset(skip).limit(limit).all()


def update_course(db: Session, course_id: int, course_update: CourseUpdate):
    """Update a course"""
    db_course = get_course_by_id(db, course_id)
    if not db_course:
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int):
    """Delete a course"""
    db_course = get_course_by_id(db, course_id)
    if db_course:
        db.delete(db_course)
        db.commit()
    return db_course
