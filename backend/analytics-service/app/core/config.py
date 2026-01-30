import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = Field(default="Analytics Service")
    LOG_LEVEL: str = Field(default="INFO")
    
    # Database Settings
    POSTGRES_URL: str
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL_SECONDS: int = 60
    
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
