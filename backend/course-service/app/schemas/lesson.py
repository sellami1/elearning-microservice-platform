from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Lesson Schemas
class LessonBase(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    position: int = Field(default=0, ge=0)


class LessonCreate(LessonBase):
    course_id: int


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    position: Optional[int] = Field(default=None, ge=0)


class Lesson(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True