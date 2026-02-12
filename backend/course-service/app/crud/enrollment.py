from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
import uuid
from datetime import datetime, timedelta

from ..models.enrollment import Enrollment, LessonProgress
from ..models.course import Course
from ..models.lesson import Lesson
from ..schemas.enrollment import EnrollmentCreate, EnrollmentUpdate

class CRUDEnrollment:
    def get(self, db: Session, enrollment_id: uuid.UUID) -> Optional[Enrollment]:
        """Get enrollment by ID"""
        return db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    def get_by_user_and_course(
        self, 
        db: Session, 
        user_id: str, 
        course_id: uuid.UUID
    ) -> Optional[Enrollment]:
        """Get enrollment by user and course"""
        return db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
    
    def get_user_enrollments(
        self, 
        db: Session, 
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Enrollment]:
        """Get all enrollments for a user"""
        query = db.query(Enrollment).filter(Enrollment.user_id == user_id)
        
        # Apply filters
        if filters:
            if "completed" in filters:
                query = query.filter(Enrollment.completed == filters["completed"])
            if "course_id" in filters:
                query = query.filter(Enrollment.course_id == filters["course_id"])
            if "search" in filters:
                # Join with course for search
                query = query.join(Course).filter(
                    Course.title.ilike(f"%{filters['search']}%") |
                    Course.description.ilike(f"%{filters['search']}%")
                )
        
        # Order by last accessed (most recent first)
        query = query.order_by(desc(Enrollment.last_accessed_at))
        
        return query.offset(skip).limit(limit).all()
    
    def count_user_enrollments(
        self, 
        db: Session, 
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count user's enrollments"""
        query = db.query(Enrollment).filter(Enrollment.user_id == user_id)
        
        if filters:
            if "completed" in filters:
                query = query.filter(Enrollment.completed == filters["completed"])
        
        return query.count()
    
    def create(
        self, 
        db: Session, 
        *, 
        user_id: str,
        course_id: uuid.UUID
    ) -> Enrollment:
        """Create a new enrollment"""
        # Check if already enrolled
        existing = self.get_by_user_and_course(db, user_id, course_id)
        if existing:
            return existing
        
        # Create enrollment
        db_obj = Enrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow()
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update course enrollment count
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            course.total_enrollments += 1
            db.add(course)
            db.commit()
        
        return db_obj
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: Enrollment, 
        obj_in: EnrollmentUpdate
    ) -> Enrollment:
        """Update enrollment"""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Update last_accessed_at if progress is being updated
        if "progress_percentage" in update_data:
            update_data["last_accessed_at"] = datetime.utcnow()
            
            # Check if course is now completed
            if update_data["progress_percentage"] >= 100.0:
                update_data["completed"] = True
                update_data["completed_at"] = datetime.utcnow()
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, enrollment_id: uuid.UUID) -> bool:
        """Delete enrollment"""
        enrollment = self.get(db, enrollment_id=enrollment_id)
        if not enrollment:
            return False
        
        # Decrease course enrollment count
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course and course.total_enrollments > 0:
            course.total_enrollments -= 1
            db.add(course)
        
        db.delete(enrollment)
        db.commit()
        return True
    
    def record_access(
        self, 
        db: Session, 
        *, 
        enrollment_id: uuid.UUID
    ) -> Enrollment:
        """Record that user accessed the course (update last_accessed_at)"""
        enrollment = self.get(db, enrollment_id=enrollment_id)
        if not enrollment:
            return None
        
        enrollment.last_accessed_at = datetime.utcnow()
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
    
    def get_course_enrollments(
        self,
        db: Session,
        course_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:
        """Get all enrollments for a course (for instructor/admin)"""
        query = db.query(Enrollment).filter(Enrollment.course_id == course_id)
        query = query.order_by(desc(Enrollment.enrolled_at))
        
        return query.offset(skip).limit(limit).all()
    
    def count_course_enrollments(self, db: Session, course_id: uuid.UUID) -> int:
        """Count enrollments for a course"""
        return db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    
    def get_user_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get enrollment statistics for a user"""
        from sqlalchemy import func
        
        stats = db.query(
            func.count(Enrollment.id).label('total_enrollments'),
            func.count(case((Enrollment.completed == True, 1))).label('completed_enrollments'),
            func.avg(Enrollment.progress_percentage).label('average_progress'),
            func.sum(Enrollment.total_time_spent_minutes).label('total_time_spent')
        ).filter(Enrollment.user_id == user_id).first()
        
        return {
            'total_enrollments': stats.total_enrollments or 0,
            'completed_enrollments': stats.completed_enrollments or 0,
            'active_enrollments': (stats.total_enrollments or 0) - (stats.completed_enrollments or 0),
            'average_progress': round(stats.average_progress or 0.0, 2),
            'total_time_spent_minutes': stats.total_time_spent or 0
        }

    def get_instructor_enrollments(
        self,
        db: Session,
        instructor_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all enrollments for all courses owned by an instructor.
        
        Returns:
            Tuple of (grouped_enrollments, total_count)
            grouped_enrollments: List of dicts with course_id, course_title, items[]
            total_count: Total number of enrollments (for pagination)
        """
        # Import here to avoid circular imports
        from .course import course as course_crud
        
        # Get all courses belonging to this instructor
        instructor_courses = course_crud.get_by_instructor(db, instructor_id=instructor_id)
        if not instructor_courses:
            return [], 0
        
        course_ids = [course.id for course in instructor_courses]
        
        # Get total count of enrollments for these courses
        total = db.query(Enrollment).filter(
            Enrollment.course_id.in_(course_ids)
        ).count()
        
        # Get paginated enrollments with course details
        from ..models.course import Course
        
        enrollments_query = db.query(
            Enrollment,
            Course.title.label('course_title')
        ).join(
            Course, Enrollment.course_id == Course.id
        ).filter(
            Enrollment.course_id.in_(course_ids)
        ).order_by(
            desc(Enrollment.enrolled_at)  # Most recent first
        ).offset(skip).limit(limit)
        
        enrollments_data = enrollments_query.all()
        
        # Group enrollments by course
        grouped = {}
        for enrollment, course_title in enrollments_data:
            course_id_str = str(enrollment.course_id)
            
            if course_id_str not in grouped:
                grouped[course_id_str] = {
                    'course_id': enrollment.course_id,
                    'course_title': course_title,
                    'items': []
                }
            
            # Build enrollment item
            enrollment_item = {
                'enrollment_id': enrollment.id,
                'user_id': enrollment.user_id,
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'progress_percentage': enrollment.progress_percentage,
                'completed': enrollment.completed,
                'total_time_spent_minutes': enrollment.total_time_spent_minutes,
                'last_accessed_at': enrollment.last_accessed_at.isoformat(),
                'last_lesson_id': enrollment.last_lesson_id
            }
            
            grouped[course_id_str]['items'].append(enrollment_item)
        
        # Convert grouped dict to list
        enrolls = list(grouped.values())
        
        return enrolls, total

class CRUDLessonProgress:
    def get_lesson_progress(
        self, 
        db: Session, 
        enrollment_id: uuid.UUID, 
        lesson_id: uuid.UUID
    ) -> Optional[LessonProgress]:
        """Get progress for a specific lesson"""
        return db.query(LessonProgress).filter(
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.lesson_id == lesson_id
        ).first()
    
    def get_enrollment_progresses(
        self, 
        db: Session, 
        enrollment_id: uuid.UUID
    ) -> List[LessonProgress]:
        """Get all lesson progresses for an enrollment"""
        return db.query(LessonProgress).filter(
            LessonProgress.enrollment_id == enrollment_id
        ).all()
    
    def update_lesson_progress(
        self,
        db: Session,
        *,
        enrollment: Enrollment,
        lesson_id: uuid.UUID,
        completed: bool = True,
        time_spent_minutes: Optional[int] = None
    ) -> Tuple[LessonProgress, bool]:
        """Update progress for a specific lesson"""
        # Get or create lesson progress
        progress = self.get_lesson_progress(db, enrollment.id, lesson_id)
        is_new = False
        
        if not progress:
            is_new = True
            progress = LessonProgress(
                enrollment_id=enrollment.id,
                lesson_id=lesson_id,
                course_id=enrollment.course_id,
                completed=completed,
                time_spent_minutes=time_spent_minutes or 0,
                last_accessed_at=datetime.utcnow()
            )
            
            if completed:
                progress.completed_at = datetime.utcnow()
        else:
            # Update existing progress
            progress.completed = completed
            progress.last_accessed_at = datetime.utcnow()
            
            if time_spent_minutes is not None:
                progress.time_spent_minutes += time_spent_minutes
            
            if completed and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
        
        db.add(progress)
        
        # Update enrollment's overall progress
        total_lessons = db.query(Lesson).filter(
            Lesson.course_id == enrollment.course_id,
            Lesson.is_published == True
        ).count()
        
        completed_lessons = db.query(LessonProgress).filter(
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.completed == True
        ).count()
        
        # Update enrollment progress
        enrollment.update_progress(db, total_lessons, completed_lessons)
        
        # Update total time spent
        if time_spent_minutes:
            enrollment.total_time_spent_minutes += time_spent_minutes
        
        enrollment.last_accessed_at = datetime.utcnow()
        enrollment.last_lesson_id = lesson_id
        
        db.add(enrollment)
        db.commit()
        
        return progress, is_new
    
    def get_course_progress_summary(
        self,
        db: Session,
        enrollment_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get progress summary for a course"""
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            return {}
        
        # Get all lessons in course
        total_lessons = db.query(Lesson).filter(
            Lesson.course_id == enrollment.course_id,
            Lesson.is_published == True
        ).count()
        
        # Get completed lessons
        completed_lessons = db.query(LessonProgress).filter(
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.completed == True
        ).count()
        
        # Get recent activity
        recent_activity = db.query(LessonProgress).filter(
            LessonProgress.enrollment_id == enrollment_id
        ).order_by(desc(LessonProgress.last_accessed_at)).limit(5).all()
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': enrollment.progress_percentage,
            'total_time_spent_minutes': enrollment.total_time_spent_minutes,
            'recent_activity': [
                {
                    'lesson_id': activity.lesson_id,
                    'completed': activity.completed,
                    'last_accessed': activity.last_accessed_at
                }
                for activity in recent_activity
            ]
        }

# Initialize CRUD instances
enrollment = CRUDEnrollment()
lesson_progress = CRUDLessonProgress()