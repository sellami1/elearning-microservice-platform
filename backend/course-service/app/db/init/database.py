"""Database initialization utilities (async)"""
import logging
from sqlalchemy import text
from app.db.session import engine, Base
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database - create all tables (async)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def check_db_connection() -> bool:
    """Check if database is accessible (async)"""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def drop_all_tables() -> None:
    """Drop all tables - use with caution! (async)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise
