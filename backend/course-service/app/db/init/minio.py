"""MinIO initialization utilities"""
import logging
from app.storage import minio_client

logger = logging.getLogger(__name__)


def init_minio() -> None:
    """Initialize MinIO - ensure bucket exists"""
    try:
        # MinIOClient already creates the bucket in __init__
        logger.info(f"MinIO bucket '{minio_client.bucket_name}' initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing MinIO: {e}")
        raise


def check_minio_connection() -> bool:
    """Check if MinIO is accessible"""
    try:
        # Try to list files to verify connection
        minio_client.list_files()
        logger.info("MinIO connection successful")
        return True
    except Exception as e:
        logger.error(f"MinIO connection failed: {e}")
        return False
