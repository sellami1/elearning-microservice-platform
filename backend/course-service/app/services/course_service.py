from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Course, Lesson
from app.schemas import CourseCreate, CourseUpdate


async def create_course(db: AsyncSession, course: CourseCreate, instructor_id: int):
    """Create a new course"""
    db_course = Course(
        title=course.title,
        description=course.description,
        instructor_id=instructor_id,
        is_published=course.is_published,
    )
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


async def get_course_by_id(db: AsyncSession, course_id: int):
    """Get course by ID"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalars().first()


async def get_courses(db: AsyncSession, skip: int = 0, limit: int = 10):
    """Get all courses"""
    result = await db.execute(select(Course).offset(skip).limit(limit))
    return result.scalars().all()


async def update_course(db: AsyncSession, course_id: int, course_update: CourseUpdate):
    """Update a course"""
    db_course = await get_course_by_id(db, course_id)
    if not db_course:
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


async def delete_course(db: AsyncSession, course_id: int):
    """Delete a course"""
    db_course = await get_course_by_id(db, course_id)
    if db_course:
        db.delete(db_course)
        await db.commit()
    return db_course
