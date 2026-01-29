from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

# Create async database engine (ensure DATABASE_URL uses a async driver like asyncpg)
# If DATABASE_URL is in the form postgresql://... we replace it with postgresql+asyncpg://
async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(
    async_db_url,
    echo=settings.DEBUG,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Async dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session
