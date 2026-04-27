from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache  # Add this import

class Settings(BaseSettings):
    # App
    env: str = Field(default="dev", validation_alias="COURSE_BACKEND_ENV")
    app_name: str = Field(default="Course Service", validation_alias="COURSE_BACKEND_APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="COURSE_BACKEND_APP_VERSION")
    log_level: str = Field(default="INFO", validation_alias="COURSE_BACKEND_LOG_LEVEL")
    debug: bool = Field(default=False, validation_alias="COURSE_BACKEND_DEBUG")
    backend_port: int = Field(default=8001, validation_alias="COURSE_BACKEND_PORT")
    
    # Database
    database_url: str = Field(..., validation_alias="COURSE_BACKEND_POSTGRES_URL")
    
    # JWT
    jwt_secret: str = Field(..., validation_alias="COURSE_BACKEND_JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="COURSE_BACKEND_JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="COURSE_BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # MinIO
    minio_endpoint: str = Field(..., validation_alias="COURSE_BACKEND_MINIO_ENDPOINT")
    minio_public_url: str = Field(default="", validation_alias="COURSE_BACKEND_MINIO_PUBLIC_URL")
    minio_access_key: str = Field(..., validation_alias="COURSE_BACKEND_MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., validation_alias="COURSE_BACKEND_MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="courses-media", validation_alias="COURSE_BACKEND_MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=False, validation_alias="COURSE_BACKEND_MINIO_SECURE")

    # Analytics
    analytics_service_url: str = Field(default="http://localhost:8003", validation_alias="COURSE_BACKEND_ANALYTICS_URL")
    analytics_request_timeout_seconds: float = Field(default=2.0, validation_alias="COURSE_BACKEND_ANALYTICS_REQUEST_TIMEOUT_SECONDS")
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = "../../.env"
        case_sensitive = False  # This allows case-insensitive matching
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()