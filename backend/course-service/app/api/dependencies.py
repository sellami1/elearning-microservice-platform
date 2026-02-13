
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from ..database import get_db

# Database dependency
def get_database() -> Generator:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()