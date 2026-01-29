"""Application factory"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import router as api_router
from app.db.init import init_db, check_db_connection, init_minio, check_minio_connection

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize databases on startup"""
    logger.info("Initializing databases and storage...")
    
    # Initialize PostgreSQL
    if check_db_connection():
        try:
            init_db()
            logger.info("PostgreSQL initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
    else:
        logger.warning("Could not connect to PostgreSQL")
    
    # Initialize MinIO
    if check_minio_connection():
        try:
            init_minio()
            logger.info("MinIO initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {e}")
    else:
        logger.warning("Could not connect to MinIO")


@app.get("/", tags=["root"])
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to E-Learning Platform API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    db_ok = check_db_connection()
    minio_ok = check_minio_connection()
    return {
        "status": "healthy" if (db_ok and minio_ok) else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "storage": "connected" if minio_ok else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
