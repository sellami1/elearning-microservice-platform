import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    # App Settings
    ENV: str = Field(default="dev", validation_alias="ANALYTICS_BACKEND_ENV")
    APP_NAME: str = Field(default="Analytics Service", validation_alias="ANALYTICS_BACKEND_APP_NAME")
    LOG_LEVEL: str = Field(default="INFO", validation_alias="ANALYTICS_BACKEND_LOG_LEVEL")
    BACKEND_PORT: int = Field(default=8003, validation_alias="ANALYTICS_BACKEND_PORT")
    
    # Database Settings
    POSTGRES_URL: str = Field(..., validation_alias="ANALYTICS_BACKEND_POSTGRES_URL")
    
    # JWT Settings
    JWT_SECRET_KEY: str = Field(..., validation_alias="ANALYTICS_BACKEND_JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias="ANALYTICS_BACKEND_JWT_ALGORITHM")
    
    # Redis Settings
    REDIS_HOST: str = Field(default="localhost", validation_alias="ANALYTICS_BACKEND_REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, validation_alias="ANALYTICS_BACKEND_REDIS_PORT")
    REDIS_TTL_SECONDS: int = Field(default=60, validation_alias="ANALYTICS_BACKEND_REDIS_TTL_SECONDS")
    
    # Configuration for loading from .env
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore' # Allow other variables in .env without error
    )

import logging

logger = logging.getLogger(__name__)

try:
    settings = Settings()
    # Note: setup_logging() will be called in main.py, so we use print for the very early bootstrap if needed, 
    # but here we can just rely on the settings being initialized.
except Exception as e:
    print(f"❌ CONFIGURATION ERROR: Missing or invalid environment variables.")
    print(f"Details: {e}")
    import sys
    sys.exit(1)
