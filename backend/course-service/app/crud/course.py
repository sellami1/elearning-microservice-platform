from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, and_
import uuid
from ..models.course import Course
from ..schemas.course import CourseCreate, CourseUpdate, CourseCreateForm

class CRUDCourse:
    def get(self, db: Session, course_id: uuid.UUID) -> Optional[Course]:
        return db.query(Course).filter(Course.id == course_id).first()
    
    def get_by_instructor(self, db: Session, instructor_id: str) -> List[Course]:
        return db.query(Course).filter(Course.instructor_id == instructor_id).all()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Course]:
        query = db.query(Course)
        
        # Apply filters
        if filters:
            if "published" in filters:
                query = query.filter(Course.published == filters["published"])
            if "category" in filters:
                query = query.filter(Course.category == filters["category"])
            if "level" in filters:
                query = query.filter(Course.level == filters["level"])
            if "instructor_id" in filters:
                query = query.filter(Course.instructor_id == filters["instructor_id"])
            if "is_featured" in filters:
                query = query.filter(Course.is_featured == filters["is_featured"])
            if "search" in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Course.title.ilike(search_term),
                        Course.description.ilike(search_term),
                        Course.short_description.ilike(search_term)
                    )
                )
        
        # Order by created date (newest first)
        query = query.order_by(desc(Course.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    ##### IMPORTANT NOTES:
    # "Nullable=False" type of Course fields are
    # accepted null!!!
    #####
    def create_from_form(self, db: Session, *, obj_in: CourseCreateForm, instructor_id: str) -> Course:
        """
        Create course from form data (without thumbnail)
        """
        db_obj = Course(
            **obj_in.dict(),
            instructor_id=instructor_id,
            thumbnail_url=None  # Will be set after upload
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_thumbnail(self, db: Session, *, course_id: uuid.UUID, thumbnail_url: str) -> Course:
        """
        Update course thumbnail URL
        """
        course = self.get(db, course_id=course_id)
        if not course:
            return None
        
        course.thumbnail_url = thumbnail_url
        db.add(course)
        db.commit()
        db.refresh(course)
        return course
    
    # Keep existing update and delete methods
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: Course, 
        obj_in: CourseUpdate
    ) -> Course:
        update_data = obj_in.dict(exclude_unset=True, exclude={"thumbnail"})
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, course_id: uuid.UUID) -> Course:
        obj = db.query(Course).get(course_id)
        db.delete(obj)
        db.commit()
        return obj
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        query = db.query(Course)
        
        if filters:
            if "published" in filters:
                query = query.filter(Course.published == filters["published"])
            if "category" in filters:
                query = query.filter(Course.category == filters["category"])
            if "instructor_id" in filters:
                query = query.filter(Course.instructor_id == filters["instructor_id"])
        
        return query.count()
    
    def update_rating(self, db: Session, course_id: uuid.UUID, new_rating: float) -> Course:
        course = self.get(db, course_id)
        if not course:
            return None
        
        total_rating = course.rating * course.total_ratings
        course.total_ratings += 1
        course.rating = (total_rating + new_rating) / course.total_ratings
        
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

course = CRUDCourse()