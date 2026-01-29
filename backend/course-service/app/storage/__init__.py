"""Storage module initialization"""
from app.storage.minio import MinIOClient, minio_client

__all__ = ["MinIOClient", "minio_client"]
