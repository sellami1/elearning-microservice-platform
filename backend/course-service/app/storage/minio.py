from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import io


class MinIOClient:
    """MinIO object storage client"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_URL.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def upload_file(self, file_path: str, object_name: str, content_type: str = "application/octet-stream") -> str:
        """Upload a file to MinIO"""
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type,
            )
            return f"{settings.MINIO_URL}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"Error uploading file: {e}")
    
    def upload_bytes(self, data: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        """Upload bytes data to MinIO"""
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(data),
                len(data),
                content_type=content_type,
            )
            return f"{settings.MINIO_URL}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"Error uploading file: {e}")
    
    def download_file(self, object_name: str, file_path: str):
        """Download a file from MinIO"""
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                file_path,
            )
        except S3Error as e:
            raise Exception(f"Error downloading file: {e}")
    
    def get_object(self, object_name: str) -> bytes:
        """Get file content as bytes"""
        try:
            response = self.client.get_object(
                self.bucket_name,
                object_name,
            )
            return response.read()
        except S3Error as e:
            raise Exception(f"Error getting file: {e}")
    
    def delete_file(self, object_name: str):
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(
                self.bucket_name,
                object_name,
            )
        except S3Error as e:
            raise Exception(f"Error deleting file: {e}")
    
    def list_files(self, prefix: str = "") -> list:
        """List files in the bucket"""
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True,
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise Exception(f"Error listing files: {e}")


# Global MinIO client instance
minio_client = MinIOClient()
