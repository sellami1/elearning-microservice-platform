import redis
import json
from typing import Any, Optional
from .config import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_TTL = settings.REDIS_TTL_SECONDS

import logging

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=1
    )
    # Test connection
    redis_client.ping()
    logger.info(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}. Caching will be disabled.")
    redis_client = None

def get_cache(key: str) -> Optional[Any]:
    """Get data from Redis cache."""
    if redis_client is None:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"Redis get error for key {key}: {e}")
        return None

def set_cache(key: str, value: Any, ttl: int = REDIS_TTL):
    """Set data in Redis cache with TTL."""
    if redis_client is None:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"Redis set error for key {key}: {e}")

def delete_cache(key: str):
    """Delete data from Redis cache."""
    if redis_client is None:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.error(f"Redis delete error for key {key}: {e}")
