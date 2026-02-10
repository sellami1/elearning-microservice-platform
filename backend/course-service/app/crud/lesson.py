from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import uuid
from ..models.lesson import Lesson
from ..schemas.lesson import LessonCreateForm, LessonUpdate

class CRUDLesson:
    def get(self, db: Session, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """Get lesson by ID"""
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    def get_by_course(
        self, 
        db: Session, 
        course_id: uuid.UUID, 
        published_only: bool = True
    ) -> List[Lesson]:
        """Get all lessons for a course"""
        query = db.query(Lesson).filter(Lesson.course_id == course_id)
        
        if published_only:
            query = query.filter(Lesson.is_published == True)
        
        # Order by order_index then by creation date
        query = query.order_by(asc(Lesson.order_index), asc(Lesson.created_at))
        
        return query.all()
    
    def get_by_course_paginated(
        self,
        db: Session,
        course_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = True
    ) -> List[Lesson]:
        """Get paginated lessons for a course"""
        query = db.query(Lesson).filter(Lesson.course_id == course_id)
        
        if published_only:
            query = query.filter(Lesson.is_published == True)
        
        query = query.order_by(asc(Lesson.order_index), asc(Lesson.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def count_by_course(
        self, 
        db: Session, 
        course_id: uuid.UUID, 
        published_only: bool = True
    ) -> int:
        """Count lessons in a course"""
        query = db.query(Lesson).filter(Lesson.course_id == course_id)
        
        if published_only:
            query = query.filter(Lesson.is_published == True)
        
        return query.count()
    
    def create_from_form(
        self, 
        db: Session, 
        *, 
        obj_in: LessonCreateForm, 
        content_url: Optional[str] = None
    ) -> Lesson:
        """Create lesson from form data"""
        db_obj = Lesson(
            **obj_in.dict(exclude={"content_url"} if hasattr(obj_in, 'content_url') else {}),
            content_url=content_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: LessonCreateForm, 
        content_url: Optional[str] = None
    ) -> Lesson:
        """Create lesson (alias for create_from_form)"""
        return self.create_from_form(db, obj_in=obj_in, content_url=content_url)
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: Lesson, 
        obj_in: LessonUpdate
    ) -> Lesson:
        """Update lesson"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_content_url(
        self, 
        db: Session, 
        *, 
        lesson_id: uuid.UUID, 
        content_url: str
    ) -> Lesson:
        """Update lesson content URL"""
        lesson = self.get(db, lesson_id=lesson_id)
        if not lesson:
            return None
        
        lesson.content_url = content_url
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson
    
    def delete(self, db: Session, *, lesson_id: uuid.UUID) -> Lesson:
        """Delete lesson"""
        obj = db.query(Lesson).get(lesson_id)
        db.delete(obj)
        db.commit()
        return obj
    
    def get_next_order_index(self, db: Session, course_id: uuid.UUID) -> int:
        """Get the next order index for a new lesson in the course"""
        last_lesson = db.query(Lesson).filter(
            Lesson.course_id == course_id
        ).order_by(desc(Lesson.order_index)).first()
        
        return (last_lesson.order_index + 1) if last_lesson else 0
    
    def reorder_lessons(
        self, 
        db: Session, 
        course_id: uuid.UUID, 
        new_order: List[uuid.UUID]
    ) -> List[Lesson]:
        """Reorder lessons in a course"""
        lessons = self.get_by_course(db, course_id, published_only=False)
        
        # Create mapping of lesson_id to lesson object
        lesson_map = {str(lesson.id): lesson for lesson in lessons}
        
        # Update order indices
        for index, lesson_id in enumerate(new_order):
            lesson = lesson_map.get(str(lesson_id))
            if lesson:
                lesson.order_index = index
                db.add(lesson)
        
        db.commit()
        
        # Return reordered lessons
        return self.get_by_course(db, course_id, published_only=False)

lesson = CRUDLesson()