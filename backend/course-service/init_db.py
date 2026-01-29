#!/usr/bin/env python3
"""Database and storage initialization script (async)"""
import logging
import sys
import asyncio
from app.db.init import init_db, check_db_connection, init_minio, check_minio_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize all databases and storage"""
    logger.info("Starting database and storage initialization...")
    
    # Check and initialize PostgreSQL
    logger.info("Checking PostgreSQL connection...")
    if not await check_db_connection():
        logger.error("Failed to connect to PostgreSQL. Please ensure the database is running.")
        sys.exit(1)
    
    logger.info("Creating database tables...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Check and initialize MinIO
    logger.info("Checking MinIO connection...")
    if not check_minio_connection():
        logger.error("Failed to connect to MinIO. Please ensure MinIO is running.")
        sys.exit(1)
    
    logger.info("Initializing MinIO buckets...")
    try:
        init_minio()
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        sys.exit(1)
    
    logger.info("✓ All databases and storage initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
