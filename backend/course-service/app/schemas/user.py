from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"


# User DTO - Data Transfer Object from User Microservice
class UserDTO(BaseModel):
    """User Data Transfer Object (from User microservice)"""
    id: int
    email: str
    role: UserRole
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True