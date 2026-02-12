"""
SQLAlchemy models initialization.
Import order matters to avoid circular dependencies.
"""

from .base import Base  # Must be first
from .course import Course
from .lesson import Lesson
from .enrollment import Enrollment

# Export all models
__all__ = ["Base", "Course", "Lesson", "Enrollment"]