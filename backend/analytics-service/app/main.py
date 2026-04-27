from fastapi import FastAPI, Depends
from sqlalchemy import text
import logging
from .routes import events, metrics
from .database import engine, Base
from .auth import get_current_user
from .models.analytics import SCHEMA_NAME
from fastapi.middleware.cors import CORSMiddleware
from .cors import GranularCORSMiddleware
from .core.logging_config import setup_logging
from .core.config import settings

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# --- DATABASE INITIALIZATION ---
with engine.connect() as connection:
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
    connection.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservice for tracking course views and enrollments",
    version="1.0.0"
)

logger.info("Analytics service boot complete (env=%s, port=%s)", settings.ENV, settings.BACKEND_PORT)

# --- CORS MIDDLEWARES ---
app.add_middleware(GranularCORSMiddleware)

app.include_router(events.router, prefix="/api/v1/analytics")
app.include_router(metrics.router, prefix="/api/v1/analytics")

@app.get("/api/v1/analytics")
@app.get("/api/v1/analytics/")
async def analytics_root():
    return {
        "service": "analytics-service",
        "version": "1.0.0",
        "endpoints": ["/events/*", "/metrics/*", "/health"]
    }

@app.get("/health")
def health_check():
    """Service health probe for Docker/K8s"""
    return {"status": "healthy", "service": "analytics-service"}

@app.get("/")
def read_root(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Welcome to the Analytics Service",
        "decoded_token": current_user
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
    )
