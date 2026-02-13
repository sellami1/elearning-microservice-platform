from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache  # Add this import

class Settings(BaseSettings):
    # App
    app_name: str = Field(default="Course Service", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    
    # Database
    database_url: str = Field(..., validation_alias="POSTGRES_URL")
    
    # JWT
    jwt_secret: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # MinIO
    minio_endpoint: str = Field(..., validation_alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., validation_alias="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="courses-media", validation_alias="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=False, validation_alias="MINIO_SECURE")
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = "../../.env"
        case_sensitive = False  # This allows case-insensitive matching
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()