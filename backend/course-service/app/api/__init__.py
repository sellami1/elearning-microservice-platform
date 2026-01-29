from fastapi import APIRouter

from app.api.routes import courses

router = APIRouter()
router.include_router(courses.router)

__all__ = ["router"]
