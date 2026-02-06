import uuid
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)  # UUID primary key
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Update timestamp
    
    def to_dict(self):
        """Convert SQLAlchemy model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}