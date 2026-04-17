import logging
import sys
from .config import settings


def _is_dev_env(env: str) -> bool:
    return env.lower() in {"dev", "development"}


def setup_logging():
    """Configure centralized logging for the application."""
    is_dev = _is_dev_env(settings.ENV)
    default_level = "DEBUG" if is_dev else "INFO"
    configured_level = settings.LOG_LEVEL.upper() if settings.LOG_LEVEL else default_level
    log_level = getattr(logging, configured_level, logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)s | analytics-service | %(name)s | %(message)s"
        if is_dev
        else "%(asctime)s | %(levelname)s | %(message)s"
    )
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # In dev we keep access logs visible, in non-dev we reduce noise.
    noisy_level = logging.INFO if is_dev else logging.WARNING
    logging.getLogger("uvicorn.access").setLevel(noisy_level)
    logging.getLogger("sqlalchemy.engine").setLevel(noisy_level)
    
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized",
        extra={
            "env": settings.ENV,
            "log_level": configured_level,
        },
    )
