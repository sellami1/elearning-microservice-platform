"""User microservice client utilities"""
import httpx
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class UserServiceClient:
    """Client for communicating with User microservice"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.USER_SERVICE_URL
        self.timeout = 10.0
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user details from user microservice"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get user {user_id}: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"Error getting user from microservice: {e}")
            return None
    
    async def verify_user_exists(self, user_id: int) -> bool:
        """Verify if user exists in user microservice"""
        user = await self.get_user(user_id)
        return user is not None
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> Optional[list]:
        """Get list of users from user microservice"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"skip": skip, "limit": limit},
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get users: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"Error getting users from microservice: {e}")
            return None


# Global client instance
user_service_client = UserServiceClient()
