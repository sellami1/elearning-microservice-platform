from minio import Minio
from minio.error import S3Error
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from .config import get_settings
import os
import io
from datetime import datetime, timedelta

settings = get_settings()

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO bucket error: {str(e)}"
            )
    
    def validate_thumbnail_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate thumbnail image file
        Returns: (is_valid, error_message)
        """
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp', 'image/svg+xml'
        ]
        
        # Check file type
        if file.content_type not in allowed_types:
            return False, f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > max_size:
            return False, f"File too large. Max size: 5MB"
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        file_extension = os.path.splitext(file.filename or "")[1].lower()
        if file_extension not in allowed_extensions:
            return False, f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        
        return True, ""
    
    async def upload_thumbnail(self, file: UploadFile, course_id: str) -> str:
        """
        Upload thumbnail image to MinIO
        """
        # Validate file
        is_valid, error_msg = self.validate_thumbnail_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        try:
            # Generate unique filename with original extension
            file_extension = os.path.splitext(file.filename or "thumbnail")[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            object_name = f"courses/{course_id}/thumbnails/{filename}"
            
            # Read file content and wrap in a BytesIO stream for MinIO
            content = await file.read()
            data_stream = io.BytesIO(content)
            data_stream.seek(0)

            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(content),
                content_type=file.content_type or "image/jpeg"
            )
            
            # Generate URL
            url = f"http://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            return url
            
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Thumbnail upload failed: {str(e)}"
            )
        finally:
            await file.close()
    
    async def upload_lesson_content(self, file: UploadFile, course_id: str, lesson_id: str = None) -> str:
        """
        Upload lesson content file to MinIO
        """
        try:
            file_extension = os.path.splitext(file.filename or "")[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            
            if lesson_id:
                object_name = f"courses/{course_id}/lessons/{lesson_id}/{filename}"
            else:
                object_name = f"courses/{course_id}/assets/{filename}"
            
            content = await file.read()
            data_stream = io.BytesIO(content)
            data_stream.seek(0)

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(content),
                content_type=file.content_type or "application/octet-stream"
            )
            
            url = f"http://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            return url
            
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )
        finally:
            await file.close()
    
    def delete_file(self, object_name: str):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error:
            pass
    
    def get_presigned_url(self, object_name: str, expiry_hours: int = 24) -> str:
        """Generate presigned URL for temporary access"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=timedelta(hours=expiry_hours)
            )
            return url
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate URL: {str(e)}"
            )

minio_client = MinIOClient()