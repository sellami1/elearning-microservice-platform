"""
SQLAlchemy models initialization.
Import order matters to avoid circular dependencies.
"""

from .base import Base  # Must be first
from .course import Course
from .lesson import Lesson
from .enrollment import Enrollment
from .feedback import Feedback

# Export all models
__all__ = ["Base", "Course", "Lesson", "Enrollment", "Feedback"]