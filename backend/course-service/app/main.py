from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .core.config import get_settings
from .database import create_tables, engine
from .api.v1 import courses, lessons, enrollments
from .api.dependencies import get_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("Starting Course Service...")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"MinIO Endpoint: {settings.minio_endpoint}")
    
    # Create tables if they don't exist
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Course Service...")
    engine.dispose()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# API v1 routes
app.include_router(
    courses.router,
    prefix="/api/v1/courses",
    tags=["Courses"]
)

app.include_router(
    lessons.router,
    prefix="/api/v1/lessons",
    tags=["Lessons"]
)

app.include_router(
    enrollments.router,
    prefix="/api/v1/enrollments",
    tags=["Enrollments"]
)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/api/v1/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )