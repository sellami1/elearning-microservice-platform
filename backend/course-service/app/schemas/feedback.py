from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDTO


# Feedback Schemas
class FeedbackBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    user_id: int
    course_id: int


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None


class Feedback(FeedbackBase):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithUser(Feedback):
    user: Optional["UserDTO"] = None


# Rebuild models with forward references
FeedbackWithUser.model_rebuild()